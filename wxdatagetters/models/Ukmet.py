from NonNCEPModel import NonNCEPModel

class Ukmet(NonNCEPModel):

  def __init__(self):
    # super(NonNCEPModel, self).__init__()
    NonNCEPModel.__init__(self)
    self.lastForecastHour = "240"
    self.name = "ukmet"
    self.modelAlias = "ukmet"
    self.runTime = ''
    self.defaultTimes = ['000','024','048','072','096','120','144','168','240']
    self.modelTimes = []
    self.modelUrl = ''
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