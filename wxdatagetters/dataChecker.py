from objects.constants import Constants
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

  modelClass = getModelObj(model)
  modelLinks = modelClass.getRun()
  constants  = Constants()  

  db = NgwipsDB(constants.dbConnStr)
  redisConn = redis.Redis(constants.redisHost)
  beanstalkdConn = beanstalkc.Connection(host=constants.beanstalkdHost, port=11300)

  resetHourKeys(modelClass, model, redisConn)
  # redisConn.set(model + '-complete', db.getCurrentRun(model))

  currentlyProcessing = redisConn.get(model)

  # If key is not set in Redis... Set it.
  if currentlyProcessing is None:
    redisConn.set(model, "0")

  print "Currently Processing: " + currentlyProcessing

  while True:
    modelClass = getModelObj(model)
    modelLinks = modelClass.getRun()
    currentlyProcessing = redisConn.get(model)
      
    print "Currently Processing: " + currentlyProcessing
    if int(currentlyProcessing) == 0:
      # If it has new hourly data, or it is a new run altogether. Put it in the Queue.
      if hasNewData(modelLinks, model, modelClass,redisConn) or db.isNewRun(model, modelClass.runTime):
        # Run has been updated. Put into queue.
        print "Putting into Queue..."
        # Set Currently processing 
        # 1 = Currently processing
        # 0 = Not currently processing
        redisConn.set(model, "1")
        print "Currently processing : " + redisConn.get(model)
        cmd = "python dataGetter.py -b --model=" + model + " --clean"
        cmdObj = {"model": model, "command": cmd}
        beanstalkdConn.put(json.dumps(cmdObj))

    print "doing nothing... Waiting 5 mins."
    # Sleep for 3 mins.
    time.sleep(180)
  

  return

def resetHourKeys(modelClass, model, redisConn):
  hourKeys = modelClass.getDefaultHours()
  for hour in hourKeys:
    redisConn.set(model + '-' + hour, "0")
  return

def hasNewData(modelLinks, model, modelClass, redisConn):

  http  = modelLinks[model]
  if not http:
    return False
  if 'files' in http:
    files = http['files']
    for file,url in files.items():
      fHour = modelClass.getForecastHour(file, True)
      redisHourKey = redisConn.get(model + '-' + fHour)
      if redisHourKey == "0":
        return True

  return False

def getModelObj(model):
  model = model.capitalize() # Capitalize for classname.
  import_module_ = "models." + model
  model_class = model
  module = __import__(import_module_, fromlist = [model])
  try:
    class_ = getattr(module, model_class)()
  except AttributeError:
    print 'Class does not exist'
  return class_


if __name__ == "__main__":
  main()
