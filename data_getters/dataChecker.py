from constants import Constants
from optparse import OptionParser
from argparse import ArgumentParser
from libs.db import NgwipsDB
import redis
import beanstalkc
import time

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

  currentlyProcessing = redisConn.get(model)

  print "Currently Processing: " + currentlyProcessing
  while True:
    if currentlyProcessing != "1":
      if db.isNewRun(model, constants.runTimes[model]):
        # Run has been updated. Put into queue.
        print "Putting into Queue..."
        # Set Currently processing 
        # 1 = Currently processing
        # 0 = Not currently processing
        redisConn.set(model, "1")
        beanstalkdConn.put("python dataGetter.py -b --model=" + model + " --clean")
        return

    print "doing nothing... Waiting 5 mins."
    # Sleep for 5 mins.
    time.sleep(300)
  

  return

if __name__ == "__main__":
  main()