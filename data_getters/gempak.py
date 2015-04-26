import glob
import os
from subprocess import call, STDOUT
import concurrent.futures
from grib2Plot import Grib2Plot

# This class contains execution logic for gempak scripts.

class Gempak:

  def __init__(self, dataGetter):
    self.modelClass =  dataGetter.modelClass
    self.constants  = dataGetter.constants
    self.redisConn  = dataGetter.redisConn
    self.DEBUG = dataGetter.DEBUG
    self.grib2Plotter = Grib2Plot(self.constants)
    return

  def runGempakScripts(self, modelLinks):
    prevWd = os.getcwd()
    os.chdir("scripts")

    model = self.modelClass.getName()
    http  = modelLinks[model]
    
    if 'files' in http and model != "gfs" and model != "nam":
      for file in glob.glob("gempak/hres/*.sh"):
        print "Executing HiRes gempak scripts."
        # Customized Gempak scripts for High resolution data in scripts/gempak/hres
        cmd = "tcsh "+ file + " " + model + " " + ",".join(self.modelClass.modelTimes) + " " + self.modelClass.runTime + " " + self.constants.dataDirEnv
        self.runCmd(cmd)
        print cmd
    else:
      print "Executing Non-HiRes gempak scripts."
      for file in glob.glob("gempak/*.sh"):
        # Non High-Res scripts
        cmd = "tcsh "+ file + " " + model + " " + ",".join(self.modelClass.modelTimes) + " " + self.modelClass.runTime + " " + self.constants.dataDirEnv
        print cmd
        self.runCmd(cmd)
    # Flag all forecast hours as processed.
    if self.DEBUG == False:
      # Set to not processing status.
      #self.redisConn.set(model, "0")
      for fHour in self.modelClass.modelTimes:
        # Set all forecast hours processed.
        self.redisConn.set(model + '-' + fHour, "1")

    os.chdir(prevWd)
    return

  def doThreadedGempakScripts(self, modelLinks):
    cmdList = []
    prevWd = os.getcwd()
    os.chdir("scripts")

    model = self.modelClass.getName()
    http  = modelLinks[model]

    if 'files' in http and model != "gfs" and model != "nam" and model != "ecmwf":
      # Do matplot stuff.
      if len(self.modelClass.modelTimes) >0:
        self.modelClass.modelTimes.sort()
        # Do TempF plotting in Matplotlib...
        self.grib2Plotter.plot2mTemp(model, self.modelClass.modelTimes, self.modelClass.runTime, self.constants.dataDirEnv)
      
      # Do gddiag. (Mutable, cannot thread this.)
      for file in glob.glob("gempak/grids/*.sh"):
        cmd = "tcsh "+ file + " " + model + " " + ",".join(self.modelClass.modelTimes) + " " + self.modelClass.runTime + " " + self.constants.dataDirEnv
        print "Doing: " + file + " =>  " + cmd
        self.runCmd(cmd)

      # Do gempak stuff.
      for file in glob.glob("gempak/hres/*.sh"):
        print "Executing HiRes gempak scripts."
        # Customized Gempak scripts for High resolution data in scripts/gempak/hres
        cmd = "tcsh "+ file + " " + model + " " + ",".join(self.modelClass.modelTimes) + " " + self.modelClass.runTime + " " + self.constants.dataDirEnv
        cmdList.append(cmd)
        #self.runCmd(cmd)
        print cmd
    else:
      print "Executing Non-HiRes gempak scripts."
      # Do Matplot stuff!
      previousTime = '000'
      if len(self.modelClass.modelTimes) >0:
        self.modelClass.modelTimes.sort()
        previousTime = self.modelClass.getPreviousTime(model, self.modelClass.modelTimes[0])
        if model != "ecmwf":
          # Do TempF plot
          self.grib2Plotter.plot2mTemp(model,self.modelClass.modelTimes, self.modelClass.runTime, self.constants.dataDirEnv)
          # Do Snowfall plotting in Matplotlib...
          # Only plot snowfall if the run has completed.
          if self.modelClass.getLastForecastHour() in self.modelClass.modelTimes:
            self.grib2Plotter.plotSnowFall(model,self.modelClass.getDefaultHours(), self.modelClass.runTime, self.constants.dataDirEnv, self.modelClass.getDefaultHours()[0])
        # Do gddiag. (Mutable, cannot thread this.)
        # for file in glob.glob("gempak/grids/*.sh"):
        #   cmd = "tcsh "+ file + " " + key + " " + ",".join(self.constants.modelTimes[key]) + " " + self.constants.runTimes[key] + " " + self.constants.dataDirEnv + " " + previousTime
        #   print "Doing: " + file + " =>  " + cmd
        #   self.runCmd(cmd)

      # Do gempak stuff.
      for file in glob.glob("gempak/*.sh"):
        # Non High-Res scripts
        cmd = "tcsh "+ file + " " + model + " " + ",".join(self.modelClass.modelTimes) + " " + self.modelClass.runTime + " " + self.constants.dataDirEnv + " " + previousTime
        # print cmd
        cmdList.append(cmd)
        #self.runCmd(cmd)

    if len(cmdList) > 0:
      with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        result = ''.join(executor.map(self.runCmd, cmdList))

    print "Done with Threads."

    # Flag all forecast hours as processed.
    if self.DEBUG == False:
      # Set to not processing status.
      #self.redisConn.set(key, "0")
      for fHour in self.modelClass.modelTimes:
        # Set all forecast hours processed.
        self.redisConn.set(model + '-' + fHour, "1")

    os.chdir(prevWd)
    return

  def runCmd(self, cmd):
    FNULL = open(os.devnull, 'w')
    print "Currently executing..."
    print cmd
    call(cmd, shell=True, stdout=FNULL, stderr=STDOUT)
    return ''