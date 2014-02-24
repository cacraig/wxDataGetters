import time
from bs4 import BeautifulSoup
import urllib2
import datetime

'''''
This Class defines everything we need to obtain the model gem files.
It also defines some default directories to save to. 
'''''
class Constants:

  # Intialize the constants class with everything we need to get model data.
  def __init__(self):

    # DATA STORAGE DIRECTORIES.
    self.baseDir   = "/home/cacraig/"
    self.gempakDir = "gempak/GEMPAK7/gempak/"
    self.dataDir   = "data/model/"

    # Define domain/resolution to obtain.
    self.modelTypes = {'ecmwf': '', 'gfs': '211', 'nam':'211', 'ruc': '236', 'ukmet': ''}

    # HTTP DATA SOURCES.
    self.baseDataHttp = "http://metfs1.agron.iastate.edu/data/gempak/model/"

    
    # Get all current run files!
    self.modelGems = {'gfs'  : self.getRun(self.baseDataHttp,'gfs'), \
    #                  'ecmwf': self.getRun(self.baseDataHttp,'ecmwf'), \
                      'ruc'  : self.getRun(self.baseDataHttp,'ruc'), \
                      'nam'  : self.getRun(self.baseDataHttp,'nam'), \
                      'ukmet': self.getRun(self.baseDataHttp,'ukmet')}

    return;

  '''''
  This method gets the url for the latest model run of the model type requested.
  Returns a dictionary keyed on url (Url to get file), and file (The file name).

  @return dictionary
  '''''
  def getRun(self, modelUrl, type):
    model = type
    # Add desired to url string.
    modelUrl = modelUrl + model + '/'
    content = urllib2.urlopen(modelUrl).read()
    soup = BeautifulSoup(content)
    maxDate = 0
    maxTime = 0
    currentRun = 0
    hrefList = soup.find_all('a')
    # Pop off crap links.
    [hrefList.pop(0) for i in range(5)]
    # Get all non-empty file names
    fileList = [i.get('href') for i in hrefList if i.get('href')]

    if type == 'gfs' or type == 'nam' or type == 'ruc' or type == 'ukmet':

      # Dictionary that stores the dates, and extensions.
      runDict = [{'date': time.strptime(file.split('_')[0], "%Y%m%d%H"),'time':  time.mktime(datetime.datetime.strptime(file.split('_')[0], "%Y%M%d%H").timetuple()),'extension': file.split('_')[1]} for file in fileList]
      
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
    if type != 'ecmwf':
      dataDict['url']  = modelUrl + currentRun
      dataDict['file'] = currentRun
    return dataDict