import urllib2
from constants import Constants
import os
from subprocess import call

# Class for downloading data, and cleaning data directories.
class GemData:

  def __init__(self):
    self.constants = Constants()
    return

  '''''
  getData loops through our model download paths, and saves them to our specified save paths in self.constants.
  '''''
  def getData(self):

    currentDir = os.getcwd()
    os.chdir(self.constants.dataDirEnv)

    for key,http in self.constants.modelGems.items():

      # If it is empty for any reason, skip!
      if not http:
        print "Skipping: " + key + "..."
        continue

      if 'files' in http:
        # download all files in http['files'].
        print "PROCESSING MANY"
        files = http['files']

        for file,url in files.items():
          savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/'
          print "downloading " + savePath  + file
          gemFile = urllib2.urlopen(url).read()
          fp = open(savePath + file, 'w')
          fp.write(gemFile)
          fp.close()
          self.processGrib2(key,savePath,file)

      else:
        savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/' 

        try:
          print "Saving: " + http['url'] + " to " + savePath + http['file']
          gemFile = urllib2.urlopen(http['url']).read()
          fp = open(savePath + http['file'], 'w')
          fp.write(gemFile)
          fp.close()

        except Exception, e:
          print "Could not get Model *.gem " + http['file'] + " with url: " + http['url']
          print " with exception %s" % e
          pass
          
    # Jump back to present WD
    os.chdir(currentDir)
    return

  def processGrib2(self, model, savePath, fileName):
    extension = fileName.split('.')[-1]
    if extension != 'grib2':
      return

    # for model.t06z.blahblah.hiresf07.blah -> forecastHour = "07"
    forecastHour = fileName.split('.')[3][6:8]
    currentRun = self.constants.runTimes[model]
    inFile  = savePath + fileName
    outFile = model + '/' + currentRun + "f0" + forecastHour + '_' + model + '.gem'
    cmd = "dcgrib2 " + outFile + ' < ' + inFile

    print cmd
    
    # convert our *.grib2 file into a *.gem file.
    self.runCmd(cmd)
    return

  '''''
  scrubTreeData takes a directory to scrub of all files. It will leave directories alone.

  @param String dir - A directory to scrub of files.
  '''''
  def scrubTreeData(self, directory):
    if os.path.isdir(directory):
      files = os.listdir(directory)
      for f in files:
        fileOrDirPath = os.path.join(directory,f)
        if os.path.isdir(fileOrDirPath):
          self.scrubTreeData(fileOrDirPath)
        else:
          self.rmFile(fileOrDirPath)
    else:
      self.rmFile(directory)

  '''''
  rmFile just removes a file, and throws an exception. Shut up.

  @param String filePath - File to remove.
  '''''
  def rmFile(self, filePath):
    try:
      print "Removing" + filePath
      os.unlink(filePath)
    except Exception, e:
      print e
    return

  def mvAssets(self):
    assetsDir = self.constants.webDir + "/src/assets/"
    cleanWebDirCmd = "sudo rm -r " + assetsDir + "*/"
    self.runCmd(cleanWebDirCmd)
    self.runCmd("sudo mv " + os.getcwd() +"/scripts/data/* " + assetsDir)

  def rebuild(self, env):
    os.chdir(self.constants.webDir)
    self.runCmd("sudo grunt build-" + env)

  def runCmd(self, cmd):
    return call(cmd, shell=True)


    