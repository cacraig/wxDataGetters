import urllib2
import socket, threading, os

'''''
Handles downloading subsets of grib2 files.
With this class you can do a once over scan of grib2 files via idx files.
You can then retrieve specific byte-ranges with the HTTP/1.1 range header.
Good if you only want certain parameters.

See: http://www.cpc.ncep.noaa.gov/products/wesley/fast_downloading_grib.html
'''''
class GribInventory:
  # curl specs.
  # -r, --range <range>
  #        (HTTP/FTP/SFTP/FILE) Retrieve a byte range (i.e a partial document) from a HTTP/1.1, FTP or SFTP server
  #        or a local FILE. Ranges can be specified in a number of ways.

  #        0-499     specifies the first 500 bytes

  #        500-999   specifies the second 500 bytes

  #        -500      specifies the last 500 bytes

  #        9500-     specifies the bytes from offset 9500 and forward

  #        0-0,-1    specifies the first and last byte only(*)(H)

  #        500-700,600-799
  #                  specifies 300 bytes from offset 500(H)

  #        100-199,500-599
  #                  specifies two separate 100-byte ranges(*)(H)

  '''''
  function __init__
  @param Model modelClass - Instance of NCEPModel.
  @param list  files      - List of grib2 files.
  @return void
  '''''
  def __init__(self, modelClass, files):
    # { ..., fileName: '100-200,500-600,800-1100,...', ...}
    self.byteRanges = {}
    # Instance of NCEPModel.
    self.model = modelClass
    self.parseIdxFiles(files)
    return
  
  '''''
  public function getByteRanges

  Given a file, get the list of byte range tuples for the variables desired.
  @param String idxFile - *.idx file with byte ranges for variables.
  @param Integer contentLength - Size of grib2 file to subset (in bytes)
  @return list of tuples : [(low,high), (low,high), ...]
  '''''
  def getByteRanges(self, idxFile, contentLength):
    # Read through each line... if a desired variable is found,
    # record the byte address. Then, read the next line. If the next line does
    # not contain a desired byte address, then add the (low, high) tuple to list.
    # If it does contain a desired variable, continue until a non-desired var is found.
    # After finding non-desired, get byte address and add (low, high) tuple to list.

    # Example:
    # DesiredVars = ['MSLET:mean sea level', 'ABSV:250 mb','ABSV:500 mb']
    # 
    # 1:0:d=2015042500:MSLET:mean sea level:45 hour fcst:       <-- Start
    # 2:134566:d=2015042500:PRMSL:mean sea level:45 hour fcst:  <-- Stop --> (0,134566)
    # 3:278805:d=2015042500:VIS:surface:45 hour fcst:
    # 4:332575:d=2015042500:ABSV:250 mb:45 hour fcst:           <-- Start
    # 5:377094:d=2015042500:ABSV:500 mb:45 hour fcst:
    # 6:443545:d=2015042500:ABSV:700 mb:45 hour fcst:           <-- Stop --> (332575,443545)
    # 7:512643:d=2015042500:ABSV:850 mb:45 hour fcst:
    # 8:588624:d=2015042500:ABSV:1000 mb:45 hour fcst:
    # 9:671392:d=2015042500:PRES:surface:45 hour fcst:
    # 10:861566:d=2015042500:HGT:surface:45 hour fcst:
    #
    # Output = [(0,134566), (332575,443545)]
    
    data = urllib2.urlopen(self.model.getDataUrl() + idxFile)
    byteRanges = []
    byteStart = 0
    varFound = False
    for line in data: # files are iterable
      parts     = line.split(':')
      varName   = parts[3] + ':' + parts[4]
      bytePoint = parts[1]
      if varName in self.model.gribVars and not varFound:
        byteStart = bytePoint
        varFound = True

      if varName not in self.model.gribVars and varFound:
        byteEnd = bytePoint
        byteRanges.append((byteStart,byteEnd))
        varFound = False

    # If the last line of file contains a desired 
    # set the last range = (start, ContentLength)
    if varFound:
      byteRanges.append((byteStart,contentLength))

    return byteRanges # [(low,high), (low,high), ...]

  '''''
  public function parseIdxFiles(files)

  Parses *.idx file for the given grib2 file, 
  and gets all of the byte ranges for each file.
  Sets public byteRanges.

  @param files - list of grib2 files.
  @return void
  '''''
  def parseIdxFiles(self, files):
    # For each file set self.byteRanges[file] = getByteRanges(file, idxFile).
    for gribFile in files:
      idxFile = gribFile + '.idx'
      # Get the content length of grib2 file
      fmeta = urllib2.urlopen(self.model.getDataUrl() + gribFile).info()
      contentLength = fmeta.getheaders("Content-Length")[0]
      self.byteRanges[gribFile] = self.getByteRanges(idxFile, contentLength)
    return

  '''''
  public function getByteRangesAsString
  Takes class member's list of byte ranges and turns them into a comma-separated
  string safe to be passed as a HTTP-1.1 range header.
  @param String gribFile
  @return String
  '''''
  def getByteRangesAsString(self, gribFile):
    byteStrList = []
    for byteTuple in self.byteRanges[gribFile]:
      byteRangeStr = str(byteTuple[0]) + "-" + str(byteTuple[1])
      byteStrList.append(byteRangeStr)
    return ",".join(byteStrList)

  '''''
  public function downloadFilteredFile

  Downloads a filtered grib2 file. Not Threadable, as socket timeouts will go unnoticed.

  @param String fileName  - Name of the file to download.
  @param String saveFile full savepath and filename to download to.
  @return boolean
  '''''
  def downloadFilteredFile(self, fileName, saveFile):
    byteRangeStr = self.getByteRangesAsString(fileName)
    req = urllib2.Request(self.model.getDataUrl() + fileName)
    req.headers['Range']='bytes=' + byteRangeStr

    f = urllib2.urlopen(req).read()
    fp = open(saveFile, 'w')
    fp.write(f)
    fp.close()
    return
  
  '''''
  public function downloadFilteredThread

  Represent's a Thread for downloading a filtered grib2 file.
  Bubbles up socket timeout error, and returns false if an error occurred.

  @param fileName String - Name of the file to download.
  @param saveFile full savepath and filename to download to.
  @return boolean
  '''''
  def downloadFilteredThread(self, fileName, saveFile):
    byteRangeStr = self.getByteRangesAsString(fileName)
    req = urllib2.Request(self.model.getDataUrl() + fileName)
    req.headers['Range']='bytes=' + byteRangeStr

    maxSocketTime = 300 # Max time a download read() can take.

    gribFileBlob = urllib2.urlopen(req)
    success,gribFileBlob = self.timeoutHttpRead(gribFileBlob, maxSocketTime)

    if success and gribFileBlob is not None:
      fp = open(saveFile, 'w')
      fp.write(gribFileBlob)
      fp.close()
    else:
      print "Socket timed out! Time exceeded "
      f = open(self.model.errorLog,'w')
      f.write("\n A socket Timed out in GemData.saveFilesThread() . We must exit this program execution, and attempt again.")
      f.write("\n URL: " + self.model.getDataUrl() + fileName)
      f.write("\n MODEL: " + self.model.model)
      f.close()
      # Exit call. Give up, get the hell out!
      return False
    return True

  '''''
  private function timeoutHttpRead(response, timeout=60)

  Time out function for Threads.

  @param object response
  @param int timeout
  @return Tuple
  '''''
  def timeoutHttpRead(self, response, timeout = 60):
    def murha(resp):
      try:
        os.close(resp.fileno())
        resp.close()
      except Exception, e:
        print e
        return (False, None)

    # set a timer to yank the carpet underneath the blocking read() by closing the os file descriptor
    t = threading.Timer(timeout, murha, (response,))
    try:
      t.start()
      body = response.read()
      t.cancel()
    except socket.error as se:
      if se.errno == errno.EBADF: # murha happened
        return (False, None)
      raise
    return (True, body)