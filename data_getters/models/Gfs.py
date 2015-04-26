from NCEPModel import NCEPModel

class Gfs(NCEPModel):

  def __init__(self):
    NCEPModel.__init__(self)
    self.lastForecastHour = "384"
    self.name = "gfs"
    self.modelRegex = '^gfs.t..z.pgrb2.0p25.f\d{0,3}$'
    self.defaultTimes = ['000','003','006','009','012','015','018','021','024','027','030','033','036','039','042','045','048','051','054','057','060','063','066','069','072','075','078', \
            '081','084','087','090','093','096','099','102','105','108','111','114','117','120','126','132','138','144', \
            '150','156','162','168','174','180','186','192','198','204','210','216','222', \
            '228','234','240','252','264','276', \
            '288','300','312','324','336','348','360','372','384'], \
    self.modelTimes = []
    self.modelUrl = "http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?lev_1000_mb=on&lev_10_m_above_ground=on&lev_250_mb=on&lev_2_m_above_ground=on" + \
                "&lev_500_mb=on&lev_700_mb=on&lev_3000-0_m_above_ground=on&lev_180-0_mb_above_ground=on" + \
                "&lev_850_mb=on&lev_mean_sea_level=on&lev_surface=on&var_ABSV=on&var_ACPCP=on&var_APCP=on&var_CAPE=on" + \
                "&var_CIN=on&var_RH=on&var_CRAIN=on&var_CSNOW=on&var_CWAT=on&var_DPT=on&var_GUST=on&var_HGT=on&var_PRES=on&var_PRMSL=on&var_PWAT=on&var_TMP=on&var_VVEL=on" + \
                "&var_CAPE=on&var_HLCY=on" + \
                "&var_UGRD=on&var_U-GWD=on&var_VGRD=on&var_V-GWD=on&var_WEASD=on&leftlon=-120&rightlon=-65&toplat=40&bottomlat=20", \
    self.modelAlias = "gfs"
    return

  '''''
  Filter GFS model file list:
  000-120 Hour (3 hour increment)
  120-240 Hour (6 hour increment)
  240-384 Hour (12 hour increment)

  Reduces number of files, Data + Memory usage, and Processing time.
  Additional timesteps aren't really necessary anyways. After 240th hour
  shit hits the fan in terms of chaos and inaccuracy.

  Expected Filtered file count: 73
  '''''
  def filterFiles(self, fileList):
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

  '''''
  Gets forecast hour from a filename, given a model.
  '''''
  def getForecastHour(self, fileName, noPrefix = False):
    forecastHour = ""
    prefix = "f"

    if noPrefix:
      prefix = ""

    # for gfs.t18z.pgrb2full.0p50.f006 -> forecastHour = "006"
    forecastHour = prefix + fileName.split('.')[4][1:4]

    return forecastHour
    
  def getLastForecastHour(self):
    return self.lastForecastHour