from NCEPModel import NCEPModel

class Nam4km(NCEPModel):

  def __init__(self):
    NCEPModel.__init__(self)
    self.lastForecastHour = "060"
    self.name = "nam4km"
    self.modelRegex = '^nam.t..z.(conus\w+).hiresf...tm...grib2$'
    self.defaultTimes = ['000','001','002','003','004','005','006','007','008','009','010','011','012','013','014','015','016','017','018','019','020','021','022','023','024','025', \
                '026','027','028','029','030','031','032','033','034','035','036','039','042','045','048','051','054','057','060']
    self.modelTimes = []
    # "&lev_convective_cloud_top_level=on&lev_deep_convective_cloud_bottom_level=on&lev_deep_convective_cloud_top_level=on" + \
    # "&lev_shallow_convective_cloud_bottom_level=on&lev_shallow_convective_cloud_top_level=on&lev_convective_cloud_bottom_level=on" + \
    self.modelUrl = "http://nomads.ncep.noaa.gov/cgi-bin/filter_nam_conusnest.pl?lev_0C_isotherm=on&lev_1000_mb=on&lev_10_m_above_ground=on" + \
                "&lev_2_m_above_ground=on&lev_850_mb=on&lev_cloud_base=on" + \
                "&lev_entire_atmosphere_%5C%28considered_as_a_single_layer%5C%29=on&lev_180-0_mb_above_ground=on" + \
                "&var_CAPE=on&var_CIN=on&var_HLCY=on&lev_1000-0_m_above_ground=on&lev_3000-0_m_above_ground=on" + \
                "&lev_30-0_mb_above_ground=on" + \
                "&lev_max_wind=on&lev_mean_sea_level=on" + \
                "&lev_surface=on&var_ABSV=on" + \
                "&var_APCP=on&var_PRMSL=on&var_CAPE=on&var_CFRZR=on&var_CICE=on&var_CICEP=on&var_CRAIN=on&var_CSNOW=on&var_DPT=on&var_GUST=on" + \
                "&var_MSLET=on&var_NCPCP=on&var_REFC=on&var_RH=on&var_SNOWC=on&var_TMP=on&var_TSOIL=on&var_UGRD=on&var_VGRD=on&var_VVEL=on" + \
                "&leftlon=0&rightlon=360&toplat=90&bottomlat=-90"
    self.modelAlias = "nam"
    return

  '''''
  Gets forecast hour from a filename, given a model.
  '''''
  def getForecastHour(self, fileName, noPrefix = False):
    forecastHour = ""
    prefix = "f"

    if noPrefix:
      prefix = ""

    # for nam.t06z.blahblah.hiresf07.blah -> forecastHour = "007"
    forecastHour = prefix + "0" + fileName.split('.')[3][6:8]

    return forecastHour

  def getLastForecastHour(self):
    return self.lastForecastHour