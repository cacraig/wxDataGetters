import urllib2
from constants import Constants
import os
from subprocess import call
from timeout import timeout
import errno
import psycopg2
import redis

# TODO: Speed up download, and require less RAM. 
#         -> http://stackoverflow.com/questions/1517616/stream-large-binary-files-with-urllib2-to-file
# Class for downloading data, and cleaning data directories.
class GemData:

  def __init__(self, models=None):
    self.constants = Constants(models)
    print "CREATING CONN"
    self.conn = psycopg2.connect(self.constants.dbConnStr)
    self.cursor = self.conn.cursor()
    self.dbRunTimes = self.getCurrentRuns()
    self.redisConn = redis.Redis(self.constants.redisHost)
    self.updated = False
    self.catCmd = "cat "
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

      if key in self.dbRunTimes:
        if self.constants.runTimes[key] == self.dbRunTimes[key]:
          del self.constants.runTimes[key]
          print "Skipping: " + key + "... Model not updated."
          continue

      if 'files' in http:
        # download all files in http['files'].
        print "PROCESSING MANY"
        files = http['files']
        savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/'
        for file,url in files.items():
          savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/'
          print "downloading " + savePath  + file
          self.saveFile(savePath,url,file)
          self.catCmd = self.catCmd + " " + savePath + file
          
        self.processGrib2(key,savePath)
        # After data has been sucessfully retrieved, and no errors thrown update model run time.
        self.updateModelTimes(key, self.constants.runTimes[key])
        self.updated = True
        self.redisConn.set(key, "0")
      else:
        savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/'

        try:
          print "Saving: " + http['url'] + " to " + savePath + http['file']
          gemFile = urllib2.urlopen(http['url']).read()
          fp = open(savePath + http['file'], 'w')
          fp.write(gemFile)
          fp.close()
          # After data has been sucessfully retrieved, and no errors thrown update model run time.
          self.updateModelTimes(key, self.constants.runTimes[key])
          self.updated = True
          self.redisConn.set(key, "0")
        except Exception, e:
          print "Could not get Model *.gem " + http['file'] + " with url: " + http['url']
          print " with exception %s" % e
          pass
          
    # Jump back to present WD
    os.chdir(currentDir)
    self.conn.close()
    return

  def isUpdated(self):
    return self.updated

  def processGrib2(self, model, savePath):
    # extension = fileName.split('.')[-1]
    # if extension != 'grib2':
    #   return

    # # for model.t06z.blahblah.hiresf07.blah -> forecastHour = "07"
    # forecastHour = fileName.split('.')[3][6:8]
    currentRun = self.constants.runTimes[model]
    # inFile  = savePath + fileName
    # outFile = model + '/' + currentRun + "f0" + forecastHour + '_' + model + '.gem'
    # cmd = "dcgrib2 " + outFile + ' < ' + inFile
    outFile = model + '/' + currentRun + '.grib2'
    self.catCmd = self.catCmd + " > " + outFile
    self.runCmd(self.catCmd)

    inFile = outFile
    outFile = model + '/' + currentRun + '.gem'

    cmd = "dcgrib2 " + outFile + ' < ' + inFile

    # convert our *.grib2 file into a *.gem file.
    self.runCmd(cmd)
    return

  #timeout after 15 mins.
  @timeout(900, os.strerror(errno.ETIMEDOUT))
  def saveFile(self, savePath,url, file):
    gemFile = urllib2.urlopen(url).read()
    fp = open(savePath + file, 'w')
    fp.write(gemFile)
    fp.close()
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
    # scp -r /var/www/ngwips/client/dist/src/assets ubuntu@54.186.9.28:/var/www/ngwips/client/dist/src
    if model is None:
      self.runCmd("scp -r " + self.constants.imageDir + " " + self.constants.imageHost + ":" + self.constants.prodBaseDir)
    else:
      self.runCmd("scp -r " + os.getcwd() +"/scripts/data/" + model + " " + self.constants.imageHost + ":" + self.constants.imageDir)

  def runCmd(self, cmd):
    return call(cmd, shell=True)

  def getCurrentRuns(self):
    print "ATTEMPT"
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
    try:
      self.cursor.execute("SELECT * from model where name='" + model + "'")
      # if self.cursor.fetchone() is None:
      #   self.cursor.execute("INSERT INTO current_run (name, utc_time) VALUES ('" + model + "','" + time + "')")
      # else:
      self.cursor.execute("UPDATE model SET current_run ='" + time + "' WHERE name='" + model+"'")
    except Exception, e:
      print e.pgerror

    self.conn.commit()
    return


    