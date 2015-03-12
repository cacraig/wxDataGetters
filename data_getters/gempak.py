import glob
import os
from subprocess import call, STDOUT
import concurrent.futures

# This class contains execution logic for gempak scripts.

class Gempak:

  def __init__(self, dataGetter):
    self.constants = dataGetter.constants
    self.redisConn = dataGetter.redisConn
    self.DEBUG = dataGetter.DEBUG
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
      # Flag all forecast hours as processed.
      if self.DEBUG == False:
        # Set to not processing status.
        self.redisConn.set(key, "0")
        for fHour in self.constants.modelTimes[key]:
          # Set all forecast hours processed.
          self.redisConn.set(key + '-' + fHour, "1")

    os.chdir(prevWd)
    return

  def doThreadedGempakScripts(self):
    cmdList = []
    prevWd = os.getcwd()
    os.chdir("scripts")
    for key,http in self.constants.modelGems.items():
      if key in self.constants.runTimes:
        if 'files' in http and key != "gfs" and key != "nam":
          for file in glob.glob("gempak/hres/*.sh"):
            print "Executing HiRes gempak scripts."
            # Customized Gempak scripts for High resolution data in scripts/gempak/hres
            cmd = "tcsh "+ file + " " + key + " " + ",".join(self.constants.modelTimes[key]) + " " + self.constants.runTimes[key] + " " + self.constants.dataDirEnv
            #cmdList.append(cmd)
            self.runCmd(cmd)
            print cmd
        else:
          print "Executing Non-HiRes gempak scripts."
          #if key == "nam" or key=="gfs":
          if len(self.constants.modelTimes[key]) >0:
            self.constants.modelTimes[key].sort()
            previousTime = self.constants.getPreviousTime(key, self.constants.modelTimes[key][0])

            # Do gddiag. (Mutable, cannot thread this.)
            for file in glob.glob("gempak/grids/*.sh"):
              cmd = "tcsh "+ file + " " + key + " " + ",".join(self.constants.modelTimes[key]) + " " + self.constants.runTimes[key] + " " + self.constants.dataDirEnv + " " + previousTime
              print "Doing: " + file + " =>  " + cmd
              self.runCmd(cmd)

          for file in glob.glob("gempak/*.sh"):
            # Non High-Res scripts
            cmd = "tcsh "+ file + " " + key + " " + ",".join(self.constants.modelTimes[key]) + " " + self.constants.runTimes[key] + " " + self.constants.dataDirEnv + " " + previousTime
            print cmd
            #cmdList.append(cmd)
            self.runCmd(cmd)

      if len(cmdList) > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
          result = ''.join(executor.map(self.runCmd, cmdList))

      print "Done with Threads."

      # Flag all forecast hours as processed.
      if self.DEBUG == False:
        # Set to not processing status.
        self.redisConn.set(key, "0")
        for fHour in self.constants.modelTimes[key]:
          # Set all forecast hours processed.
          self.redisConn.set(key + '-' + fHour, "1")

    os.chdir(prevWd)
    return

  def runCmd(self, cmd):
    FNULL = open(os.devnull, 'w')
    print "Currently executing..."
    print cmd
    call(cmd, shell=True, stdout=FNULL, stderr=STDOUT)
    return ''