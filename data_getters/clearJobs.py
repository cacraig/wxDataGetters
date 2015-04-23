import beanstalkc
import time
from subprocess import call
import ConfigParser
import json
import redis
from dataGetterModule import DataGetter

def main():

  # Open our parameters.ini file, and get defined constants.
  config = ConfigParser.SafeConfigParser()
  config.read('conf/parameters.ini')

  # Hosts.
  beanstalkdHost = config.get('DEFAULT', 'BEANSTALKD_HOST')
  redisHost = config.get('DEFAULT', 'REDIS_HOST')

  redisConn = redis.Redis(redisHost)
  beanstalkdConn = beanstalkc.Connection(host=beanstalkdHost, port=11300)

  # Switch to the default (tube):
  beanstalkdConn.use('default')

  while beanstalkdConn.peek_ready() is not None:
    job = beanstalkdConn.reserve(timeout=None)
    cmdObj = json.loads(job.body)
    print "Clearing Job: " + job.body
    job.delete()
    redisConn.set(cmdObj['model'], "0")

  modelCache = ['nam','gfs','nam4km','ruc','ecmwf','ukmet']

  # reset cache  
  for model in modelCache:
     print "Re-Setting model-cache: " + model
     redisConn.set(model, "0")

  print "Done clearing jobs."

  return

if __name__ == "__main__":
  main()
