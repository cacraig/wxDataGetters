import os

class BatchGenerateImages:
  def __init__(self, dataGetter):
    self.constants = dataGetter.constants
    return

  def getCommand(self):
    cmd = "perl scripts/gempak.pl " + self.constants.dataDirEnv + " "
    for key,http in self.constants.modelGems.items():
      fileArgString = key + "=" + http['file']
      cmd += fileArgString + " "
    return cmd
