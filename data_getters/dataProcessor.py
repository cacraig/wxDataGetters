import urllib2
from constants import Constants
import os
from subprocess import call, STDOUT
from timeout import timeout
import errno
import psycopg2
import redis
import concurrent.futures
import socket, threading
# TODO: Speed up download, and require less RAM. 
#         -> http://stackoverflow.com/questions/1517616/stream-large-binary-files-with-urllib2-to-file
# Class for downloading data, and cleaning data directories.
class DataProcessor:

  def __init__(self, modelClass, debug=False):
    self.modelClass = modelClass
    self.constants = Constants()
    print "Creating Connection to DB & Redis..."
    self.conn = psycopg2.connect(self.constants.dbConnStr)
    self.cursor = self.conn.cursor()
    self.redisConn = redis.Redis(self.constants.redisHost)
    self.dbRunTimes = {}
    self.updated = True
    self.DEBUG = debug
    self.complete = False
    self.updatingDir = "/updating"
    return

  '''''
  getData loops through our model download paths, and saves them to our specified save paths in self.modelClass.
  '''''
  def getData(self, modelLinks):
    currentDir = os.getcwd()
    os.chdir(self.constants.dataDirEnv)
    model = self.modelClass.getName()
    http  = modelLinks[model]

    # If it is empty for any reason, skip!
    if not http:
      del self.modelClass.runTime
      print "Skipping: " + model + "... Model not updated."
      # Jump back to present WD
      os.chdir(currentDir)
      if self.DEBUG == True:
        self.closeConnection()
      return

    # If DEBUG is True, clear all model times so they aren't skipped.
    if self.DEBUG:
      for model,time in self.dbRunTimes.items():
        self.dbRunTimes[model] = ""

    self.dbRunTimes = self.getCurrentRuns(model)

    if(self.DEBUG == False):
      if model in self.dbRunTimes:
        if self.modelClass.runTime != self.dbRunTimes[model]:
          print "Resetting Hour keys for Mode ->" + model
          self.resetHourKeys(key)
        lastCompletedRun = self.redisConn.get(model + "-complete")
        if self.modelClass.runTime == lastCompletedRun:
          del self.modelClass.runTime
          print "Skipping: " + model + "... Model not updated."
          # Jump back to present WD
          os.chdir(currentDir)
          if self.DEBUG == True:
            self.closeConnection()
          return

    if 'files' in http:
      if not self.modelClass.isNCEPSource:
        # Download files.
        print http
        print "PROCESSING MANY"
        files = http['files']

        savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + model + '/'
        self.getDataNoThreads(files, model)
        # Combine if nesc.
      else:
        # download all files in http['files'].
        print "PROCESSING MANY"
        files = http['files']

        savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + model + '/'

        # Get all data. Spawn multiple threads.
        self.getDataThreaded(files, model)

      # After data has been sucessfully retrieved, and no errors thrown update model run time.
      if(self.DEBUG == False):
        self.updateModelTimes(model, self.modelClass.runTime)
        print "SETTING COMPLETION FLAG  " + model + "-complete" 
        self.setRunCompletionFlag(model)

    # Jump back to present WD
    os.chdir(currentDir)
    if self.DEBUG == True:
      self.closeConnection()
    return

  def isUpdated(self):
    return self.updated

  def isComplete(self):
    return self.complete

  def closeConnection(self):
    return self.conn.close()

  def resetHourKeys(self, model):
    hourKeys = self.modelClass.getDefaultHoursByModel(model)
    for hour in hourKeys:
      self.redisConn.set(model + '-' + hour, "0")
    return

  def setRunCompletionFlag(self, model):

    f = open(self.constants.execLog, 'w')
    f.write('Trying: ' + model + '-complete')
    for item in self.modelClass.modelTimes:
      f.write("Hour: " + item)

    if self.modelClass.getLastForecastHour() in self.modelClass.modelTimes:
      self.redisConn.set(model + '-complete', self.modelClass.runTime)
      self.complete = True
      # Set updating directory to empty string.
      # When model is complete, copy images to completed directory
      self.updatingDir = ""
      f.write("COMPLETION! SETTING KEY: " + model + "-complete to " + self.modelClass.runTime)

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
      forecastHour = self.modelClass.getForecastHour(fileName)

      currentRun = self.modelClass.runTime

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

  # Saves file. Skips saving if file already exists.
  # timeout after 15 mins.
  @timeout(120, os.strerror(errno.ETIMEDOUT))
  def saveFilesAndCat(self, savePath, urls, fileName, model = None):

    grib2File = savePath + fileName

    # If model is specified, check for a decoded .gem file.
    # if model is not None:
    #   gemFile = self.getGemFileName(model, savePath, fileName)
    #   if os.path.isfile(gemFile):
    #     print "Decoded GEM file:" + gemFile + " already exists...skipping..."
    #     return


    # If file exists, don't download again!
    # if os.path.isfile(grib2File):
    #   print "File already downloaded. Skipping..."
    #   return
    if isinstance(urls, list):
      # File does not already exist, download it.
      for url in urls:
        print "Downloading: " + url + " to " + grib2File
        gemFile = urllib2.urlopen(url).read()
        fp = open(grib2File, 'a')
        fp.write(gemFile)
        fp.close()
        print "DONE DOWNLOADING"
    else:
      print "Downloading: " + url + " to " + grib2File
      gemFile = urllib2.urlopen(url).read()
      fp = open(grib2File, 'a')
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
    # try:
    maxSocketTime = 300 # Max time a download read() can take.
    maxUrlOpenTime = 15 # Max time to open a URL
    gemFile = urllib2.urlopen(url)
    success,gemFile = self.timeoutHttpRead(gemFile, maxSocketTime)

    # If the blocking urllib2.read() took longer than maxSocketTime, Abandon Ship!
    # Return False, otherwise download file.
    if success and gemFile is not None:
      fp = open(grib2File, 'w')
      fp.write(gemFile)
      fp.close()
    else:
      print "Socket timed out! Time exceeded "
      f = open(self.modelClass.errorLog,'w')
      f.write("\n A socket Timed out in GemData.saveFilesThread() . We must exit this program execution, and attempt again.")
      f.write("\n URL: " + url)
      f.write("\n MODEL: " + model)
      f.write("\n SAVE_PATH: " + savePath)
      f.close()
      # Exit call. Give up, get the hell out!
      return False

    # except socket.error:
    #   print "There was a timeout"

    self.processGrib2(model, savePath, fileName)

    return True

  def timeoutHttpRead(self, response, timeout = 60):
    def murha(resp):
      try:
        os.close(resp.fileno())
        resp.close()
      except Exception, e:
        print e
        return (False, None)

    # set a timer to yank the carpet underneath the blocking read() by closing the os file descriptor
    t = threading.Timer(timeout, murha, (response,))
    try:
      t.start()
      body = response.read()
      t.cancel()
    except socket.error as se:
      if se.errno == errno.EBADF: # murha happened
        return (False, None)
      raise
    return (True, body)

  def getDataThreaded(self, files, model):
    savePath = self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + model + '/'
    args = []
    for file,url in files.items():
      grib2File = savePath + file
      arg = (model, savePath, file, url)
      # Append forecast hour to times to be processed... No prefixes also.
      fHour = self.modelClass.getForecastHour(file, True)

      if(self.DEBUG == False):
        if self.redisConn.get(model + '-' + fHour) != "1":
          self.modelClass.modelTimes.append(fHour)
      else:
        self.modelClass.modelTimes.append(fHour)
      args.append(arg)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
      for res in executor.map(self.saveFilesThread, args):
        if res == False:
          print "Exiting... See error.log for details."
          exit(1)
    print "Done with Threads."

    return

  def getDataNoThreads(self, files, model):
    savePath = self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + model + '/'
    args = []
    for file,urls in files.items():
      grib2File = savePath + file
      # Append forecast hour to times to be processed... No prefixes also.
      fHour = self.modelClass.getForecastHour(file, True)
      self.saveFilesAndCat(savePath, urls, file, model)
      if(self.DEBUG == False):
        if self.redisConn.get(model + '-' + fHour) != "1":
          self.modelClass.modelTimes.append(fHour)
      else:
        self.modelClass.modelTimes.append(fHour)
        
      self.processGrib2(model, savePath, file)

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
  Clear saved npy files.
  '''''
  def clearNpyDat(self, model):
    self.runCmd("rm " + self.constants.NP_TMP_DIR + "/" + model + "_*")
    return


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
    model = self.modelClass.getName()
    runTime = self.modelClass.runTime
    # Remove and move over only updated data.
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
      self.runCmd("rsync -a -vPr " + self.constants.imageDir + " " + self.constants.imageHost + ":" + self.constants.prodBaseDir)
    else:
      self.runCmd("rsync -a -vPr " + os.getcwd() +"/scripts/data/" + model + " " + self.constants.imageHost + ":" + self.constants.imageDir + self.updatingDir)

  def runCmd(self, cmd):
    FNULL = open(os.devnull, 'w')
    print "Currently executing..."
    print cmd
    return call(cmd, shell=True, stdout=FNULL, stderr=STDOUT)

  def getCurrentRuns(self, model):
    '''''
    Get latest run time from database for model.
    @return String
    '''''
    print "Getting Current Runs from DB..."
    selectQuery = "select model.name as name, run_time from model_runtime JOIN model ON (model.id = model_runtime.model_id) WHERE model.name='" + \
                     model + "' ORDER BY run_time DESC LIMIT 1"
    self.cursor.execute(selectQuery)
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
      insertStr = "INSERT INTO model_runtime (model_id, run_time) " + \
                   "VALUES ((SELECT id FROM model WHERE model.name ='" + model +"'),'" + time + "')"

      self.cursor.execute(insertStr)
      self.cursor.execute("UPDATE model SET updating=1 WHERE name='" + model+"'")
    except Exception, e:
      print e

    self.conn.commit()
    return

  def setUpdatingFlag(self, model, boolValue):

    try:
      #updateStr = "UPDATE model_runtime SET updating=" + str(boolValue) + \
      #            " WHERE model_id = (SELECT id FROM model WHERE model.name = '" + model + "') AND run_time='" + self.dbRunTimes[model] + "'"
      updateStr = "UPDATE model SET updating =" + str(boolValue) + " WHERE name='" + model+"'"
      self.cursor.execute(updateStr)
      #self.cursor.execute("UPDATE model SET updating =" + str(boolValue) + " WHERE name='" + model+"'")
    except Exception, e:
      print e

    self.conn.commit()
    return