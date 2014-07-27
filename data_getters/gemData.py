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
    self.gfs2p5list = []
    self.gfsp5list = []
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
          if key != "gfs":
            self.catCmd = self.catCmd + " " + savePath + file
          else:
            # GFS model will result in two files... a 2.5 degree file and a .5 degree file.
            if file.split('.')[2].split('f')[0] == "mastergrb2":
              self.gfsp5list.append(savePath + file)
            else:
              self.gfs2p5list.append(savePath + file)
              #self.saveFile(savePath,url,file)
          
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
          #fp = open(savePath + self.constants.runTimes[key] + ".gem", 'w')
          fp = open(savePath + key + ".gem", 'w') # save as model.gem
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

  # Process Grib2 files.
  def processGrib2(self, model, savePath):

    currentRun = self.constants.runTimes[model]

    if model == "gfs":
      outFilep5 = model + '/' + currentRun + '_p5.grib2'
      outFilep5_2 = model + '/' + currentRun + '_p5_2.grib2'
      outFile2p5 = model + '/' + currentRun + '2p5.grib2'

      f = open(outFilep5, "w")
      f2 = open(outFilep5_2, "w")
      f3 = open(outFile2p5, "w")

      def listSort(x, y):
        xForecastHour = 0
        yForecastHour = 0

        if x[-3:-2] == 'f':
          xForecastHour = x[-2:]
        if y[-3:-2] == 'f':
          yForecastHour = y[-2:]
        if x[-4:-3] == 'f':
          xForecastHour = x[-3:]
        if y[-4:-3] == 'f':
          yForecastHour = y[-3:]

        if int(xForecastHour) > int(yForecastHour):
          return 1
        if int(xForecastHour) == int(yForecastHour):
          return 0

        return -1
      # Sort Asc. 
      self.gfsp5list.sort(listSort)

      # Store days 1-5 in one file, and 5-8 in another.
      # Gempak apparently has a max size allowed for gem file.
      fileCtr = 0
      for file in self.gfsp5list:
        if fileCtr <=20:
          fp = open(file, 'r')
          f.write(fp.read())
        else:
          fp = open(file, 'r')
          f2.write(fp.read())
        fileCtr += 1

      for file in self.gfs2p5list:
        fp = open(file, 'r')
        f3.write(fp.read())

      inFile = outFile2p5
      outFile = model + '/' + currentRun + '_2p5.gem'

      cmd = "dcgrib2 " + outFile + ' < ' + inFile

      # # convert our *.grib2 file into a *.gem file.
      self.runCmd(cmd)

      inFile = outFilep5
      outFile = model + '/' + currentRun + '_p5.gem'

      cmd = "dcgrib2 " + outFile + ' < ' + inFile
      self.runCmd(cmd)

      inFile = outFilep5_2
      outFile = model + '/' + currentRun + '_p5_2.gem'

      cmd = "dcgrib2 " + outFile + ' < ' + inFile
      self.runCmd(cmd)

    else:
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
    print url
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


    