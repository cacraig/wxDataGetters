import glob
import os
from subprocess import call

# This class contains execution logic for gempak scripts.

class Gempak:

  def __init__(self, dataGetter):
    self.constants = dataGetter.constants 
    return

  def runGempakScripts(self):
    os.chdir("scripts")
    for file in glob.glob("gempak/*.sh"):
      for key,http in self.constants.modelGems.items():
        if 'files' in http:
          files = http['files']
          fileList = []
          for mfile,url in files.items():
            fileList.append(mfile)

          dirf = file.split('/')[0]
          script = file.split('/')[1]
          # Customized Gempak scripts for High resolution data in scripts/gempak/hres
          cmd = "tcsh "+ dirf + "/hres/" + script + " " + key + " " + self.constants.modelTimes[key] + " " + self.constants.runTimes[key] + " " + self.constants.dataDirEnv
          self.runCmd(cmd)
          print cmd
          continue

        # Non High-Res scripts
        cmd = "tcsh "+ file + " " + key + " " + self.constants.modelTimes[key] + " " + http['file'] + " " + self.constants.dataDirEnv
        print cmd
        self.runCmd(cmd)
    return

  def runCmd(self, cmd):
    return call(cmd, shell=True)