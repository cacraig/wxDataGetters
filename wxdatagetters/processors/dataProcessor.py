import urllib2
from objects.constants import Constants
import os
from subprocess import call, STDOUT
from decorators.timeout import timeout
import errno
import psycopg2
import redis
import concurrent.futures
import socket, threading


class DataProcessor:
  '''''
  Downloads all files for modelClass. Converts into *.gem files if nescessary, and handles updating database runtimes (and redis keys).
  @param object modelClass
  @param boolean debug
  '''''
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
  public function getData(modelLinks)

  getData loops through our model download paths, and saves them to our specified save paths in self.modelClass.
  
  @param dictionary modelLinks
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
          self.resetHourKeys(model)
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
        files = http['files']

        savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + model + '/'
        self.getDataNoThreads(files, model)
        # Combine if nesc.
      else:
        # download all files in http['files'].
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

  '''''
  public functon isUpdated()

  Returns true if the model differs from that in the DB, 
  or there are new forecast hours to process for current run.
  @return boolean 
  '''''
  def isUpdated(self):
    return self.updated

  '''''
  public functon isComplete()

  Returns model downloading status. 
  True if the model run is completely downloaded. (Last forecast hour encountered)
  @return boolean 
  '''''
  def isComplete(self):
    return self.complete

  '''''
  public functon closeConnection()

  Closes open DB connection.
  @return boolean 
  '''''
  def closeConnection(self):
    return self.conn.close()

  '''''
  public function resetHourKeys(model)
  Resets all redis keys for a model to 0 (not yet processed).
  
  @param String model
  '''''
  def resetHourKeys(self, model):
    hourKeys = self.modelClass.getDefaultHours()
    for hour in hourKeys:
      self.redisConn.set(model + '-' + hour, "0")
    return

  '''''
  public function setRunCompletionFlag(model)
  Sets redis key model-complete to 1 if the model is completely processed (downloaded).

  @param String model
  @retrun void
  '''''
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
  
  '''''
  public function processGrib2(model, savePath, fileName)

  Turns a *.grib2 file into a *.gem file. (Dependancy: dcgrib2)
  @param String model    - Name of model
  @param String savePath - Save path of all model files.
  @param String fileName - File name of *.gem file.
  @return void
  '''''
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

  '''''
  public function getGemFileName(model, savePath, fileName)

  Gets a *.gem file name in format model/{runTime}{forecastHour}.gem
  @param String model    - Name of model
  @param String savePath - Save path of all model files.
  @param String fileName - File name of *.gem file.
  @return String outFile - *.gem file name to use.
  '''''
  def getGemFileName(self, model, savePath, fileName):
      forecastHour = self.modelClass.getForecastHour(fileName)

      currentRun = self.modelClass.runTime

      outFile = model + '/' + currentRun + forecastHour + '.gem'

      return outFile

  '''''
  public function saveFile(savePath, url, fileName, model = None)

  Saves a file. NON-THREADED. Skips download if file already exists.
  Times out after some time.

  @param String savePath - Path to save file to.
  @param String url      - URL to download file from.
  @param String fileName - Name of file to download.
  @param String model    - Name of model.
  @return void
  '''''
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

  '''''
  public function saveFilesAndCat(savePath, url, fileName, model = None)

  Saves a file. NON-THREADED. Skips download if file already exists.
  Times out after some time.

  @param String savePath - Path to save file to.
  @param String url      - URL to download file from.
  @param String fileName - Name of file to download.
  @param String model    - Name of model.
  @return void
  '''''
  # Saves file. Skips saving if file already exists.
  # timeout after 15 mins.
  @timeout(120, os.strerror(errno.ETIMEDOUT))
  def saveFilesAndCat(self, savePath, urls, fileName, model = None):

    grib2File = savePath + fileName

    # If model is specified, check for a decoded .gem file.
    if model is not None:
      gemFile = self.getGemFileName(model, savePath, fileName)
      if os.path.isfile(gemFile):
        print "Decoded GEM file:" + gemFile + " already exists...skipping..."
        return

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

  '''''
  private function saveFilesThread(arg)
  Thread worker function for Threaded saving of files.

  @param Tuple arg
  @return boolean - True if successful, otherwise False.
  '''''
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

  '''''
  private function timeoutHttpRead(response, timeout=60)

  Time out function for Threads.

  @param object response
  @param int timeout
  @return Tuple
  '''''
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

  '''''
  public function getDataThreaded(files, model)

  Gets data with Threads!
  
  @param dictionary files
  @param String model
  @return void
  '''''
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

  '''''
  public function getDataNoThreads(files, model)

  Gets data WITHOUT Threads!
  
  @param dictionary files
  @param String model
  @return void
  '''''
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
      raise e
    return

  def mvAssets(self):
    model = self.modelClass.getName()
    runTime = self.modelClass.runTime
    # Remove and move over only updated data.
    assetsDir = self.constants.webDir + "/src/assets/" + model
    cleanWebDirCmd = "sudo rm -r " + assetsDir + "/*/"
    self.runCmd(cleanWebDirCmd)
    self.runCmd("sudo mv " + os.getcwd() +"/scripts/data/" + model + "/* " + assetsDir)

  '''''
  public function transferFilesToProd(model = None)

  Transfers files to production webservers via. Rsync.

  @param String model
  @return void
  '''''
  def transferFilesToProd(self, model = None):

    if model is None:
      self.runCmd("rsync -a -vPr " + self.constants.imageDir + " " + self.constants.imageHost + ":" + self.constants.prodBaseDir)
    else:
      self.runCmd("rsync -a -vPr " + os.getcwd() +"/scripts/data/" + model + " " + self.constants.imageHost + ":" + self.constants.imageDir + self.updatingDir)

  '''''
  private function runCmd(cmd)

  Runs a shell command.

  @param String cmd - Command to run.
  @return boolean
  '''''
  def runCmd(self, cmd):
    FNULL = open(os.devnull, 'w')
    print "Currently executing..."
    print cmd
    return call(cmd, shell=True, stdout=FNULL, stderr=STDOUT)

  '''''
  public function getCurrentRuns(model)

  Get latest run time from database for model.

  @param String model
  @return dictionary dbRunTimes - a dictionary of runtimes for model.
  '''''
  def getCurrentRuns(self, model):

    print "Getting Current Runs from DB..."
    selectQuery = "select model.name as name, run_time from model_runtime JOIN model ON (model.id = model_runtime.model_id) WHERE model.name='" + \
                     model + "' ORDER BY run_time DESC LIMIT 1"

    self.cursor.execute(selectQuery)
    rows = self.cursor.fetchall()

    dbRunTimes = {}
    for row in rows:
      dbRunTimes[row[0]] = row[1]

    return dbRunTimes

  '''''
  public function updateModelTimes(model)

  Updates model run time in DB.
  
  @param String model
  @param String time  - Time of model run.
  @return void
  '''''
  # Insert/update our current model run times.
  def updateModelTimes(self, model, time):

    try:
      # If the current run = run being processed...skip
      if model in self.dbRunTimes:
        if self.dbRunTimes[model] == time:
          return
      insertStr = "INSERT INTO model_runtime (model_id, run_time) " + \
                   "VALUES ((SELECT id FROM model WHERE model.name ='" + model +"'),'" + time + "')"
      self.cursor.execute(insertStr)
      self.cursor.execute("UPDATE model SET updating=1 WHERE name='" + model+"'")
    except Exception, e:
      raise e

    self.conn.commit()
    return

  '''''
  public function setUpdatingFlag(model)

  Sets updating flag -> Sets the "model currently updating" status in DB.
  
  @param String model
  @param int boolValue
  @return void
  '''''
  def setUpdatingFlag(self, model, boolValue):

    try:
      #updateStr = "UPDATE model_runtime SET updating=" + str(boolValue) + \
      #            " WHERE model_id = (SELECT id FROM model WHERE model.name = '" + model + "') AND run_time='" + self.dbRunTimes[model] + "'"
      updateStr = "UPDATE model SET updating =" + str(boolValue) + " WHERE name='" + model+"'"
      self.cursor.execute(updateStr)
      #self.cursor.execute("UPDATE model SET updating =" + str(boolValue) + " WHERE name='" + model+"'")
    except Exception, e:
      raise e

    self.conn.commit()
    return