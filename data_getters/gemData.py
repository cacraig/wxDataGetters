import urllib2
import time
from constants import Constants

# Get all of our constants for the data getting script.

class GemData:

  def __init__(self):

    self.constants = Constants()
    return

  def getData(self):

    for key,http in self.constants.modelGems.items():

      # If it is empty for any reason, skip!
      if not http:
        print "Skipping: " + key + "..."
        continue

      if 'files' in http:
        # download all files in http['files'].
        print "PROCESSING MANY"
        files = http['files']

        for file,url in files.items():
          savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/' + file
          print "downloading " + savePath
          gemFile = urllib2.urlopen(url).read()
          fp = open(savePath, 'w')
          fp.write(gemFile)
          fp.close()

      else:
        savePath =  self.constants.baseDir + self.constants.gempakDir + self.constants.dataDir + key + '/' + http['file']

        try:
          print "Saving: " + http['url'] + " to " + savePath
          gemFile = urllib2.urlopen(http['url']).read()
          fp = open(savePath, 'w')
          fp.write(gemFile)
          fp.close()

        except Exception, e:
          print "Could not get Model *.gem " + http['file'] + " with url: " + http['url']
          print " with exception %s" % e
          pass

    return