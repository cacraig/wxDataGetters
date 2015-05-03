from NonNCEPModel import NonNCEPModel

class Ukmet(NonNCEPModel):

  def __init__(self):
    '''''
    The UKMET model is strange because hours 0-72 must be downloaded (*.gem Decoded only) from COD Motherlode, and 96-120 from NOAA-NCEP (grib2 only).

    This makes coming up with a standard paradigm very difficult. Ugh. I'll do this one at a later date.
    '''''
    # super(NonNCEPModel, self).__init__()
    NonNCEPModel.__init__(self)
    self.lastForecastHour = "120"
    self.name = "ukmet"
    self.modelAlias = "ukmet"
    self.runTime = ''
    self.defaultTimes = ['000','006','012','018','024','030','036','042','048','054','060','066','072','096','120']
    self.modelTimes = []
    # --user=unidata --password=lotzodata
    self.modelUrl = 'ftp://motherlode.ucar.edu/decoded/gempak/model/ukmet/' # or http://metfs1.agron.iastate.edu/data/gempak/model/ukmet/
    return

  '''''
  Returns model files grouped by forecast hour filename (grib2).
  '''''
  def getRun(self):
    return { self.name : {} }

  '''''
  Gets forecast hour from a filename, given a model.
  '''''
  def getForecastHour(self, fileName, noPrefix = False):
    forecastHour = ""
    prefix = "f"

    return forecastHour
    
  def getLastForecastHour(self):
    return self.lastForecastHour