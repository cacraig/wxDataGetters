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
class GemData:

  def __init__(self, models=None, debug=False):
    self.constants = Constants(models)
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
  getData loops through our model download paths, and saves them to our specified save paths in self.constants.
  '''''
  def getData(self):
    currentDir = os.getcwd()
    os.chdir(self.constants.dataDirEnv)

    for key,http in self.constants.modelGems.items():
      print http

      # If it is empty for any reason, skip!
      if not http:
        del self.constants.runTimes[key]
        print "Skipping: " + key + "... Model not updated."
        continue

      # If DEBUG is True, clear all model times so they aren't skipped.
      if self.DEBUG:
        for model,time in self.dbRunTimes.items():
          self.dbRunTimes[model] = ""

      self.dbRunTimes = self.getCurrentRuns(key)

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
    hourKeys = self.constants.getDefaultHoursByModel(model)
    for hour in hourKeys:
      self.redisConn.set(model + '-' + hour, "0")
    return

  def setRunCompletionFlag(self, model):

    f = open(self.constants.execLog, 'w')
    f.write('Trying: ' + model + '-complete')
    for item in self.constants.modelTimes[model]:
      f.write("Hour: " + item)

    if self.constants.lastForecastHour[model] in self.constants.modelTimes[model]:
      self.redisConn.set(model + '-complete', self.constants.runTimes[model])
      self.complete = True
      # Set updating directory to empty string.
      # When model is complete, copy images to completed directory
      self.updatingDir = ""
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
      f = open(self.constants.errorLog,'w')
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
        os.close(resp.fileno())
        resp.close()

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
      for res in executor.map(self.saveFilesThread, args):
        if res == False:
          print "Exiting... See error.log for details."
          exit(1)
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