import glob
import os
from subprocess import call

# This class contains execution logic for gempak scripts.

class Gempak:

  def __init__(self, dataGetter):
    self.constants = dataGetter.constants 
    return

  def runGempakScripts(self):
    prevWd = os.getcwd()
    os.chdir("scripts")
    for key,http in self.constants.modelGems.items():
      if key in self.constants.runTimes:
        if 'files' in http and key != "gfs" and key != "nam":
          for file in glob.glob("gempak/hres/*.sh"):
            print "Executing HiRes gempak scripts."
            # Customized Gempak scripts for High resolution data in scripts/gempak/hres
            cmd = "tcsh "+ file + " " + key + " " + ",".join(self.constants.modelTimes[key]) + " " + self.constants.runTimes[key] + " " + self.constants.dataDirEnv
            self.runCmd(cmd)
            print cmd
        else:
          print "Executing Non-HiRes gempak scripts."
          for file in glob.glob("gempak/*.sh"):
            # Non High-Res scripts
            cmd = "tcsh "+ file + " " + key + " " + ",".join(self.constants.modelTimes[key]) + " " + self.constants.runTimes[key] + " " + self.constants.dataDirEnv
            print cmd
            self.runCmd(cmd)
    os.chdir(prevWd)
    return

  def runCmd(self, cmd):
    return call(cmd, shell=True)