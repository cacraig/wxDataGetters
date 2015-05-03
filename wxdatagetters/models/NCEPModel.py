import time
from bs4 import BeautifulSoup
import urllib2
import datetime, re, os


class NCEPModel:
  '''''
  Base Class for all NCEP models.
  '''''
  def __init__(self):
    self.name = ""
    self.modelRegex = ""

    # Intructions:
    #   curl "http://nomads.ncep.noaa.gov/cgi-bin/filter_nam_conusnest.pl
    #          ?file=gfs.t12z.pgrbf12.grib2&lev_500_mb=on&var_TMP=on
    #          &leftlon=0&rightlon=360&toplat=90&bottomlat=-90&showurl=&dir=%2Fgfs.2009020612"
    #         -o my_file
    # Each value contains a url to obtain a specific subset of the grib2 data.
    # This is done to reduce file size and processing/download time.
    self.modelUrls = {
      'nam4km': "http://nomads.ncep.noaa.gov/cgi-bin/filter_nam_conusnest.pl?lev_0C_isotherm=on&lev_1000_mb=on&lev_10_m_above_ground=on" + \
                "&lev_2_m_above_ground=on&lev_850_mb=on&lev_cloud_base=on" + \
                "&lev_entire_atmosphere_%5C%28considered_as_a_single_layer%5C%29=on&lev_180-0_mb_above_ground=on" + \
                "&var_CAPE=on&var_CIN=on&var_HLCY=on&lev_1000-0_m_above_ground=on&lev_3000-0_m_above_ground=on" + \
                # "&lev_convective_cloud_top_level=on&lev_deep_convective_cloud_bottom_level=on&lev_deep_convective_cloud_top_level=on" + \
                # "&lev_shallow_convective_cloud_bottom_level=on&lev_shallow_convective_cloud_top_level=on&lev_convective_cloud_bottom_level=on" + \
                "&lev_30-0_mb_above_ground=on" + \
                "&lev_max_wind=on&lev_mean_sea_level=on" + \
                "&lev_surface=on&var_ABSV=on" + \
                "&var_APCP=on&var_PRMSL=on&var_CAPE=on&var_CFRZR=on&var_CICE=on&var_CICEP=on&var_CRAIN=on&var_CSNOW=on&var_DPT=on&var_GUST=on" + \
                "&var_MSLET=on&var_NCPCP=on&var_REFC=on&var_RH=on&var_SNOWC=on&var_TMP=on&var_TSOIL=on&var_UGRD=on&var_VGRD=on&var_VVEL=on" + \
                "&leftlon=0&rightlon=360&toplat=90&bottomlat=-90", \

      'gfs'   : "http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?lev_1000_mb=on&lev_10_m_above_ground=on&lev_250_mb=on&lev_2_m_above_ground=on" + \
                "&lev_500_mb=on&lev_700_mb=on&lev_3000-0_m_above_ground=on&lev_180-0_mb_above_ground=on" + \
                "&lev_850_mb=on&lev_mean_sea_level=on&lev_surface=on&var_ABSV=on&var_ACPCP=on&var_APCP=on&var_CAPE=on" + \
                "&var_CIN=on&var_RH=on&var_CRAIN=on&var_CSNOW=on&var_CWAT=on&var_DPT=on&var_GUST=on&var_HGT=on&var_PRES=on&var_PRMSL=on&var_PWAT=on&var_TMP=on&var_VVEL=on" + \
                "&var_CAPE=on&var_HLCY=on" + \
                "&var_UGRD=on&var_U-GWD=on&var_VGRD=on&var_V-GWD=on&var_WEASD=on&leftlon=-120&rightlon=-65&toplat=40&bottomlat=20", \

      "nam"   : "http://nomads.ncep.noaa.gov/cgi-bin/filter_nam_na.pl?lev_1000_mb=on&lev_10_m_above_ground=on&lev_150_mb=on&lev_200_mb=on&lev_250_mb=on&lev_2_hybrid_level=on" + \
                "&lev_2_m_above_ground=on&lev_500-1000_mb=on&lev_500_mb=on&lev_650_mb=on&lev_700_mb=on&lev_725_mb=on&lev_750_mb=on&lev_925_mb=on&lev_950_mb=on&lev_975_mb=on" + \
                "&var_CAPE=on&var_CIN=on&var_HLCY=on&lev_3000-0_m_above_ground=on&lev_180-0_mb_above_ground=on" + \
                "&lev_cloud_base=on&lev_entire_atmosphere_%5C%28considered_as_a_single_layer%5C%29=on&lev_max_wind=on&lev_mean_sea_level=on&lev_planetary_boundary_layer=on" + \
                "&lev_surface=on&lev_850_mb=on&var_ABSV=on&var_ACPCP=on&var_APCP=on&var_CAPE=on&var_CFRZR=on&var_CICE=on&var_CICEP=on&var_CRAIN=on&var_CSNOW=on&var_DPT=on" + \
                "&var_DZDT=on&var_EVP=on&var_GUST=on&var_HGT=on&var_ICEC=on&var_PRES=on&var_PRMSL=on&var_PWAT=on&var_REFC=on&var_RH=on&var_TMAX=on" + \
                "&var_TMIN=on&var_TMP=on&var_UGRD=on&var_VGRD=on&var_VVEL=on&var_WEASD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90"
    }

    # Default times.
    self.modelTimes = []

    # Define domain/resolution to obtain.
    self.modelTypes = {'ecmwf': '', 'gfs': '211', 'nam':'212', 'ruc': '236', 'ukmet': '','nam12km':'218','nam4km':''}

    # HTTP DATA SOURCES.
    # Link List base Url.
    self.baseDataHttp = "http://motherlode.ucar.edu/repository/entry/show/RAMADDA/Data/IDD+Data/decoded/gempak/model/"

    # Data GET base URL 
    self.getDataHttp = "http://motherlode.ucar.edu/repository/entry/get/RAMADDA/Data/IDD+Data/decoded/gempak/model/"

    self.highResDataHttp = "http://www.ftp.ncep.noaa.gov/data/nccf/com/"

    # Dict to store model => runTime
    self.runTime = ''

    self.modelGems = {}

    self.modelAliases = ""
    self.isNCEPSource = True

    return
  
  '''''
  This method gets all conusnest High-Resolution model paths. These model paths are an array
  of download paths for grib2 data (one for each time stamp).

  @param list html   - List containing HTML content
  @param String type - String containing model type. 
  @return list
  '''''
  def getFiles(self, html, type, alias = None):
    soup = BeautifulSoup(html)

    modelType = alias

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

    #latestRunDir  = "gfs.2015032612/" # TEST
    #latestRunDir  = "nam.20150502/" # TEST
    # if model == 'nam':
    #   latestRunDir  = "nam.20150328/" # TEST

    modelDataUrl = self.highResDataHttp + modelType + "/prod/" + latestRunDir
    print modelDataUrl
    content = urllib2.urlopen(modelDataUrl).read()

    print modelDataUrl

    soup = BeautifulSoup(content, 'html.parser')

    urlRegex = self.modelRegex

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

    #latestHour = "00" # TEST for NAM and NAM4km

    # Associate the current runTime with the model... nam4km => YYYYMMDDZZ
    if modelType is not type:
      # Use full name, and not alias.
      modelType = type


    self.runTime = latestRunDir.split('/')[0].split('.')[1] + latestHour
    # if model == 'nam':
    #   runFileList = runFileList[0:1]
    #runFileList = runFileList[2:5] # test!
    #print runFileList

    print "Length of currently updated files: " + str(len(runFileList))

    return (latestRunDir[:-1],runFileList)


  '''''
  This method gets the url for the latest model run of the model type requested.
  Returns a dictionary keyed on url (Url to get file), and file (The file name).

  Get model data for NAM 4km, HRRR, WRF ARW, GFS .5 degree... etc.
  These must be downloaded as subsets of .grib2 files (due to their massive size)
  We must specify certain paramaters/levels to grab, rather than pulling the entire model run's data.
  '''''
  def getRun(self):

    runDict = {}

    model = self.name
    alias = self.getAlias()

    contentListUrl = self.highResDataHttp + alias + "/prod/"
    print contentListUrl
    #print contentListUrl
    contentList = urllib2.urlopen(contentListUrl).read()

    filesList = self.getFiles(contentList, model, alias)

    
    latestRun = filesList[0]
    files = filesList[1]

    # Skip if this run has not finished updating yet.
    # if len(files) < self.expectedNumberOfFiles[type]:
    #   print "NUMBER OF FILES: " + str(len(files))
    #   return {}

    scriptUrl = self.modelUrl

    # Set file download paths, along with desired vars/levels.
    gribDir = latestRun

    for file in files:
      runDict[file] = scriptUrl + "&dir=/" + gribDir + "&file=" + file

    dataDict = {}

    # A list of all Download urls.
    dataDict['files'] = runDict

    dataDict = {self.name: dataDict}

    #print files

    return dataDict
  
  '''''
  Filters file list according to rules.
  This is just a template. Default this does nothing. May be overidden.
  '''''
  def filterFiles(self, fileList):
    return

  '''''
  Gets the previous forecast hour  for a given model, and forecast hour.
  '''''
  def getPreviousTime(self, model, currentHour):
    if currentHour == '000':
      return '000'
    defaultHours = self.getDefaultHours()
    defaultHours.sort() #assert ascending order
    for (idx,hour) in enumerate(defaultHours):
      if currentHour == hour:
        return defaultHours[idx-1]

    return '000'

  '''''
  Intialze all of our models hour stamp data to defaults.
  '''''
  def setDefaultHours(self):
    # Default times.
    self.modelTimes = self.defaultTimes
    return

    '''''
  Intialze all of our models hour stamp data to defaults.
  '''''
  def getDefaultHours(self):
    # Default times.
    return self.defaultTimes

  '''''
  Intialze all of our models hour stamp data to defaults.
  '''''
  def getDefaultHours(self):
    # Default times.
    modelTimes = self.defaultTimes
    
    return modelTimes

  def getName(self):
    return self.name

  def getAlias(self):
    return self.modelAlias

  def getForecastHour(self, fileName, noPrefix = False):
    return ""

  def getLastForecastHour(self):
    return "000"

  


  