import time
from bs4 import BeautifulSoup
import urllib2
import datetime, re, os
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
  def __init__(self, modelsOverride=None):

    # Open our parameters.ini file, and get defined constants.
    config = ConfigParser.SafeConfigParser()
    config.read('conf/parameters.ini')

    # DATA STORAGE DIRECTORIES.
    self.baseDir   = config.get('DEFAULT', 'BASE_DIR')
    self.gempakDir = config.get('DEFAULT', 'GEMPAK_DIR')
    self.dataDir   = config.get('DEFAULT', 'DATA_DIR')
    self.webDir    = config.get('DEFAULT', 'WEB_DIR')
    self.distDir   = config.get('DEFAULT', 'DIST_DIR')
    self.dbConnStr = config.get('DEFAULT', 'DB_CONN')
    self.imageHost = config.get('DEFAULT', 'IMAGE_HOST')
    self.imageDir  = config.get('DEFAULT', 'IMAGE_DIR')
    self.prodBaseDir  = config.get('DEFAULT', 'PRODUCTION_DIR')
    self.beanstalkdHost = config.get('DEFAULT', 'BEANSTALKD_HOST')
    self.redisHost = config.get('DEFAULT', 'REDIS_HOST')
    self.errorLog = config.get('DEFAULT', 'ERROR_LOG')
    self.execLog = config.get('DEFAULT', 'EXEC_LOG')
    self.numPyTmpDir =  config.get('DEFAULT', 'NP_TMP_DIR')

    self.expectedNumberOfFiles = {
      "nam": 28,
      "nam4km" : 44,
      "gfs" : 65 # [BANDAID FIX] Actually 73 but if we begin d/l when 65 are complete, the rest should complete by the time script finishes
    }

    self.lastForecastHour = {
      "nam": "084",
      "nam4km": "060",
      "gfs": "384"

    }

    self.modelRegex = {
      "nam": "^nam.t..z.awip32...tm...grib2$",
      "nam4km": '^nam.t..z.(conus\w+).hiresf...tm...grib2$',
      #"gfs": '^gfs.t..z.pgrb2full.0p50.f\d{0,3}$'
      "gfs": '^gfs.t..z.pgrb2.0p25.f\d{0,3}$'
    }

    self.modelAliases = {
      "nam4km" : "nam" \
    }

    self.highResModelList = ['nam4km', "gfs","nam"]

    # Intructions:
    #   curl "http://nomads.ncep.noaa.gov/cgi-bin/filter_nam_conusnest.pl
    #          ?file=gfs.t12z.pgrbf12.grib2&lev_500_mb=on&var_TMP=on
    #          &leftlon=0&rightlon=360&toplat=90&bottomlat=-90&showurl=&dir=%2Fgfs.2009020612"
    #         -o my_file
    # Each value contains a url to obtain a specific subset of the grib2 data.
    # This is done to reduce file size and processing/download time.
    self.highResScriptUrls = {
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
    
    # Full path of data directory.
    self.dataDirEnv = self.baseDir + self.gempakDir + self.dataDir

    # self.modelTimes = {
    #  'ruc': '00,01,02,03,04,05,06,07,08,09,10,11,12', \
    #  'gfs': '000,003,006,009,012,015,018,021,024,027,030,033,036,039,042,045,048,051,054,057,060,063,066,069,072,075,078,' + \
    #         '081,084,087,090,093,096,099,102,105,108,111,114,117,120,123,126,129,132,135,138,141,144,147,'+ \
    #         '150,153,156,159,162,165,168,171,174,177,180,183,186,189,192,195,198,201,204,207,210,213,216,219,222,225,' +\
    #         '228,231,234,237,240,252,264,276,' + \
    #         '288,300,312,324,336,348,360,372,384', \
    #  'nam': '000,003,006,009,012,015,018,021,024,027,030,033,036,039,042,045,048,051,054,057,060,063,066,069,072,075,078,081,084', \
    #  'hrrr': '000,001,002,003,004,005,006,007,008,009,010,011,012,013,014,015,016,017,018,019,020,021,022,023', \
    #  #'nam12km': '000,003,006,009,012,015,018,021,024,027,030,033,036,039,042,045,048,051,054,057,060,063,066,069,072,075,078,081,084', \
    #  'ukmet' : '00,06,12,18,24,30,36,42,48,54,60', \
    #  'rap': '000,001,002,003,004,005,006,007,008,009,010,011,012,013,014,015,016,017,018,019,020,021,022,023', \
    #  'ecmf1': '00,24,48,72,96,120,144,168,240', \
    #  'nam4km': '000,001,002,003,004,005,006,007,008,009,010,011,012,013,014,015,016,017,018,019,020,021,022,023,024,025,026,027,028,029,030,031,032,033,034,035,036,039,042,045,048,051,054,057,060'\
    # }

    # Default times.
    self.modelTimes = {
     'ruc': [], \
     'gfs': [], \
     'nam': [], \
     'hrrr': [], \
     #'nam12km': '000,003,006,009,012,015,018,021,024,027,030,033,036,039,042,045,048,051,054,057,060,063,066,069,072,075,078,081,084', \
     'ukmet' : [], \
     'rap': [], \
     'ecmf1': [], \
     'nam4km': [] \
    }

    # Define domain/resolution to obtain.
    self.modelTypes = {'ecmf1': '', 'gfs': '211', 'nam':'212', 'ruc': '236', 'ukmet': '','nam12km':'218','nam4km':''}

    # HTTP DATA SOURCES.
    # Link List base Url.
    self.baseDataHttp = "http://motherlode.ucar.edu/repository/entry/show/RAMADDA/Data/IDD+Data/decoded/gempak/model/"

    # Data GET base URL 
    self.getDataHttp = "http://motherlode.ucar.edu/repository/entry/get/RAMADDA/Data/IDD+Data/decoded/gempak/model/"

    self.highResDataHttp = "http://www.ftp.ncep.noaa.gov/data/nccf/com/"

    # Dict to store model => runTime
    self.runTimes = {}

    if modelsOverride:
      self.modelGems = { modelsOverride: self.getRun(modelsOverride) }
    else:
      # Get all current run files!
      self.modelGems = {
         'gfs'  : self.getRun('gfs'), \
         'ecmf1': self.getRun('ecmf1'), \
         'ruc'  : self.getRun('ruc'), \
         'nam'  : self.getRun('nam'), \
         'ukmet': self.getRun('ukmet'), \
         # 'nam12km' : self.getRun('nam12km'), \
         'nam4km' : self.getRun('nam4km') \
      }

    return;

  '''''
  Intialze all of our models hour stamp data to defaults.
  '''''
  def setDefaultHours(self):
    # Default times.
    self.modelTimes = {
     'ruc': ['00','01','02','03','04','05','06','07','08','09','10','11','12'], \
     'gfs': ['000','003','006','009','012','015','018','021','024','027','030','033','036','039','042','045','048','051','054','057','060','063','066','069','072','075','078', \
            '081','084','087','090','093','096','099','102','105','108','111','114','117','120','123','126','129','132','135','138','141','144','147', \
            '150','153','156','159','162','165','168','171','174','177','180','183','186','189','192','195','198','201','204','207','210','213','216','219','222','225', \
            '228','231','234','237','240','252','264','276', \
            '288','300','312','324','336','348','360','372','384'], \
     'nam': ['000','003','006','009','012','015','018','021','024','027','030','033','036','039','042','045','048','051','054','057','060','063','066','069','072','075','078','081','084'], \
     'hrrr': ['000','001','002','003','004','005','006','007','008','009','010','011','012','013','014','015','016','017','018','019','020','021','022','023'], \
     #'nam12km': '000,003,006,009,012,015,018,021,024,027,030,033,036,039,042,045,048,051,054,057,060,063,066,069,072,075,078,081,084', \
     'ukmet' : ['00','06','12','18','24','30','36','42','48','54','60'], \
     'rap': ['000','001','002','003','004','005','006','007','008','009','010','011','012','013','014','015','016','017','018','019','020','021','022','023'], \
     'ecmf1': ['00','24','48','72','96','120','144','168','240'], \
     'nam4km': ['000','001','002','003','004','005','006','007','008','009','010','011','012','013','014','015','016','017','018','019','020','021','022','023','024','025', \
                '026','027','028','029','030','031','032','033','034','035','036','039','042','045','048','051','054','057','060'] \
    }
    return

  '''''
  Intialze all of our models hour stamp data to defaults.
  '''''
  def getDefaultHoursByModel(self, model):
    # Default times.
    modelTimes = {
     'ruc': ['00','01','02','03','04','05','06','07','08','09','10','11','12'], \
     'gfs': ['000','003','006','009','012','015','018','021','024','027','030','033','036','039','042','045','048','051','054','057','060','063','066','069','072','075','078', \
            '081','084','087','090','093','096','099','102','105','108','111','114','117','120','123','126','129','132','135','138','141','144','147', \
            '150','153','156','159','162','165','168','171','174','177','180','183','186','189','192','195','198','201','204','207','210','213','216','219','222','225', \
            '228','231','234','237','240','252','264','276', \
            '288','300','312','324','336','348','360','372','384'], \
     'nam': ['000','003','006','009','012','015','018','021','024','027','030','033','036','039','042','045','048','051','054','057','060','063','066','069','072','075','078','081','084'], \
     'hrrr': ['000','001','002','003','004','005','006','007','008','009','010','011','012','013','014','015','016','017','018','019','020','021','022','023'], \
     #'nam12km': '000,003,006,009,012,015,018,021,024,027,030,033,036,039,042,045,048,051,054,057,060,063,066,069,072,075,078,081,084', \
     'ukmet' : ['00','06','12','18','24','30','36','42','48','54','60'], \
     'rap': ['000','001','002','003','004','005','006','007','008','009','010','011','012','013','014','015','016','017','018','019','020','021','022','023'], \
     'ecmf1': ['00','24','48','72','96','120','144','168','240'], \
     'nam4km': ['000','001','002','003','004','005','006','007','008','009','010','011','012','013','014','015','016','017','018','019','020','021','022','023','024','025', \
                '026','027','028','029','030','031','032','033','034','035','036','039','042','045','048','051','054','057','060'] \
    }
    
    return modelTimes[model]

  '''''
  This method parses the soup, and gets all model links with extension _[model][type].gem
  ie. /*_gfs211.gem .
  
  @param list html   - List containing HTML content
  @param String type - String containing model type. 
  @return list
  '''''
  def getModelLinks(self, html, type):

    soup = BeautifulSoup(html)
    # if type == "nam12km":
    #   modelType = 'nam218'
    # else:
    modelType = type + self.modelTypes[type]

    # We want relative paths ending in fileExtension?q1=*
    urlRegex = '('+ modelType +'.*\.(gem))[^/]*$'
    hrefList = soup.find_all('a', text=re.compile(urlRegex))


    # get all hrefs, and split off query parameters and pop off file name into fileList
    fileList = [i.get('href').split('?')[0].split('/')[-1] for i in hrefList if i.get('href')]

    return fileList

  '''''
  This method gets all conusnest High-Resolution model paths. These model paths are an array
  of download paths for grib2 data (one for each time stamp).

  @param list html   - List containing HTML content
  @param String type - String containing model type. 
  @return list
  '''''
  def getLatestHiresFiles(self, html, type, alias = None):
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
    #latestRunDir  = "nam.20150328/" # TEST

    modelDataUrl = self.highResDataHttp + modelType + "/prod/" + latestRunDir

    content = urllib2.urlopen(modelDataUrl).read()

    print modelDataUrl

    soup = BeautifulSoup(content, 'html.parser')

    urlRegex = self.modelRegex[type]

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

    if modelType == "gfs":
      self.runTimes[modelType] = latestRunDir.split('/')[0].split('.')[1]
      runFileList = self.filterGFSFiles(runFileList)
    else:
      self.runTimes[modelType] = latestRunDir.split('/')[0].split('.')[1] + latestHour

    #runFileList = runFileList[10:30] # test!
    print runFileList

    print "Length of currently updated files: " + str(len(runFileList))

    return (latestRunDir[:-1],runFileList)

  '''''
  This method gets the url for the latest model run of the model type requested.
  Returns a dictionary keyed on url (Url to get file), and file (The file name).

  @param String - string containing model type.
  @return dictionary
  '''''
  def getRun(self, type):

    if self.isHighRes(type):
      return self.getHighResRun(type)

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

    dataDict['url']  = modelGetUrl + currentRun
    dataDict['file'] = currentRun

    self.runTimes[type] = currentRun.split('_')[0]

    return dataDict

  '''''
  Get model data for NAM 4km, HRRR, WRF ARW, GFS .5 degree... etc.
  These must be downloaded as subsets of .grib2 files (due to their massive size)
  We must specify certain paramaters/levels to grab, rather than pulling the entire model run's data.
  '''''
  def getHighResRun(self, type):

    runDict = {}

    model = type
    alias = self.getAlias(model)

    contentListUrl = self.highResDataHttp + alias + "/prod/"
    print contentListUrl
    contentList = urllib2.urlopen(contentListUrl).read()

    filesList = self.getLatestHiresFiles(contentList, model, alias)

    
    latestRun = filesList[0]
    files = filesList[1]

    # Skip if this run has not finished updating yet.
    # if len(files) < self.expectedNumberOfFiles[type]:
    #   print "NUMBER OF FILES: " + str(len(files))
    #   return {}

    scriptUrl = self.highResScriptUrls[type]

    # Set file download paths, along with desired vars/levels.
    gribDir = latestRun

    for file in files:
      runDict[file] = scriptUrl + "&dir=/" + gribDir + "&file=" + file

    dataDict = {}

    # A list of all Download urls.
    dataDict['files'] = runDict

    print files

    return dataDict

  def isHighRes(self, model):
    if model in self.highResModelList:
      return True
    else:
      return False

  def getAlias(self, model):
    if model in self.modelAliases:
      return self.modelAliases[model]
    else:
      return model

  '''''
  Filter GFS model file list:
  000-120 Hour (3 hour increment)
  120-240 Hour (6 hour increment)
  240-384 Hour (12 hour increment)

  Reduces number of files, Data + Memory usage, and Processing time.
  Additional timesteps aren't really necessary anyways. After 240th hour
  shit hits the fan in terms of choas and inaccuracy.

  Expected Filtered file count: 73
  '''''
  def filterGFSFiles(self, fileList):
    fileListCopy = []
    for idx, fileName in enumerate(fileList):
      forecastHour = int(fileName.split('.')[4][1:4])

      # if forecastHour == 384:
      #   fileListCopy.append(fileName)

      if forecastHour <= 120:
        fileListCopy.append(fileName)

      elif forecastHour > 120 and forecastHour <=240 and (forecastHour % 6) == 0:
        # Remove file from list.
        fileListCopy.append(fileName)

      elif forecastHour > 240 and (forecastHour % 12) == 0:
        # Remove file from list.
        fileListCopy.append(fileName)

    return fileListCopy

  def getForecastHour(self, model, fileName, noPrefix = False):
    forecastHour = ""
    prefix = "f"

    if noPrefix:
      prefix = ""

    if model == 'gfs':
      # for gfs.t18z.pgrb2full.0p50.f006 -> forecastHour = "006"
      forecastHour = prefix + fileName.split('.')[4][1:4]
    elif model == 'nam':
      # for nam.t18z.awip3281.tm00.grib2 -> forecastHour = "081"
      forecastHour = prefix + "0" + fileName.split('.')[2][6:8]
    elif model == 'nam4km':
      # for nam.t06z.blahblah.hiresf07.blah -> forecastHour = "007"
      forecastHour = prefix + "0" + fileName.split('.')[3][6:8]

    return forecastHour

  def getPreviousTime(self, model, currentHour):
    if currentHour == '000':
      return '000'
    defaultHours = self.getDefaultHoursByModel(model)
    defaultHours.sort() #assert ascending order
    for (idx,hour) in enumerate(defaultHours):
      if currentHour == hour:
        return defaultHours[idx-1]

    return '000'


