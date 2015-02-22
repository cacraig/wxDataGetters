from constants import Constants
from optparse import OptionParser
from argparse import ArgumentParser
from libs.db import NgwipsDB
import redis
import beanstalkc
import time
import json

def main():
  parser = ArgumentParser()

  parser.add_argument("-m", "--model", required=True,
                help="Check this model")

  args = parser.parse_args()
  model = args.model

  constants = Constants(model)

  db = NgwipsDB(constants.dbConnStr)
  redisConn = redis.Redis(constants.redisHost)
  beanstalkdConn = beanstalkc.Connection(host=constants.beanstalkdHost, port=11300)

  resetHourKeys(constants, model)

  while True:
    constants = Constants(model)
    currentlyProcessing = redisConn.get(model)
    print "Currently Processing: " + currentlyProcessing

    # If key is not set in Redis... Set it.
    if currentlyProcessing is None:
      redisConn.set(model, "0")

    if currentlyProcessing != "1":
      if hasNewData(constants, model):
        # Run has been updated. Put into queue.
        print "Putting into Queue..."
        # Set Currently processing 
        # 1 = Currently processing
        # 0 = Not currently processing
        redisConn.set(model, "1")
        cmd = "python dataGetter.py -b --model=" + model + " --clean"
        cmdObj = {"model": model, "command": cmd}
        beanstalkdConn.put(json.dumps(cmdObj))

    print "doing nothing... Waiting 5 mins."
    # Sleep for 5 mins.
    time.sleep(300)
  

  return

def resetHourKeys(constants, model):
  hourKeys = constants.getDefaultHoursByModel(model)
  for hour in hourKeys:
    self.redisConn.set(model + '-' + hour, "0")
  return

def hasNewData(self, constants, model):
  for model,http in constants.modelGems.items():
    if not http:
      return False
  if 'files' in http:
    files = http['files']
    for file,url in files.items():
      fHour = getForecastHour(model, file, True)
      redisHourKey = self.redisConn.get(model + '-' + hour)
      if redisHourKey == "0":
        return True

  return False

def getForecastHour(model, fileName, noPrefix = False):
  forecastHour = ""
  prefix = "f"

  if noPrefix:
    prefix = ""

  if model == 'gfs':
    # for gfs.t18z.pgrb2full.0p50.f006 -> forecastHour = "006"
    forecastHour = prefix + fileName.split('.')[4][1:4]
  elif model == 'nam':
    # for nam.t18z.awip3281.tm00.grib2 -> forecastHour = "081"
    forecastHour = prefix + "0" + fileName.split('.')[2][6:8]
  elif model == 'nam4km':
    # for nam.t06z.blahblah.hiresf07.blah -> forecastHour = "007"
    forecastHour = prefix + "0" + fileName.split('.')[3][6:8]

  return forecastHour

if __name__ == "__main__":
  main()