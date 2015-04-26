from dataProcessor import DataProcessor
from gempak import Gempak
import ConfigParser
import os

class DataGetter:

  def __init__(self, model):
    # Connect
    self.model = model
    return

  def run(self):

    modelClass = self.getModelObj(args.model)
    modelLinks = modelClass.getRun()

    # initalize for only one model.
    dataGetter = DataProcessor(modelClass) # Second parameter enables DEBUG mode.
    dataGetter.getData(modelLinks)

    gempak = Gempak(dataGetter)
    gempak.doThreadedGempakScripts(modelLinks)

    if dataGetter.isUpdated():
      # Scrub only model dir used. Only if run is complete.
      if dataGetter.isComplete():
        dataGetter.scrubTreeData(dataGetter.constants.dataDirEnv + "/" + self.model)
        # Model is complete. Reset updating flag to 0;
        dataGetter.setUpdatingFlag(self.model, 0)
        # Clear accumulation data.
        # dataGetter.clearNpyDat(self.model)
      dataGetter.transferFilesToProd(self.model)

    dataGetter.closeConnection()
    
    return

  def getModelObj(self, model):
    model = model.capitalize() # Capitalize for classname.
    import_module_ = "models." + model
    model_class = model
    module = __import__(import_module_, fromlist = [model])
    try:
      class_ = getattr(module, model_class)()
    except AttributeError:
      print 'Class does not exist'
    return class_
