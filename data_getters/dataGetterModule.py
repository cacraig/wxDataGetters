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
    gempak.runGempakScripts()
    if dataGetter.isUpdated():
      dataGetter.scrubTreeData(dataGetter.constants.dataDirEnv)
      dataGetter.transferFilesToProd(self.model)
    return
