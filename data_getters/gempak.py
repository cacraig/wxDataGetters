import glob
import os
from subprocess import call
import time

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

          run = fileList[0]
          run = run[0:10]
          dirf = file.split('/')[0]
          script = file.split('/')[1]
          # Customized Gempak scripts for High resolution data in scripts/gempak/hres
          cmd = "tcsh "+ dirf + "/hres/" + script + " " + key + " " + self.constants.modelTimes[key] + " " + run + " " + self.constants.dataDirEnv
          self.runCmd(cmd)
          print cmd
          continue
        # If it is RUC model, and divisible by 3... render extended hour range.
        #if key == "ruc":
        #  value = http['file'].split('_')[0]
        #  if int(value[-2]) % 3 == 0:
        #    self.constants.modelTimes[key] = '00,01,02,03,04,05,06,07,08,09,10,11,12'

        # Non High-Res scripts
        cmd = "tcsh "+ file + " " + key + " " + self.constants.modelTimes[key] + " " + http['file'] + " " + self.constants.dataDirEnv
        #print cmd
        self.runCmd(cmd)
    return

  def runCmd(self, cmd):
    return call(cmd, shell=True)