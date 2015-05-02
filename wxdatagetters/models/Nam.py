from NCEPModel import NCEPModel

class Nam(NCEPModel):

  def __init__(self):
    NCEPModel.__init__(self)
    self.lastForecastHour = "084"
    self.name = "nam"
    self.modelRegex = "^nam.t..z.awip32...tm...grib2$"
    self.defaultTimes = ['000','003','006','009','012','015','018','021','024','027','030','033','036','039','042','045','048','051','054','057','060','063','066','069','072','075','078','081','084']
    self.modelTimes = []
    self.runTime  = ''
    self.modelUrl = "http://nomads.ncep.noaa.gov/cgi-bin/filter_nam_na.pl?lev_1000_mb=on&lev_10_m_above_ground=on&lev_150_mb=on&lev_200_mb=on&lev_250_mb=on&lev_2_hybrid_level=on" + \
                "&lev_2_m_above_ground=on&lev_500-1000_mb=on&lev_500_mb=on&lev_650_mb=on&lev_700_mb=on&lev_725_mb=on&lev_750_mb=on&lev_925_mb=on&lev_950_mb=on&lev_975_mb=on" + \
                "&var_CAPE=on&var_CIN=on&var_HLCY=on&lev_3000-0_m_above_ground=on&lev_180-0_mb_above_ground=on" + \
                "&lev_cloud_base=on&lev_entire_atmosphere_%5C%28considered_as_a_single_layer%5C%29=on&lev_max_wind=on&lev_mean_sea_level=on&lev_planetary_boundary_layer=on" + \
                "&lev_surface=on&lev_850_mb=on&var_ABSV=on&var_ACPCP=on&var_APCP=on&var_CAPE=on&var_CFRZR=on&var_CICE=on&var_CICEP=on&var_CRAIN=on&var_CSNOW=on&var_DPT=on" + \
                "&var_DZDT=on&var_EVP=on&var_GUST=on&var_HGT=on&var_ICEC=on&var_PRES=on&var_PRMSL=on&var_PWAT=on&var_REFC=on&var_RH=on&var_TMAX=on" + \
                "&var_TMIN=on&var_TMP=on&var_UGRD=on&var_VGRD=on&var_VVEL=on&var_WEASD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90"
    self.modelAlias = "nam"
    return

  '''''
  Gets forecast hour from a filename, given a model.
  '''''
  def getForecastHour(self, fileName, noPrefix = False):
    forecastHour = ""
    prefix = "f"
    model = self.name

    if noPrefix:
      prefix = ""

    # for nam.t18z.awip3281.tm00.grib2 -> forecastHour = "081"
    forecastHour = prefix + "0" + fileName.split('.')[2][6:8]

    return forecastHour

  def getLastForecastHour(self):
    return self.lastForecastHour