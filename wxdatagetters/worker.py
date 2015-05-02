import beanstalkc
import time
from subprocess import call
import ConfigParser
import json
import redis
from dataGetterModule import DataGetter
import os

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

  print "Spinning our client..."

  while True:
    # To receive a job:
    job = beanstalkdConn.reserve()
    # Work with the job:
    print "Doing job:: " + job.body
    cmdObj = json.loads(job.body)
    print "Currently Processing:  " +  redisConn.get(cmdObj['model'])
    dataGetter = DataGetter(cmdObj['model'])
    job.delete()
    # If this throws an Exception ...like socket timed out or w/e.
    # Reset updating flag, and allow job to spawn again.
    wd = os.getcwd()
    try:
      dataGetter.run()
      print "Releasing LOCK!"
      redisConn.set(cmdObj['model'], "0")
      dataGetter = None
    except Exception, e:
      print e
      print os.getcwd()
      # assert we are in the appropriate dir.
      os.chdir(wd)
      redisConn.set(cmdObj['model'], "0")
      print "Releasing LOCK!"
      dataGetter = None

  # Delete the job: 
  job.delete()

  return

if __name__ == "__main__":
  main()
