from gemData import GemData
from gempak import Gempak
import ConfigParser

class DataGetter:

  def __init__(self, model):
    # Connect
    self.model = model
    return

  def run(self):
    dataGetter = GemData(self.model)
    dataGetter.getData()
    gempak = Gempak(dataGetter)
    gempak.doThreadedGempakScripts()
    if dataGetter.isUpdated():
      # Scrub only model dir used. Only if run is complete.
      if dataGetter.isComplete():
        dataGetter.scrubTreeData(dataGetter.constants.dataDirEnv + "/" + self.model)
        # Model is complete. Reset updating flag to 0;
        dataGetter.setUpdatingFlag(self.model, 0)

      dataGetter.transferFilesToProd(self.model)
    return
