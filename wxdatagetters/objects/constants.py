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

    # Full path of data directory.
    self.dataDirEnv = self.baseDir + self.gempakDir + self.dataDir

    return

