import time
from bs4 import BeautifulSoup
import urllib2
import datetime, re, os
from subprocess import call
import ConfigParser

'''''
This Class defines everything we need to obtain the model gem files.
It also defines some default directories to save to. 
'''''
class Constants:
  '''''
  Intialize the constants class with everything we need to get model data.

  @return void
  '''''
  def __init__(self):

    # Open our parameters.ini file, and get defined constants.
    config = ConfigParser.SafeConfigParser()
    config.read('conf/parameters.ini')

    # DATA STORAGE DIRECTORIES.
    self.baseDir   = config.get('DEFAULT','BASE_DIR')
    self.gempakDir = config.get('DEFAULT','GEMPAK_DIR')
    self.dataDir   = config.get('DEFAULT','DATA_DIR')

    # Intructions:
    #   curl "http://nomads.ncep.noaa.gov/cgi-bin/filter_nam_conusnest.pl
    #          ?file=gfs.t12z.pgrbf12.grib2&lev_500_mb=on&var_TMP=on
    #          &leftlon=0&rightlon=360&toplat=90&bottomlat=-90&showurl=&dir=%2Fgfs.2009020612"
    #         -o my_file
    self.highResScriptUrls = {
      'nam4km': "http://nomads.ncep.noaa.gov/cgi-bin/filter_nam_conusnest.pl" \
    }
    
    # Full path of data directory.
    self.dataDirEnv = self.baseDir + self.gempakDir + self.dataDir

    self.modelTimes = {
     'ruc': '00,01,02,03,04,05,06,07,08,09,10,11,12', \
     'gfs': '00,06,12,18,24,30,36,42,48,54,60,66,72,78,84,90,96,102,108,114,120,126,132,138,144,150,156,162,168,174,180,192,204,216,228,240', \
     'nam': '00,03,06,09,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60,63,66,69,72,75,78,81,84', \
     'nam12km': '000,003,006,009,012,015,018,021,024,027,030,033,036,039,042,045,048,051,054,057,060,063,066,069,072,075,078,081,084', \
     'ukmet' : '00,06,12,18,24,30,36,42,48,54,60', \
     'ecmf1': '00,24,48,72,96,120,144,168,240', \
     'nam4km': '00,03,06,09,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60'\
    }

    # Define domain/resolution to obtain.
    self.modelTypes = {'ecmf1': '', 'gfs': '211', 'nam':'212', 'ruc': '236', 'ukmet': '','nam12km':'218','nam4km':''}

    # HTTP DATA SOURCES.
    # Link List base Url.
    self.baseDataHttp = "http://motherlode.ucar.edu/repository/entry/show/RAMADDA/Data/IDD+Data/decoded/gempak/model/"

    # Data GET base URL 
    self.getDataHttp = "http://motherlode.ucar.edu/repository/entry/get/RAMADDA/Data/IDD+Data/decoded/gempak/model/"

    self.highResDataHttp = "http://www.ftp.ncep.noaa.gov/data/nccf/com/"
    
    # Get all current run files!
    self.modelGems = {'gfs'  : self.getRun('gfs'), \
                      'ecmf1': self.getRun('ecmf1'), \
                      'ruc'  : self.getRun('ruc'), \
                      'nam'  : self.getRun('nam'), \
                      'ukmet': self.getRun('ukmet'),
                      'nam12km' : self.getNam218('nam12km'),
                      #'nam4km' : self.getHighResRun('nam4km')
                      }

    return;
  
  '''''
  This method parses the soup, and gets all model links with extension _[model][type].gem
  ie. /*_gfs211.gem .
  
  @param soup   - BS object containing HTML content
  @param String - String containing model type. 
  @return list
  '''''
  def getModelLinks(self, html, type):

    soup = BeautifulSoup(html)
    if type == "nam12km":
      modelType = 'nam218'
    else:
      modelType = type + self.modelTypes[type]

    # We want relative paths ending in fileExtension?q1=*
    urlRegex = '('+ modelType +'.*\.(gem))[^/]*$'
    hrefList = soup.find_all('a', text=re.compile(urlRegex))


    # get all hrefs, and split off query parameters and pop off file name into fileList
    fileList = [i.get('href').split('?')[0].split('/')[-1] for i in hrefList if i.get('href')]

    return fileList

  def getLatestHiresFiles(self, html, type):
    soup = BeautifulSoup(html)

    modelType = type

    urlRegex = '(' + modelType + '.*)[^/]*$'
    hrefList = soup.find_all('a', text=re.compile(urlRegex))

    dirList = [i.get('href') for i in hrefList if i.get('href')]

    # Assure that we have the latest run Date.
    latestRun = 0
    for dir in dirList:
      date = dir.split('.')[1][:-1]
      model = dir.split('.')[0]
      if model == modelType and int(date) > int(latestRun):
        latestRunDir = dir

    #latestRunDir  = dirList[-1]

    modelDataUrl = self.highResDataHttp + modelType + "/prod/" + latestRunDir

    content = urllib2.urlopen(modelDataUrl).read()

    soup = BeautifulSoup(content, 'html.parser')

    urlRegex = '^'+ modelType +'.t..z.(conus\w+).hiresf...tm...grib2$'

    hrefList = soup.find_all('a', text=re.compile(urlRegex))
    fileList = [i.get('href') for i in hrefList]
    # for each href, grab latest Run hour.
    latestHour = "00"
    runFileList = []

    # Loop through file list. Build a list of files with latest run only.
    for file in fileList:
      runHour = file.split('.')[1][1:3]
      if int(runHour) > int(latestHour):
        latestHour = runHour
        runFileList = []
        runFileList.append(file)
      else:
        runFileList.append(file)

    #TODO!!
    # http://nomads.ncep.noaa.gov/txt_descriptions/fast_downloading_grib.shtml
    # http://nomads.ncep.noaa.gov/cgi-bin/filter_nam_conusnest.pl
    # This may be more useful... download only grids we need...
    # Package them all into one grib, and convert to gem.

    # When downloading Temp data, select : 2 hybrid level  &  2 m above ground
    return (latestRunDir[:-1],runFileList)

  '''''
  This method gets the url for the latest model run of the model type requested.
  Returns a dictionary keyed on url (Url to get file), and file (The file name).

  @param String - string containing model type.
  @return dictionary
  '''''
  def getRun(self, type):

    model = type

    if model == 'ecmf1':
      model = 'ecmwf'

    # Set our model List url.
    modelListUrl = self.baseDataHttp + model + '/'

    # Set our Model Data GET url.
    modelGetUrl = self.getDataHttp + model + '/'
    content = urllib2.urlopen(modelListUrl).read()
    maxDate = 0
    maxTime = 0
    currentRun = 0

    # Get our list of urls for this model.
    fileList = self.getModelLinks(content, type)

    # Dictionary that stores dates, unix_timestamp, and extensions.
    runDict = [{'date': time.strptime(file.split('_')[0], "%Y%m%d%H"),'time':  time.mktime(datetime.datetime.strptime(file.split('_')[0], "%Y%m%d%H").timetuple()),'extension': file.split('_')[1]} for file in fileList]

    # Get the latest run date, and file name.
    for run in runDict:
      # If the run being analyzed is newer than the current newest run, set the newest run file.
      if run['time'] > maxTime and run['extension'] == (type + self.modelTypes[type] + '.gem'):
        maxTime = run['time']
        maxDate = run['date']
        currentRun = time.strftime("%Y%m%d%H", maxDate) + '_' +  run['extension']

    # Return a URL to the current model run .gem file.
    dataDict = {}
    print modelGetUrl
    print currentRun
    # Skip ecmwf for now.
    dataDict['url']  = modelGetUrl + currentRun
    dataDict['file'] = currentRun

    return dataDict

  def getNam218(self, type):

    model = type

    # Set our model List url.
    modelListUrl = self.baseDataHttp + model + '/'

    # Set our Model Data GET url.
    modelGetUrl = self.getDataHttp + model + '/'
    content = urllib2.urlopen(modelListUrl).read()
    maxDate = 0
    maxTime = 0
    currentRun = 0

    fileList = self.getModelLinks(content, type)
    
    first = fileList[0]

    run = first[0:10]
    runDict = {}

    for file in fileList:
      if file[0:10] == run:
        runDict[file] = modelGetUrl + file

    # Return a URL to the current model run .gem file.
    dataDict = {}
    # Skip ecmwf for now.
    dataDict['files'] = runDict

    return dataDict

  def getHighResRun(self, type):
    model = type
    if type == "nam12km" or type == "nam4km":
      model = 'nam'
    contentListUrl = self.highResDataHttp + model + "/prod/"
    print contentListUrl
    contentList = urllib2.urlopen(contentListUrl).read()

    files = self.getLatestHiresFiles(contentList, model)

    latestRun = files[0]
    files = files[1]
    
    scriptUrl = self.highResScriptUrls[type]
    runDict = {}

    # TODO! Add desired parameters/levels to script d/l urls
    for file in files:
      runDict[file] = scriptUrl + "?dir=/" + latestRun + "&file=" + file

    dataDict = {}

    # A list of all Download urls.
    dataDict['files'] = runDict

    print runDict

    return

