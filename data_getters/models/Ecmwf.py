from NonNCEPModel import NonNCEPModel

class Ecmwf(NonNCEPModel):

  def __init__(self):
    # super(NonNCEPModel, self).__init__()
    NonNCEPModel.__init__(self)
    self.lastForecastHour = "240"
    self.name = "ecmwf"
    self.modelAlias = "ecmwf"
    self.defaultTimes = ['000','024','048','072','096','120','144','168','240']
    self.modelTimes = []
    self.modelUrl = 'data-portal.ecmwf.int/'
    self.runTime = ''
    return

  '''''
  Returns model files grouped by forecast hour filename (grib2).
  '''''
  def getRun(self):

    username = 'wmo'
    password = 'essential'
    model = self.name
    modelRunUrl = ''
    modelListUrl = "ftp://wmo:essential@" + self.modelUrl
    runTime = ''

    # Parse it, get model run time.
    from datetime import datetime, timedelta
    dateUTC = datetime.utcnow()
    currentHour = int(dateUTC.hour)

    # If we haven't crossed the 6th hour, we should look at the previous day's output.
    if currentHour <= 5:
      dateUTC = dateUTC - timedelta(days=1)

    month = str(dateUTC.month)
    year  = str(dateUTC.year)
    day   = str(dateUTC.day)
    ddhh  = ""

    if int(day) < 10:
      day = '0' + day

    if int(month) < 10:
      month = '0' + month

    # Get model Run Dir.
    if currentHour >= 20 or currentHour <= 5:
      runTime = year + month + day + "12"
      ddhh = day + "12"
      # Get 12z run.
      modelRunUrl = modelListUrl + year + month + day + "120000/"
    elif currentHour >=9:
      runTime = year + month + day + "00"
      ddhh = day + "00"
      # Get 0Z run.
      modelRunUrl = modelListUrl + year + month + day + "000000/"

    # content = urllib2.urlopen(modelRunUrl).read()
    
    wmoLevels = ['500hPa', 'msl', '850hPa']
    wmoVars   = ['t', 'ws', 'u','v','gh']

    runFileList = []

    files = [
      "A_HHXA50ECMF*_C_ECMF_^_an_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HHXE50ECMF*_C_ECMF_^_24h_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HHXI50ECMF*_C_ECMF_^_48h_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HHXK50ECMF*_C_ECMF_^_72h_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HHXM50ECMF*_C_ECMF_^_96h_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HHXO50ECMF*_C_ECMF_^_120h_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HHXQ50ECMF*_C_ECMF_^_144h_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HHXS50ECMF*_C_ECMF_^_168h_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HHXW50ECMF*_C_ECMF_^_192h_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HHXY50ECMF*_C_ECMF_^_216h_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HHXT50ECMF*_C_ECMF_^_240h_gh_500hPa_global_0p5deg_grib2.bin", \
      "A_HPXA89ECMF*_C_ECMF_^_an_msl_global_0p5deg_grib2.bin", \
      "A_HPXE89ECMF*_C_ECMF_^_24h_msl_global_0p5deg_grib2.bin", \
      "A_HPXI89ECMF*_C_ECMF_^_48h_msl_global_0p5deg_grib2.bin", \
      "A_HPXK89ECMF*_C_ECMF_^_72h_msl_global_0p5deg_grib2.bin", \
      "A_HPXM89ECMF*_C_ECMF_^_96h_msl_global_0p5deg_grib2.bin", \
      "A_HPXO89ECMF*_C_ECMF_^_120h_msl_global_0p5deg_grib2.bin", \
      "A_HPXQ89ECMF*_C_ECMF_^_144h_msl_global_0p5deg_grib2.bin", \
      "A_HPXS89ECMF*_C_ECMF_^_168h_msl_global_0p5deg_grib2.bin", \
      "A_HPXT89ECMF*_C_ECMF_^_240h_msl_global_0p5deg_grib2.bin", \
      "A_HPXW89ECMF*_C_ECMF_^_192h_msl_global_0p5deg_grib2.bin", \
      "A_HPXY89ECMF*_C_ECMF_^_216h_msl_global_0p5deg_grib2.bin", \
      "A_HTXA85ECMF*_C_ECMF_^_an_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HTXE85ECMF*_C_ECMF_^_24h_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HTXI85ECMF*_C_ECMF_^_48h_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HTXK85ECMF*_C_ECMF_^_72h_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HTXM85ECMF*_C_ECMF_^_96h_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HTXO85ECMF*_C_ECMF_^_120h_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HTXQ85ECMF*_C_ECMF_^_144h_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HTXS85ECMF*_C_ECMF_^_168h_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HTXT85ECMF*_C_ECMF_^_240h_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HTXW85ECMF*_C_ECMF_^_192h_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HTXY85ECMF*_C_ECMF_^_216h_t_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXA85ECMF*_C_ECMF_^_an_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXE85ECMF*_C_ECMF_^_24h_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXI85ECMF*_C_ECMF_^_48h_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXK85ECMF*_C_ECMF_^_72h_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXM85ECMF*_C_ECMF_^_96h_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXO85ECMF*_C_ECMF_^_120h_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXQ85ECMF*_C_ECMF_^_144h_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXS85ECMF*_C_ECMF_^_168h_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXT85ECMF*_C_ECMF_^_240h_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXW85ECMF*_C_ECMF_^_192h_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HUXY85ECMF*_C_ECMF_^_216h_u_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXA85ECMF*_C_ECMF_^_an_v_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXE85ECMF*_C_ECMF_^_24h_v_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXI85ECMF*_C_ECMF_^_48h_v_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXK85ECMF*_C_ECMF_^_72h_v_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXM85ECMF*_C_ECMF_^_96h_v_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXO85ECMF*_C_ECMF_^_120h_v_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXQ85ECMF*_C_ECMF_^_144h_v_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXS85ECMF*_C_ECMF_^_168h_v_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXT85ECMF*_C_ECMF_^_240h_v_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXW85ECMF*_C_ECMF_^_192h_v_850hPa_global_0p5deg_grib2.bin", \
      "A_HVXY85ECMF*_C_ECMF_^_216h_v_850hPa_global_0p5deg_grib2.bin" \
    ]

    runDict = {}
    for f in files:
      parts = f.split('*')
      newStr = parts[0] + ddhh + "00" + parts[1]

      parts = newStr.split('^')
      newStr = parts[0] + runTime + "0000" + parts[1]

      forecastHour = newStr.split('_')[5]
      if forecastHour == "an":
        forecastHour = "00h"
      forecastHour = forecastHour[:-1]
      if int(forecastHour) < 100:
        forecastHour = "0" + forecastHour
      gribFile = runTime + forecastHour + ".grib2"
      if gribFile not in runDict:
        runDict[gribFile] = []
      url = modelRunUrl + newStr
      runDict[gribFile].append(url)
    
    dataDict = {}

    # A list of all Download urls.
    dataDict['files'] = runDict
    self.runTime = runTime

    dataDict = {self.name: dataDict}

    return dataDict

  '''''
  Gets forecast hour from a filename, given a model.
  '''''
  def getForecastHour(self, fileName, noPrefix = False):
    forecastHour = ""
    prefix = "f"

    if noPrefix:
      prefix = ""

    # for 20150422120192.grib2 -> forecastHour = "192"
    forecastHour = prefix + fileName.split('.')[0][-3:]

    return forecastHour
    
  def getLastForecastHour(self):
    return self.lastForecastHour