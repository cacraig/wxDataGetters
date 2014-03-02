import os

class BatchGenerateImages:
  def __init__(self, dataGetter):
    self.dataGetter = dataGetter
    return

  def getCommand(self):
    cmd = "perl scripts/gempak.pl " + self.dataGetter.constants.dataDirEnv + " "
    for key,http in self.dataGetter.constants.modelGems.items():
      fileArgString = key + "=" + http['file']
      cmd += fileArgString + " "
    return cmd
