import urllib2
from constants import Constants
import os
from subprocess import call, STDOUT
from timeout import timeout
import errno
import psycopg2
import redis
import concurrent.futures


# TODO: Speed up download, and require less RAM. 
#         -> http://stackoverflow.com/questions/1517616/stream-large-binary-files-with-urllib2-to-file
# Class for downloading data, and cleaning data directories.
class GemData:

  def __init__(self, models=None, debug=False):
    self.constants = Constants(models)
    print "Creating Connection to DB & Redis..."
    self.conn = psycopg2.connect(self.constants.dbConnStr)
    self.cursor = self.conn.cursor()
    self.dbRunTimes = self.getCurrentRuns()
    self.redisConn = redis.Redis(self.constants.redisHost)
    self.updated = True
    self.DEBUG = debug
    self.complete = False
    self.updatingDir = "/updating"

    # If DEBUG is True, clear all model times so they aren't skipped.
    if self.DEBUG:
      for model,time in self.dbRunTimes.items():
        self.dbRunTimes[model] = ""

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
        del self.constants.runTimes[key]
        print "Skipping: " + key + "... Model not updated."
        continue

      if(self.DEBUG == False):
        if key in self.dbRunTimes:
          if self.constants.runTimes[key] != self.dbRunTimes[key]:
            print "Resetting Hour Keys for Mode ->" + key
            self.resetHourKeys(key)
          lastCompletedRun = self.redisConn.get(key + "-complete")
          if self.constants.runTimes[key] == lastCompletedRun:
            del self.constants.runTimes[key]
            print "Skipping: " + key + "... Model not updated."
            continue

      if 'files' in http:
        # download all files in http['files'].
        print "PROCESSING MANY"
        files = http['files']

        savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/'

        # Get all data. Spawn multiple threads.
        self.getDataThreaded(files, key)

        # for file,url in files.items():
        #   savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/'
        #   print "downloading " + savePath  + file
        #   self.saveFile(savePath, url, file, key)
        #   self.processGrib2(key, savePath, file)

        #   # Append forecast hour to times to be processed... No prefixes also.
        #   fHour = self.constants.getForecastHour(key, file, True)

        #   if(self.DEBUG == False):
        #     if self.redisConn.get(key + '-' + fHour) != "1":
        #       self.constants.modelTimes[key].append(fHour)
        #   else:
        #     self.constants.modelTimes[key].append(fHour)

        # After data has been sucessfully retrieved, and no errors thrown update model run time.
        if(self.DEBUG == False):
          self.updateModelTimes(key, self.constants.runTimes[key])
          print "SETTING COMPLETION FLAG  " + key + "-complete" 
          self.setRunCompletionFlag(key)

        #self.updated = True
      # else:
      #   savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/'
      #   self.constants.setDefaultHours()
        
      #   try:
      #     print "Saving: " + http['url'] + " to " + savePath + http['file']
      #     gemFile = urllib2.urlopen(http['url']).read()
      #     #fp = open(savePath + self.constants.runTimes[key] + ".gem", 'w')
      #     fp = open(savePath + key + ".gem", 'w') # save as model.gem
      #     fp.write(gemFile)
      #     fp.close()
      #     # After data has been sucessfully retrieved, and no errors thrown update model run time.
      #     self.updateModelTimes(key, self.constants.runTimes[key])
      #     self.updated = True
      #   except Exception, e:
      #     print "Could not get Model *.gem " + http['file'] + " with url: " + http['url']
      #     print " with exception %s" % e
      #     pass

      # END FOR Set model's redis key to not processing.
      # if(self.DEBUG == False):
      #   self.redisConn.set(key, "0")

    # Jump back to present WD
    os.chdir(currentDir)
    self.conn.close()
    return

  def isUpdated(self):
    return self.updated

  def isComplete(self):
    return self.complete

  def resetHourKeys(self, model):
    hourKeys = self.constants.getDefaultHoursByModel(model)
    for hour in hourKeys:
      self.redisConn.set(model + '-' + hour, "0")
    return

  def setRunCompletionFlag(self, model):

    f = open('/home/vagrant/logs/output.log','w')
    f.write('Trying: ' + model + '-complete')
    for item in self.constants.modelTimes[model]:
      f.write("Hour: " + item)

    if self.constants.lastForecastHour[model] in self.constants.modelTimes[model]:
      self.redisConn.set(model + '-complete', self.constants.runTimes[model])
      self.complete = True
      # Set updating directory to empty string.
      # When model is complete, copy images to completed directory
      self.updatingDir = ""
      self.setUpdatingFlag(model, 0)
      f.write("COMPLETION! SETTING KEY: " + model + "-complete to " + self.constants.runTimes[model])

    f.close() # you can omit in most cases as the destructor will call if
    return
  
  # Convert grib2 files into gem files.
  def processGrib2(self, model, savePath, fileName):
    
    inFile  = savePath + fileName
    outFile = self.getGemFileName(model, savePath, fileName)
    cmd = "dcgrib2 " + outFile + ' < ' + inFile

    print cmd
    
    # convert our *.grib2 file into a *.gem file.
    if os.path.isfile(outFile):
      print "Not decoding, skipping"
      return
    self.runCmd(cmd)
    return

  def getGemFileName(self, model, savePath, fileName):
      forecastHour = self.constants.getForecastHour(model,fileName)

      currentRun = self.constants.runTimes[model]

      outFile = model + '/' + currentRun + forecastHour + '.gem'

      return outFile

  # Saves file. Skips saving if file already exists.
  # timeout after 15 mins.
  @timeout(900, os.strerror(errno.ETIMEDOUT))
  def saveFile(self, savePath, url, fileName, model = None):

    grib2File = savePath + fileName
    
    # If model is specified, check for a decoded .gem file.
    if model is not None:
      gemFile = self.getGemFileName(model, savePath, fileName)
      if os.path.isfile(gemFile):
        print "Decoded GEM file:" + gemFile + " already exists...skipping..."
        return


    # If file exists, don't download again!
    # if os.path.isfile(grib2File):
    #   print "File already downloaded. Skipping..."
    #   return

    # File does not already exist, download it.
    gemFile = urllib2.urlopen(url).read()
    fp = open(grib2File, 'w')
    fp.write(gemFile)
    fp.close()
    return

  def saveFilesThread(self, arg):
    # (model, savePath, fileName, url)
    model = arg[0]
    savePath = arg[1]
    fileName = arg[2]
    url = arg[3]

    print "downloading " + savePath  + fileName

    grib2File = savePath + fileName

    if model is not None:
      gemFile = self.getGemFileName(model, savePath, fileName)
      if os.path.isfile(gemFile):
        print "Decoded GEM file:" + gemFile + " already exists...skipping..."
        return ''


    # If file exists, don't download again!
    # if os.path.isfile(grib2File):
    #   print "File already downloaded. Skipping..."
    #   return

    # File does not already exist, download it.
    gemFile = urllib2.urlopen(url).read()
    fp = open(grib2File, 'w')
    fp.write(gemFile)
    fp.close()

    self.processGrib2(model, savePath, fileName)

    return ''

  def getDataThreaded(self, files, key):
    savePath = self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/'
    args = []
    for file,url in files.items():
      grib2File = savePath + file
      arg = (key, savePath, file, url)
      # Append forecast hour to times to be processed... No prefixes also.
      fHour = self.constants.getForecastHour(key, file, True)

      if(self.DEBUG == False):
        if self.redisConn.get(key + '-' + fHour) != "1":
          self.constants.modelTimes[key].append(fHour)
      else:
        self.constants.modelTimes[key].append(fHour)
      args.append(arg)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
      result = ''.join(executor.map(self.saveFilesThread, args))
    print "Done with Threads."

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
    # Remove and move over only updated data.
    for model,runTime in self.constants.runTimes.items():
      assetsDir = self.constants.webDir + "/src/assets/" + model
      cleanWebDirCmd = "sudo rm -r " + assetsDir + "/*/"
      self.runCmd(cleanWebDirCmd)
      self.runCmd("sudo mv " + os.getcwd() +"/scripts/data/" + model + "/* " + assetsDir)

  def rebuild(self, env):
    os.chdir(self.constants.webDir)
    self.runCmd("sudo rm -rf dist/src/assets")
    self.runCmd("sudo grunt build-" + env)
    self.runCmd("git add src/assets")

  def transferFilesToProd(self, model = None):

    if model is None:
      self.runCmd("rsync -vPr " + self.constants.imageDir + " " + self.constants.imageHost + ":" + self.constants.prodBaseDir)
    else:
      self.runCmd("rsync -vPr " + os.getcwd() +"/scripts/data/" + model + " " + self.constants.imageHost + ":" + self.constants.imageDir + self.updatingDir)

  def runCmd(self, cmd):
    FNULL = open(os.devnull, 'w')
    print "Currently executing..."
    print cmd
    return call(cmd, shell=True, stdout=FNULL, stderr=STDOUT)

  def getCurrentRuns(self):
    print "Getting Current Runs from DB..."
    self.cursor.execute("SELECT name,current_run from model")
    rows = self.cursor.fetchall()
    print rows
    dbRunTimes = {}
    for row in rows:
      dbRunTimes[row[0]] = row[1]
    print dbRunTimes
    return dbRunTimes

  # Insert/update our current model run times.
  def updateModelTimes(self, model, time):
    # If the current run = run being processed...skip
    if self.dbRunTimes[model] == time:
      return

    try:
      # self.cursor.execute("SELECT * from model where name='" + model + "'")
      self.cursor.execute("UPDATE model SET current_run ='" + time + "', previous_run= '" + self.dbRunTimes[model] + "', updating=1 WHERE name='" + model+"'")
    except Exception, e:
      print e

    self.conn.commit()
    return

  def setUpdatingFlag(self, model, boolValue):

    try:
      # self.cursor.execute("SELECT * from model where name='" + model + "'")
      self.cursor.execute("UPDATE model SET updating =" + str(boolValue) + " WHERE name='" + model+"'")
    except Exception, e:
      print e

    self.conn.commit()
    return