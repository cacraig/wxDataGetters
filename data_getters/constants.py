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
    
    # Full path of data directory.
    self.dataDirEnv = self.baseDir + self.gempakDir + self.dataDir

    # Define domain/resolution to obtain.
    self.modelTypes = {'ecmwf': '', 'gfs': '211', 'nam':'212', 'ruc': '236', 'ukmet': ''}

    # HTTP DATA SOURCES.
    # Link List base Url.
    self.baseDataHttp = "http://motherlode.ucar.edu/repository/entry/show/RAMADDA/Data/IDD+Data/decoded/gempak/model/";

    # Data GET base URL 
    self.getDataHttp = "http://motherlode.ucar.edu/repository/entry/get/RAMADDA/Data/IDD+Data/decoded/gempak/model/";
    
    # Get all current run files!
    self.modelGems = {'gfs'  : self.getRun('gfs'), \
    #                  'ecmwf': self.getRun('ecmwf'), \
    #                  'ruc'  : self.getRun('ruc'), \
                      'nam'  : self.getRun('nam'), \
                      'ukmet': self.getRun('ukmet')}

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
    modelType = type + self.modelTypes[type]

    # We want relative paths ending in fileExtension?q1=*
    urlRegex = '(' + modelType + '.*\.(gem))[^/]*$'
    hrefList = soup.find_all('a', text=re.compile(urlRegex))

    # get all hrefs, and split off query parameters and pop off file name into fileList
    fileList = [i.get('href').split('?')[0].split('/')[-1] for i in hrefList if i.get('href')]

    return fileList

  '''''
  This method gets the url for the latest model run of the model type requested.
  Returns a dictionary keyed on url (Url to get file), and file (The file name).

  @param String - string containing model type.
  @return dictionary
  '''''
  def getRun(self, type):

    model = type
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

    # Skip ecmwf for now.
    dataDict['url']  = modelGetUrl + currentRun
    dataDict['file'] = currentRun

    return dataDict
