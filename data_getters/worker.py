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

  print "Spinning our client..."

  while True:
    # To receive a job:
    job = beanstalkdConn.reserve(timeout=None)
    # Work with the job:
    print "Doing job:: " + job.body
    cmdObj = json.loads(job.body)
    dataGetter = DataGetter(cmdObj['model'])
    dataGetter.run()

    #call(cmdObj['command'], shell=True)
    redisConn.set(cmdObj['model'], "0")
    job.delete()

  # Delete the job: 
  job.delete()

  return

if __name__ == "__main__":
  main()
