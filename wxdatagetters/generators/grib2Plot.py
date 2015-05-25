import matplotlib
matplotlib.use('agg')

import pygrib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid,cm
import numpy as np
from pylab import rcParams
import pylab as pyl
from matplotlib.colors import LinearSegmentedColormap
from objects import coltbls
from objects.gribMap import GribMap
from subprocess import call, STDOUT
import concurrent.futures
import os
import gc
import multiprocessing as mp
from objects.asyncPool import AsyncPool

# See: /home/vagrant/GEMPAK7/gempak/tables/stns/geog.tbl 
# !------------------------------------------------------------------------------
# !G      GEOG NAME           CENLAT  CENLON   LLLAT   LLLON   URLAT   URLON PROJ
# !(8)    (18)              (8)     (8)     (8)     (8)     (8)     (8)      (30)
# !------------------------------------------------------------------------------
# NC      NORTH CAROLINA       35.50  -79.25   30.00  -87.25   41.00  -71.25 NPS
# WA      WASHINGTON           47.25 -120.00   41.75 -128.00   52.75 -112.00 NPS
# WWE     WINTER WX AREA       36.00  -78.00   18.00 -106.00   54.00  -50.00 NPS (LABELED EASTUS)
# OK      OKLAHOMA             35.75  -97.25   30.25 -105.25   41.25  -89.25 NPS
# MA      MASSACHUSETTS        42.25  -72.25   36.75  -80.25   47.75  -64.25 NPS (LABELED NEUS)
# CENTUS  CENTRAL US           36.15  -91.20   24.70 -105.40   47.60  -77.00 STR/90;-95;0
# TATL    TROPICAL ATLANTIC    15.00  -50.00  -10.00  -90.00   35.00  -15.00 MER
# EPAC    E PACIFIC            40.00 -130.60   12.00 -134.00   75.00 -110.00 STR/90;-100;1
# CHIFA   CHICAGO FA AREA      42.00  -93.00   34.00 -108.00   50.00  -75.00 LCC
# CA      CALIFORNIA           37.00 -119.75   31.50 -127.75   42.50 -111.75 NPS
# WSIG    PACIFIC              38.00 -160.00   18.00  155.00   58.00 -115.00 CED

# setup north polar stereographic basemap.
# The longitude lon_0 is at 6-o'clock, and the
# latitude circle boundinglat is tangent to the edge
# of the map at lon_0. Default value of lat_ts
# (latitude of true scale) is pole.

class Grib2Plot:

  '''''
  Intialize the grib2Plot class with everything we need!

  @return void
  '''''
  def __init__(self, constants, model):

    self.regionMaps = {
      #                              CENLAT  CENLON   LLLAT   LLLON   URLAT   URLON PROJ
      # NC      NORTH CAROLINA       35.50  -79.25   30.00  -87.25   41.00  -71.25  laea
      "CONUS": GribMap(llcrnrlat=19,urcrnrlat=50,\
                       llcrnrlon=-119,urcrnrlon=-56, \
                       resolution='l',projection="stere",\
                       lat_ts=50,lat_0=90,lon_0=-100., fix_aspect=False, \
                       borderX=61., borderY=40.), \
      "CENTUS" : GribMap(llcrnrlat=24.70,urcrnrlat=47.60,\
                       llcrnrlon=-105.40,urcrnrlon=-77.00, \
                       resolution='l',projection="lcc",\
                       lat_ts=20,lat_0=36.15,lon_0=-91.20, lat_1=36.15, fix_aspect=False, \
                       borderX=127.), \
      # # CHIFA   CHICAGO FA AREA      42.00  -93.00   34.00 -108.00   50.00  -75.00 LCC
      "CHIFA" : GribMap(llcrnrlat=34.00,urcrnrlat=50.00,\
                 llcrnrlon=-108.00,urcrnrlon=-75.00, \
                 resolution='l',projection="laea",\
                 lat_ts=20,lat_0=42.00,lon_0=-93.00, fix_aspect=False, \
                 borderY=76., hasDoubleYBorder=True), \
      "NEUS" : GribMap(llcrnrlat=42.25,urcrnrlat=47.75,\
                       llcrnrlon=-80.25,urcrnrlon=-64.25, \
                       resolution='l',projection="laea",\
                       lat_ts=20,lat_0=42.25,lon_0=-72.25, fix_aspect=False, \
                       borderX=91.), \
      # CUSTOM: 30; -85; 18.00;-92.00;54.00;-40.00
      "EASTUS" : GribMap(llcrnrlat=18.00,urcrnrlat=54.00,\
                       llcrnrlon=-92.00,urcrnrlon=-40.00, \
                       resolution='l',projection="lcc",\
                       lat_ts=50,lat_0=30.00,lon_0=-85.00, lat_1=30.00, fix_aspect=False, \
                       borderX=213.), \
      "NC" : GribMap(llcrnrlat=30.00,urcrnrlat=41.00,\
                     llcrnrlon=-87.25,urcrnrlon=-71.25, \
                     resolution='l',projection="laea",\
                     lat_ts=20,lat_0=36.00,lon_0=-78.00, fix_aspect=False, \
                     borderX=35.), \
      "WA" : GribMap(llcrnrlat=41.75,urcrnrlat=52.75,\
                     llcrnrlon=-128.00,urcrnrlon=-112.00, \
                     resolution='l',projection="laea",\
                     lat_ts=50,lat_0=47.25,lon_0=-120.00, fix_aspect=False, \
                     borderX=135.), \
      "OK" : GribMap(llcrnrlat=30.25,urcrnrlat=41.25,\
                     llcrnrlon=-105.25,urcrnrlon=-89.25, \
                     resolution='l',projection="laea",\
                     lat_ts=50,lat_0=35.75,lon_0=-97.25, fix_aspect=False, \
                     borderX=37.), \
      "CA" : GribMap(llcrnrlat=31.50,urcrnrlat=42.50,\
                     llcrnrlon= -127.75,urcrnrlon=-111.75, \
                     resolution='l',projection="laea",\
                     lat_ts=50,lat_0=37.00,lon_0= -119.75, fix_aspect=False, \
                     borderX=45.) \
    }

    self.nonLAEAprojections = ['CENTUS', 'CONUS','EASTUS']
    self.globalModelGrids = ['gfs']
    self.borderPadding = {}
    self.constants = constants
    self.isPng = ['CONUS']
    self.snowSum = None
    self.snowSum12 = None
    self.snowSum24 = None
    self.snowSum72 = None
    self.snowSum120 = None

    # Run state
    self.runTime = model.runTime
    self.times = model.modelTimes
    self.modelDataPath = constants.dataDirEnv
    self.model = model.getName()
    self.gribVars = ['swem','500mbT', '2mT','precip','850mbT']
    # Cache for all loaded grib data.
    self.cache = {}
    self.preloadData()

    return

  # Preloads all data.
  # times to preload can be overridden.
  def preloadData(self, times = None):

    if not times:
      times = self.times

    for time in times:
      skip = False

      if time not in self.cache:
        self.cache[time] = {}

      g2file = self.getGrib2File(self.modelDataPath, self.runTime, self.model, time)

      for var in self.gribVars:
        if var not in self.cache[time]:
          self.cache[time][var] = None
        else:
          skip = True
      # Skip preloading if already loaded.


      print "LOADING TIME: " + time

      try:
        grbs=pygrib.open(g2file)
        grbs.seek(0)
      except Exception, e:
        print "Failure on loading grib file = " + g2file
        continue
        pass

      if skip:
        print "Skipping: " + time + " -> Already loaded or not found."
        continue

      try:
        self.cache[time]['swem'] = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]
      except Exception, e:
        print e
        pass

      try:
        self.cache[time]['500mbT'] = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=500)[0]
      except Exception, e:
        print e
        pass

      try:
        self.cache[time]['850mbT'] = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=850)[0]
      except Exception, e:
        print e
        pass

      try:
        self.cache[time]['2mT'] = grbs.select(name='2 metre temperature', typeOfLevel='heightAboveGround', level=2)[0]
      except Exception, e:
        print e
        pass

      try:
        self.cache[time]['precip'] = grbs.select(name='Total Precipitation', level=0)[0]
      except Exception, e:
        print e
        pass

      if grbs is not None:
        grbs.close()
        
    return

  # Wraps plot2mTemp in it's own process. Isolates any possible memory leaks.
  def plot2mMPTemp(self, model, times, runTime, modelDataPath):
    ap = AsyncPool(6)
    for time in times:
      ap.doJob(self.plot2mTempMP,(model, time, runTime, modelDataPath))
    ap.join()
    return

  # Wraps doSnowPlot in it's own process. Isolates any possible memory leaks.
  # Executes two processes at a time, and waits for processes to finish before continueing.
  # This gives a little concurrency, and assures memory is released.
  # as opposed to using a Pool (Where processes are kept alive until pool is closed.)
  def doPlotMP(self, method, argList, maxWorkers = 2):

    '''''
    Do AT MOST two processes, two at a time. Otherwise do 1 process, one at a time.
    '''''

    # Make sure that maxWorkers <= 2.
    if maxWorkers > 2:
      raise ValueError('Only max two workers allowed for doPlotMP. Pass 1 or 2 for maxWorkers param.')

    for i in xrange(0,len(argList),maxWorkers):
      # Process 1.
      try:
        args = argList[i]
        p = mp.Process(target=method, args=args)
        p.start()
      except Exception, e:
        print e
        pass

      # Process 2.
      if maxWorkers > 1:
        try:
          args2 = argList[i+1]
          p2 = mp.Process(target=method, args=args2)
          p2.start()
        except Exception, e:
          print e
          pass
      
      # Join Process 1.
      try:
        p.join()
      except Exception, e:
        pass

      # Join Process 2.
      if maxWorkers > 1:
        try:
          p2.join()
        except Exception, e:
          pass

    return

  # Wraps doSnowPlot in it's own process. Isolates any possible memory leaks.
  def doSnowPlotAccumMP(self, runTime, region, model, times, gribmap, modelDataPath ,previousTime):
    args = (runTime, region, model, times, gribmap, modelDataPath ,previousTime)
    p = mp.Process(target=self.doSnowAccumulations, args=args)
    p.start()
    p.join()
    return

  def plot2mTempMP(self, zargs):
    (model, time, runTime, modelDataPath) = zargs

    level = "sfc"
    variable = "tmpf"
    baseDir = "data"
    imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable
    call("mkdir -p " + imgDir, shell=True)

    borderBottomCmd = '' # Reset any bottom border.

    #g2File = self.getGrib2File(modelDataPath, runTime, model, time)

    # Get grib2 data.
    gTemp2m = self.cache[time]['2mT']

    if gTemp2m is None:
      return


    for region, gribmap in self.regionMaps.items():
      fig, borderWidth, borderBottom = self.getRegionFigure(gribmap)
      m = gribmap.getBaseMap()
      print time

      convertExtension = ".gif"
      if region in self.isPng:
        convertExtension = ".png"

      tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
      saveFileName = imgDir + "/" + region +"_f" + time + convertExtension

      temp2m = gTemp2m.values
      grbs = None

      # Convert Kelvin to (F)
      temp2m = ((temp2m- 273.15)* 1.8000) + 32.00

      lat, lon = gTemp2m.latlons()

      if borderBottom > 1.0:
        if gribmap.hasDoubleYBorder:
          borderBottomCmd = " -bordercolor none -border 0x" + str(int(borderBottom))
        else:
          borderBottomCmd = " -gravity south -splice 0x" + str(int(borderBottom))

      #if model == "gfs" and region is not "CONUS":
        # GFS model (and some others) come with (0 - 360) Longitudes.
        # This must be converted to (-180 - 180) when using Mercator.
      #  lon = self.convertLon360to180(lon, temp2m)
      
      # TURNING OFF MESHGRID FOR GFS FOR NOW. DAMN SHAPE BUG yo.
      # if model == 'gfs'and region != 'merc':
      #   x = np.arange(-180, 180.5, 1.0).reshape((361,720))
      #   y = np.arange(-90, 91, 1.0).reshape((361,720))
      #   x,y = np.meshgrid(x,y)
      #   x,y = m(x,y)
      # else:
      x,y = m(lon,lat)
      ax = fig.add_axes([1,1,1,1], axisbg='k') # This needs to be here or else the figsize*DPI calc will not work!
                                               # I have no idea why. Just a Matplotlib quirk I guess.

      colorMap = coltbls.sftemp()

      # TURNING OFF MESHGRID FOR GFS FOR NOW. DAMN SHAPE BUG yo.
      if region == 'CONUS' and model != 'gfs':
        cs = m.pcolormesh(x, y, temp2m, cmap=colorMap, vmin=-25, vmax=115)
      else:
        CLEVELS= [(c*5)-25 for c in range(29)]
        cs = m.contourf(x,y,temp2m,CLEVELS,cmap=colorMap, vmin=-25, vmax=115)

      # m.drawcoastlines()
      m.drawmapboundary()
      # Overlay 32 degree isotherm
      cc = m.contour(x,y,temp2m, [32], cmap=plt.cm.winter, vmin=32, vmax=32)

      # m.drawstates()
      # m.drawcountries()
      # m.drawcoastlines()
      # m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0]) # 19.00;-119.00;50.00;-56.00
      # m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])

      # FOR SETTING COLOR BARS!!!!!
      # cb = plt.colorbar(cs, orientation='vertical', ticks=[(c*10)-25 for c in range(29)])
      # axes_obj = plt.getp(ax,'axes')                        #get the axes' property handler
      # plt.setp(plt.getp(axes_obj, 'yticklabels'), color='w') #set yticklabels color
      # plt.setp(plt.getp(axes_obj, 'xticklabels'), color='w') #set xticklabels color
      # plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='w') # set colorbar  
      # cb.ax.yaxis.set_tick_params(color='w')      #set colorbar ticks color 
      # fig.set_facecolor('black')
      # cb.outline.set_edgecolor('white')
      # END COLORBARS
      
      # PNG optimization
      # pngquant -o lossy.png --force --quality=70-80 input.png
      # optipng -o1 -strip all -out out.png -clobber input.png

      #print "convert -background none "+ tempFileName + " " + borderBottomCmd + " -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName

      #print "pngquant -o "+ os.getcwd()+ "/" + tempFileName + " --force --quality=70-80 "+ os.getcwd()+ "/" + tempFileName
      fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor())


      call("pngquant -o "+ tempFileName + " --force --quality=50-65 "+ tempFileName, shell=True)
      #call("optipng -o2 -strip all -out " + tempFileName + " -clobber " + tempFileName, shell=True)
      call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
      call("rm " + tempFileName, shell=True)
      cc = None
      cs = None
      fig.clf()
      plt.clf()
      gc.collect()


    return ""

  def plotSnowFall(self, model, times, runTime, modelDataPath, previousTime):
    accumArgList = []
    hourArgList = []
    snowPrevTime = previousTime
    # args for accumulations.
    for region,gribmap in self.regionMaps.items():
      accumArgList.append((runTime, region, model, times, gribmap, modelDataPath ,previousTime))

    for time in times:
      hourArgList.append((runTime, model, time, modelDataPath ,snowPrevTime))
      snowPrevTime = time

    maxWorkers = 2
    
    # The GFS model run is big, and has lots of files.
    # Matplotlib will flip out and suck up memory, so only allow one process at a time.
    if model == 'gfs':
      maxWorkers = 1

    ap = AsyncPool(6)

    try:
      # Do multiprocessing -> snow plots.
      #self.doPlotMP(self.doSnowPlot, hourArgList, maxWorkers)
      for time in times:
        ap.doJob(self.doSnowPlot,(runTime, model, time, modelDataPath ,snowPrevTime))
        snowPrevTime = time
      ap.join()
    except Exception, e:
      print e
      pass

    try:
      # Do multiprocessing -> snowfall accumulations.
      self.doPlotMP(self.doSnowAccumulations, accumArgList, maxWorkers)
    except Exception, e:
      print e
      pass
    return

  def plotPrecip(self, model, times, runTime, modelDataPath):

    argList = []
    # nam.t18z.awip3281.tm00.grib2
    for region,gribmap in self.regionMaps.items():
      argList.append((runTime, region, model, times, gribmap, modelDataPath))

    maxWorkers = 2
    
    # The GFS model run is big, and has lots of files.
    # Matplotlib will flip out and suck up memory, so only allow one process at a time.
    if model == 'gfs':
      maxWorkers = 1

    try:
      # Do multiprocessing -> snowfall accumulations.
      self.doPlotMP(self.doAccumPrecipPlotMP, argList, maxWorkers)
    except Exception, e:
      print e
      pass

    return

  def doSnowPlot(self, zargs):
    (runTime, model, time, modelDataPath ,previousTime) = zargs
    previous = previousTime
    level = "sfc"
    variable = "snow"
    baseDir = "data"
    imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable
    imgDirAccumTotal = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable + "_accum"
    call("mkdir -p " + imgDir, shell=True)
    call("mkdir -p " + imgDirAccumTotal, shell=True)
    
    # If the inital timestep (0th hour) is in the times set.
    # self.hasInitialTime = 0 in map(int, times)

    # # dont do anything on the 0th hour (if it's the only time being processed)
    # if self.hasInitialTime and len(times) <= 1:
    #   print "Passed 0th Hour only... skipping snowfall stuff"
    #   return
      
    # skip the 0th hour.
    if int(time) == 0:
      return

    #for time in times:
    for region,gribmap in self.regionMaps.items():

      fig, borderWidth, borderBottom = self.getRegionFigure(gribmap)



      startFile = self.getGrib2File(modelDataPath, runTime, model, previous)
      endFile = self.getGrib2File(modelDataPath, runTime, model, time)

      tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
      saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
      borderBottomCmd = "" # Reset bottom border.

      print "Region: " + region
      print "TIME: " + time
      print "START FILE: " + startFile
      print "END FILE: " + endFile

      # if int(time) == 3:
      #   # skip third hour.
      #   return

      skip = False

      grbSwemPrevious = self.cache[previous]['swem']
      grbSwemCurrent = self.cache[time]['swem']
      grbT500 = self.cache[time]['500mbT']
      grbT850 = self.cache[time]['850mbT']
      grbT2m = self.cache[time]['2mT']

      # Check to make sure data is set.
      if grbSwemPrevious is None:
        previous = time
        skip = True

      if grbSwemCurrent is None or grbT500 is None or grbT850 is None or grbT2m is None:
        skip = True

      # try:
      #   grbs=pygrib.open(startFile)
      #   grbs.seek(0)
      #   grbSwemPrevious = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]
      #   grbs.close()
      # except Exception, e:
      #   print "Failure on loading grib [START] file = " + startFile
      #   print "Region" + region
      #   print "Model" + model
      #   print e
      #   previous = time
      #   # DO Increment previous time in the case where previous time has missing data.
      #   # So if previous=33h and time = 36hr, and 33h has missing data:
      #   # The next step would be previous=36hr and time=39hr: total = 39h - 36hr
      #   skip = True
      #   pass

      # try:
      #   grbs=pygrib.open(endFile)
      #   grbs.seek(0)
      #   grbSwemCurrent = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]
      #   grbT500 = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=500)[0]
      #   grbT850 = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=850)[0]
      #   grbT2m = grbs.select(name='2 metre temperature', typeOfLevel='heightAboveGround', level=2)[0]
      #   grbs.close()
      # except Exception, e:
      #   print "Failure on loading grib [END] file = " + endFile
      #   print "Region" + region
      #   print "Model" + model
      #   print e
      #   skip = True
      #   # DONT Increment previous time in the case of missing data.
      #   # ie. if 33h and 36 have missing data, the next increment
      #   # will try 39h - 33h = difference.
      #   pass

      if skip == True:
        print "Skipping Hour: " + time
        continue

      data = {}
      # Subset data for global grids...
      # Very strange bug.
      if model in self.globalModelGrids and region in self.nonLAEAprojections:
        data['500'],lat, lon = grbT500.data(lat1=20,lat2=75,lon1=220,lon2=320)
        data['850'],lat, lon = grbT850.data(lat1=20,lat2=75,lon1=220,lon2=320)
        data['2'],lat, lon   = grbT2m.data(lat1=20,lat2=75,lon1=220,lon2=320)
        data['swemCurr'],lat, lon = grbSwemCurrent.data(lat1=20,lat2=75,lon1=220,lon2=320)
        data['swemPrev'],lat, lon = grbSwemPrevious.data(lat1=20,lat2=75,lon1=220,lon2=320)
      else:
        data['500'] = grbT500.values
        data['850'] = grbT850.values
        data['2']   = grbT2m.values
        data['swemCurr'] = grbSwemCurrent.values
        data['swemPrev'] = grbSwemPrevious.values
        lat, lon = grbT2m.latlons()

      d = np.maximum(data['850'],data['2'])
      d = np.maximum(d, data['500']) 



      dmax = np.where(d >=271.16, d, np.nan)
      dmin = np.where(d <271.16, d, np.nan)

      # np.nan should propagate. Otherwise you end up with (12 + 2*(271.16 - 0)) = (really fucking big). Instead we just want np.nan.
      dmin = (12 + (271.16 - dmin))
      dmax = (12 + 2*(271.16 - dmax))
      dmin = np.nan_to_num(dmin)
      dmax = np.nan_to_num(dmax)

      # A fix for weird grids ie. CONUS for gfs model.
      # This fixes strange graphical.
      # if model in self.globalModelGrids and region in self.nonLAEAprojections:
      #   dmin[dmin > 40] = 0 # Filter grid. I can't quite understand why this is nesc. 
      #                       # It is certainly a bug with matplotlib.
      #                       # 40 = 12 + (271.16 - X) -> X = -22 degrees F.
      #                       # Limits the calculation to -22F...

      dtot = dmin + dmax # Total Snow water equivalent ratios

      swemAccum =  data['swemCurr'] - data['swemPrev']
      swemAccum = np.where(swemAccum > 0, swemAccum, 0)
      # Truncate negative values to 0.
      swemAccum = swemAccum.clip(0)
      dtot = dtot.clip(0)
      


      #snow = swemAccum/25.4 * 10
      snow = (swemAccum*dtot)/25.4
      print '-----------------------------------'
      print "MEAN " + str(np.mean(snow))
      print "-----------------------------------"

      # A fix for weird grids ie. CONUS for gfs model.
      # This fixes strange graphical.
      # if model in self.globalModelGrids and region in self.nonLAEAprojections:
      #   snow[snow < .25] = 0 # Keep small values out of total accumulation calc.
      #                      # Also. might fix a crazy bug. We will see.
      #   median = np.median(snow)
      #   if median > 0:
      #     # In theory the median should be 0.
      #     # If the data glitches out for some reason,
      #     # the median will NOT be 0. So therefore, 
      #     # set all values where value == median = 0
      #     snow[snow == median] = 0
      #     print "CURRENT MEDIAN = " + str(median)
      #     print "FORCING MEDIAN 0!!!!!"

      m = gribmap.getBaseMap()

      if borderBottom > 1.0:
        if gribmap.hasDoubleYBorder:
          borderBottomCmd = " -border 0x" + str(int(borderBottom))
        else:
          borderBottomCmd = " -gravity south -splice 0x" + str(int(borderBottom))

      #if model == "gfs" and proj == 'merc':
        # GFS model (and some others) come with (0 - 360) Longitudes.
        # This must be converted to (-180 - 180) when using Mercator.
      #  lon = self.convertLon360to180(lon, data['2'])

      x,y = m(lon,lat)

      # x = np.arange(-180, 180.5, 1.0)
      # y = np.arange(-90, 91, 1.0)
      # x,y = np.meshgrid(x,y)
      # x,y = m(x,y)

      ax = fig.add_axes([1,1,1,1],axisbg='k') # This needs to be here or else the figsize*DPI calc will not work!
                                              # I have no idea why. Just a Matplot lib quirk I guess.
      SNOWP_LEVS = [0.25,0.5,0.75,1,1.5,2,2.5,3,4,5,6,8,10,12,14,16,18]
      # print snow
      cs = plt.contourf(x,y,snow, SNOWP_LEVS, extend='max',cmap=coltbls.snow2())

      #cs = plt.imshow(data['2'], cmap='RdBu', vmin=data['2'].min(), vmax=data['2'].max(), extent=[x.min(), x.max(), y.min(), y.max()])
      # m = Basemap(llcrnrlat=19,urcrnrlat=50,\
      #             llcrnrlon=-119,urcrnrlon=-56, \
      #             resolution='l',projection='stere',\
      #             lat_ts=50,lat_0=90,lon_0=-100., fix_aspect=False)
      #cs = plt.imshow(data['2'], cmap='RdBu', vmin=data['2'].min(), vmax=data['2'].max(), extent=[x.min(), x.max(), y.min(), y.max()])
      #cs = m.pcolormesh(x,y,swemAccum,shading='flat',cmap=plt.cm.jet)

      #cs = m.contourf(x,y,snow,15,cmap=plt.cm.jet)
      #cb = plt.colorbar(cs, orientation='vertical')
      #m.drawcoastlines()
      #m.fillcontinents()
      m.drawmapboundary()
      #fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())

      #m.drawstates()
      #m.drawcountries()
      # m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0]) # 19.00;-119.00;50.00;-56.00
      # m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])

      # FOR SETTING COLOR BARS!!!!!
      #cb = plt.colorbar(cs, orientation='vertical')
      # cb.outline.set_color('white')

      # axes_obj = plt.getp(ax,'axes')                        #get the axes' property handler
      # plt.setp(plt.getp(axes_obj, 'yticklabels'), color='w') #set yticklabels color
      # plt.setp(plt.getp(axes_obj, 'xticklabels'), color='w') #set xticklabels color
                     
      # plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='w') # set colorbar  
      #                                                                 # yticklabels color
      ##### two new lines ####
      # cb.outline.set_color('w')                   #set colorbar box color
      # cb.ax.yaxis.set_tick_params(color='w')      #set colorbar ticks color 
      ##### two new lines ####
      # fig.set_facecolor('black')
      # END COLORBARS

      #print "convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + borderBottomCmd + " " + saveFileName
      fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
      call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
      call("rm " + tempFileName, shell=True)
      fig.clf()
    plt.close()
    plt.close(fig.number)
    fig = None
    cs = None
    gc.collect()
    return

  def doAccumPrecipPlotMP(self, runTime, region, model, times, gribmap, modelDataPath):

    level = "sfc"
    variable = "precip"
    baseDir = "data"
    imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable
    imgDirAccumTotal = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable + "_accum"
    call("mkdir -p " + imgDir, shell=True)
    call("mkdir -p " + imgDirAccumTotal, shell=True)
    
    # If the inital timestep (0th hour) is in the times set.
    self.hasInitialTime = 0 in map(int, times)
    # dont do anything on the 0th hour (if it's the only time being processed)
    if self.hasInitialTime and len(times) <= 1:
      print "Passed 0th Hour only... skipping precipitation stuff"
      return

    precipSum    = None
    precipSum12  = None
    precipSum24  = None
    # precipSum72  = None
    # precipSum120 = None

    fig, borderWidth, borderBottom = self.getRegionFigure(gribmap)

    for time in times:

      # skip the 0th hour.
      if int(time) == 0:
        continue
      
      # Only get every 6th hour of the GFS.
      # This is because GFS stores 6 hour accums.
      if model == 'gfs' and (int(time) % 6) != 0:
        continue

      # Only do every 3rd hour 0-3hr, 3-6hr, etc.
      # FOR NAM4km only.
      if model == 'nam4km' and (int(time) % 3) != 0:
        continue

      g2File = self.getGrib2File(modelDataPath, runTime, model, time)


      print "Region: " + region
      print "TIME: " + time

      variableAccum = variable + "_accum"
      tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
      saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
      accumTmpFileName = "init_" + region + "_" + model + "_" + level + "_" + variableAccum + "_f" + time + ".png"
      accumSaveFileName = imgDir + "_accum" + "/" + region +"_f" + time + ".gif"
      borderBottomCmd = "" # Reset bottom border.

      skip = False

      precipgrb = self.cache[time]['precip']
      if precipgrb is None:
        skip = True

      if skip == True:
        print "Skipping Hour: " + time
        continue

      # Subset data for global grids...
      # Very strange bug.
      if model in self.globalModelGrids:   #  and region in self.nonLAEAprojections
        precip,lat, lon = precipgrb.data(lat1=20,lat2=75,lon1=220,lon2=320)
      else:
        precip = precipgrb.values
        lat, lon = precipgrb.latlons()

      precip = precip/25.4


      if int(time) > 3:
        # Set Hour accumulation

        if precipSum is None:
          precipSum = precip
        else:
          precipSum += precip
        
        print "MAX PRECIP: " + str(np.max(precip))

        # 120 hour accum.
        # if snowSum120 is None:
        #   precipSum120 = precip
        # else:
        #   precipSum120 += precip

        # # 72 hour accum.
        # if snowSum72 is None:
        #   precipSum72 = precip
        # else:
        #   precipSum72 += precip

        # 24 hour accum
        if precipSum24 is None:
          precipSum24 = precip
        else:
          precipSum24 += precip

        # 12 hour accum
        if precipSum12 is None:
          precipSum12 = precip
        else:
          precipSum12 += precip

      m = gribmap.getBaseMap()

      if borderBottom > 1.0:
        if gribmap.hasDoubleYBorder:
          borderBottomCmd = " -border 0x" + str(int(borderBottom))
        else:
          borderBottomCmd = " -gravity south -splice 0x" + str(int(borderBottom))

      x,y = m(lon,lat)

      PRECIP_LEVS = [0.1, 0.25,0.5,1, 1.5, 2, 2.5,3, 3.5,4, 4.5,5,6,8,10,12,14,16]

      fig.clf()
      if precipSum is not None:
        print "---------------------------------------------------------------------------"
        print "--------------Drawing precip Accum plot for time: " + time + "---------------"
        print "--------------SAVING TO: " + accumSaveFileName
        print "----------------------------------------------------------------------------"
        ax = fig.add_axes([1,1,1,1],axisbg='k')
        cs = plt.contourf(x,y,precipSum, PRECIP_LEVS, extend='max',cmap=coltbls.reflect_ncdc())
        m.drawmapboundary()

        # FOR SETTING COLOR BARS!!!!!
        # cb = plt.colorbar(cs, orientation='vertical')
        # axes_obj = plt.getp(ax,'axes')                        #get the axes' property handler
        # plt.setp(plt.getp(axes_obj, 'yticklabels'), color='w') #set yticklabels color
        # plt.setp(plt.getp(axes_obj, 'xticklabels'), color='w') #set xticklabels color
        # plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='w') # set colorbar  
        # cb.ax.yaxis.set_tick_params(color='w')      #set colorbar ticks color 
        # fig.set_facecolor('black')
        # cb.outline.set_edgecolor('white')
        # END COLORBARS

        fig.savefig(accumTmpFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
        call("convert -background none "+ accumTmpFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + accumSaveFileName, shell=True)
        call("rm " + accumTmpFileName, shell=True)
        fig.clf()

      # if int(time) % 120 == 0 and int(time) > 0:
      #   # do plot
      #   #save to model/precip120/*
      #   imgDir120 = imgDir + "120"
      #   call("mkdir -p " + imgDir120, shell=True)
      #   tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "120" + "_f" + time + ".png"
      #   saveFileName = imgDir120 + "/" + region +"_f" + time + ".gif"
      #   ax = fig.add_axes([1,1,1,1],axisbg='k')
      #   cs = plt.contourf(x, y, precip1120, PRECIP_LEVS, extend='max', cmap=coltbls.precip1())
      #   m.drawmapboundary()

      #   fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
      #   call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
      #   call("rm " + tempFileName, shell=True)
      #   precipSum120 = None
      #   fig.clf()

      # if int(time) % 72 == 0 and int(time) > 0:
      #   # do plot
      #   #save to model/snow72/*
      #   imgDir72 = imgDir + "72"
      #   call("mkdir -p " + imgDir72, shell=True)
      #   tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "72" + "_f" + time + ".png"
      #   saveFileName = imgDir72 + "/" + region +"_f" + time + ".gif"
      #   ax = fig.add_axes([1,1,1,1],axisbg='k')
      #   cs = plt.contourf(x, y, precipSum72, PRECIP_LEVS, extend='max', cmap=coltbls.precip1())
      #   m.drawmapboundary()

      #   fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
      #   call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
      #   call("rm " + tempFileName, shell=True)
      #   precipSum72 = None
      #   fig.clf()

      if int(time) % 24 == 0 and int(time) > 0:
        # do plot
        #save to model/precip24/*
        imgDir24 = imgDir + "24"
        call("mkdir -p " + imgDir24, shell=True)
        tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "24" + "_f" + time + ".png"
        saveFileName = imgDir24 + "/" + region +"_f" + time + ".gif"
        ax = fig.add_axes([1,1,1,1],axisbg='k')
        cs = plt.contourf(x, y, precipSum24, PRECIP_LEVS, extend='max', cmap=coltbls.reflect_ncdc())
        m.drawmapboundary()

        fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
        call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
        call("rm " + tempFileName, shell=True)
        precipSum24 = None
        fig.clf()

      if int(time) % 12 == 0 and int(time) > 0:
        # do plot
        #save to model/precip12/*
        imgDir12 = imgDir + "12"
        call("mkdir -p " + imgDir12, shell=True)
        tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "12" + "_f" + time + ".png"
        saveFileName = imgDir12 + "/" + region +"_f" + time + ".gif"
        ax = fig.add_axes([1,1,1,1],axisbg='k')
        cs = plt.contourf(x, y, precipSum12, PRECIP_LEVS, extend='max', cmap=coltbls.reflect_ncdc())
        m.drawmapboundary()

        fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
        call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
        call("rm " + tempFileName, shell=True)
        precipSum12 = None
        fig.clf()
      
    plt.close()
    plt.close(fig.number)
    fig = None
    cs = None
    gc.collect()
    return

  def doSnowAccumulations(self, runTime, region, model, times, gribmap, modelDataPath ,previousTime):

    previous = previousTime
    level = "sfc"
    variable = "snow"
    baseDir = "data"
    imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable
    imgDirAccumTotal = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable + "_accum"
    call("mkdir -p " + imgDir, shell=True)
    call("mkdir -p " + imgDirAccumTotal, shell=True)
    
    # If the inital timestep (0th hour) is in the times set.
    self.hasInitialTime = 0 in map(int, times)
    # dont do anything on the 0th hour (if it's the only time being processed)
    if self.hasInitialTime and len(times) <= 1:
      print "Passed 0th Hour only... skipping snowfall stuff"
      return

    snowSum    = None
    snowSum12  = None
    snowSum24  = None
    snowSum72  = None
    snowSum120 = None

    fig, borderWidth, borderBottom = self.getRegionFigure(gribmap)

    for time in times:

      # skip the 0th hour.
      if int(time) == 0:
        continue


      startFile = self.getGrib2File(modelDataPath, runTime, model, previous)
      endFile = self.getGrib2File(modelDataPath, runTime, model, time)


      print "Region: " + region
      print "TIME: " + time
      print "START FILE: " + startFile
      print "END FILE: " + endFile

      variableAccum = variable + "_accum"
      tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
      saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
      accumTmpFileName = "init_" + region + "_" + model + "_" + level + "_" + variableAccum + "_f" + time + ".png"
      accumSaveFileName = imgDir + "_accum" + "/" + region +"_f" + time + ".gif"
      borderBottomCmd = "" # Reset bottom border.

      # if int(time) == 3:
      #   # skip third hour.
      #   return
      skip = False

      grbSwemPrevious = self.cache[previous]['swem']
      grbSwemCurrent = self.cache[time]['swem']
      grbT500 = self.cache[time]['500mbT']
      grbT850 = self.cache[time]['850mbT']
      grbT2m = self.cache[time]['2mT']

      # Check to make sure data is set.
      if grbSwemPrevious is None:
        previous = time
        skip = True

      if grbSwemCurrent is None or grbT500 is None or grbT850 is None or grbT2m is None:
        skip = True

      # try:
      #   grbs=pygrib.open(startFile)
      #   grbs.seek(0)
      #   grbSwemPrevious = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]
      #   grbs.close()
      # except Exception, e:
      #   print "Failure on loading grib [START] file = " + startFile
      #   print "Region" + region
      #   print "Model" + model
      #   print e
      #   skip = True
      #   previous = time
      #   # DO Increment previous time in the case where previous time has missing data.
      #   # So if previous=33h and time = 36hr, and 33h has missing data:
      #   # The next step would be previous=36hr and time=39hr: total = 39h - 36hr
      #   pass

      # try:
      #   grbs=pygrib.open(endFile)
      #   grbs.seek(0)
      #   grbSwemCurrent = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]
      #   grbT500 = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=500)[0]
      #   grbT850 = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=850)[0]
      #   grbT2m = grbs.select(name='2 metre temperature', typeOfLevel='heightAboveGround', level=2)[0]
      #   grbs.close()
      # except Exception, e:
      #   print "Failure on loading grib [END] file = " + endFile
      #   print "Region" + region
      #   print "Model" + model
      #   print e
      #   skip = True
      #   # DONT Increment previous time in the case of missing data.
      #   # ie. if 33h and 36 have missing data, the next increment
      #   # will try 39h - 33h = difference.
      #   pass

      if skip == True:
        print "Skipping Hour: " + time
        continue

      data = {}
      # Subset data for global grids...
      # Very strange bug.
      if model in self.globalModelGrids and region in self.nonLAEAprojections:
        data['500'],lat, lon = grbT500.data(lat1=20,lat2=75,lon1=220,lon2=320)
        data['850'],lat, lon = grbT850.data(lat1=20,lat2=75,lon1=220,lon2=320)
        data['2'],lat, lon   = grbT2m.data(lat1=20,lat2=75,lon1=220,lon2=320)
        data['swemCurr'],lat, lon = grbSwemCurrent.data(lat1=20,lat2=75,lon1=220,lon2=320)
        data['swemPrev'],lat, lon = grbSwemPrevious.data(lat1=20,lat2=75,lon1=220,lon2=320)
      else:
        data['500'] = grbT500.values
        data['850'] = grbT850.values
        data['2']   = grbT2m.values
        data['swemCurr'] = grbSwemCurrent.values
        data['swemPrev'] = grbSwemPrevious.values
        lat, lon = grbT2m.latlons()

      d = np.maximum(data['850'],data['2'])
      d = np.maximum(d, data['500']) 



      dmax = np.where(d >=271.16, d, np.nan)
      dmin = np.where(d <271.16, d, np.nan)

      # np.nan should propagate. Otherwise you end up with (12 + 2*(271.16 - 0)) = (really fucking big). Instead we just want np.nan.
      dmin = (12 + (271.16 - dmin))
      dmax = (12 + 2*(271.16 - dmax))
      dmin = np.nan_to_num(dmin)
      dmax = np.nan_to_num(dmax)

      dtot = dmin + dmax # Total Snow water equivalent ratios

      swemAccum =  data['swemCurr'] - data['swemPrev']
      swemAccum = np.where(swemAccum > 0, swemAccum, 0)
      # Truncate negative values to 0.
      swemAccum = swemAccum.clip(0)
      dtot = dtot.clip(0)
      


      #snow = swemAccum/25.4 * 10
      snow = (swemAccum*dtot)/25.4
      print '-----------------------------------'
      print "MEAN " + str(np.mean(snow))
      print "-----------------------------------"


      if int(time) > 3:
        # Set Hour accumulation

        if snowSum is None:
          snowSum = snow
        else:
          snowSum += snow
        
        print "MAX SNOW: " + str(np.max(snow))

        # 120 hour accum.
        if snowSum120 is None:
          snowSum120 = snow
        else:
          snowSum120 += snow

        # 72 hour accum.
        if snowSum72 is None:
          snowSum72 = snow
        else:
          snowSum72 += snow

        # 24 hour accum
        if snowSum24 is None:
          snowSum24 = snow
        else:
          snowSum24 += snow

        # 12 hour accum
        if snowSum12 is None:
          snowSum12 = snow
        else:
          snowSum12 += snow

      m = gribmap.getBaseMap()

      if borderBottom > 1.0:
        if gribmap.hasDoubleYBorder:
          borderBottomCmd = " -border 0x" + str(int(borderBottom))
        else:
          borderBottomCmd = " -gravity south -splice 0x" + str(int(borderBottom))

      x,y = m(lon,lat)

      SNOWP_LEVS = [0.25,0.5,0.75,1,1.5,2,2.5,3,4,5,6,8,10,12,14,16,18]

      fig.clf()
      if snowSum is not None:
        print "---------------------------------------------------------------------------"
        print "--------------Drawing snow Accum plot for time: " + time + "---------------"
        print "--------------SAVING TO: " + accumSaveFileName
        print "----------------------------------------------------------------------------"
        ax = fig.add_axes([1,1,1,1],axisbg='k')
        cs = plt.contourf(x,y,snowSum, SNOWP_LEVS, extend='max',cmap=coltbls.snow2())
        m.drawmapboundary()
        fig.savefig(accumTmpFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
        call("convert -background none "+ accumTmpFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + accumSaveFileName, shell=True)
        call("rm " + accumTmpFileName, shell=True)
        fig.clf()

      if int(time) % 120 == 0 and int(time) > 0:
        # do plot
        #save to model/snow120/*
        imgDir120 = imgDir + "120"
        call("mkdir -p " + imgDir120, shell=True)
        tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "120" + "_f" + time + ".png"
        saveFileName = imgDir120 + "/" + region +"_f" + time + ".gif"
        ax = fig.add_axes([1,1,1,1],axisbg='k')
        cs = plt.contourf(x, y, snowSum120, SNOWP_LEVS, extend='max', cmap=coltbls.snow2())
        m.drawmapboundary()

        fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
        call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
        call("rm " + tempFileName, shell=True)
        snowSum120 = None
        fig.clf()

      if int(time) % 72 == 0 and int(time) > 0:
        # do plot
        #save to model/snow72/*
        imgDir72 = imgDir + "72"
        call("mkdir -p " + imgDir72, shell=True)
        tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "72" + "_f" + time + ".png"
        saveFileName = imgDir72 + "/" + region +"_f" + time + ".gif"
        ax = fig.add_axes([1,1,1,1],axisbg='k')
        cs = plt.contourf(x, y, snowSum72, SNOWP_LEVS, extend='max', cmap=coltbls.snow2())
        m.drawmapboundary()

        fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
        call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
        call("rm " + tempFileName, shell=True)
        snowSum72 = None
        fig.clf()

      if int(time) % 24 == 0 and int(time) > 0:
        # do plot
        #save to model/snow24/*
        imgDir24 = imgDir + "24"
        call("mkdir -p " + imgDir24, shell=True)
        tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "24" + "_f" + time + ".png"
        saveFileName = imgDir24 + "/" + region +"_f" + time + ".gif"
        ax = fig.add_axes([1,1,1,1],axisbg='k')
        cs = plt.contourf(x, y, snowSum24, SNOWP_LEVS, extend='max', cmap=coltbls.snow2())
        m.drawmapboundary()

        fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
        call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
        call("rm " + tempFileName, shell=True)
        snowSum24 = None
        fig.clf()

      if int(time) % 12 == 0 and int(time) > 0:
        # do plot
        #save to model/snow12/*
        imgDir12 = imgDir + "12"
        call("mkdir -p " + imgDir12, shell=True)
        tempFileName = "init_" + region + "_" + model + "_" + level + "_" + variable + "12" + "_f" + time + ".png"
        saveFileName = imgDir12 + "/" + region +"_f" + time + ".gif"
        ax = fig.add_axes([1,1,1,1],axisbg='k')
        cs = plt.contourf(x, y, snowSum12, SNOWP_LEVS, extend='max', cmap=coltbls.snow2())
        m.drawmapboundary()

        fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
        call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
        call("rm " + tempFileName, shell=True)
        snowSum12 = None
        fig.clf()
      previous = time
      
    plt.close()
    plt.close(fig.number)
    fig = None
    cs = None
    gc.collect()
    return

  def getAccumulationStartTime(self, divisor, time):
    quotient  = int(int(time)/divisor) # 24 / 24 = 1 (quotient)
    startInt  = (quotient-1) * divisor # (1-1) * 24 = 0 (Start time if hour = 24)
    startTime = time 
    if startInt < 100:
      if startInt < 10:
        startTime= "00" + str(startInt)
      else:
        startTime= "0" + str(startInt)
    return startTime

  # Take a ndarray of Longitudes, and shift E/W to (-180-180) range.
  def convertLon360to180(self, lons, data):
    loncopy = lons.copy()
    for i,j in enumerate(lons):
      for n,l in enumerate(j):
        #data,loncopy[i] = shiftgrid(-180., data, j,start=False)
        if l >= 180:
          loncopy[i][n]=loncopy[i][n]-360. 
    return loncopy

  def getGrib2File(self, modelDataPath, runTime, model, time):
    g2file = ""
    if model == 'nam':
      time = time[-2:]
      runHour = runTime[-2:]
      g2file = modelDataPath + model + "/" + "nam.t" + runHour + "z.awip32"+ time +".tm00.grib2"
    # elif model == 'gfs':
    #   g2file = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ time 
    elif model == 'gfs':
      runHour = runTime[-2:]
      # gfs.t18z.pgrb2.0p25.f009
      g2file = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2.0p25.f"+ time 
    elif model == 'nam4km':
      runHour = runTime[-2:]
      time = time[-2:]
      # nam.t00z.conusnest.hiresf03.tm00.grib2
      g2file = modelDataPath + model + "/" + "nam.t" + runHour + "z.conusnest.hiresf"+ time +".tm00.grib2"
    elif model == 'hrrr':
      runHour = runTime[-2:]
      time = time[-2:]
      # hrrr.t00z.wrfnatf03.grib2
      g2file = modelDataPath + model + "/" + "hrrr.t" + runHour + "z.wrfnatf"+ time +".grib2"
    return g2file

  def getRegionFigure(self, gribmap):
    frameWidth = 6.402
    frameHieght = 5.121
    fig = None
    borderTop = 0

    borderWidth = gribmap.getBorderX() # In Pixels. Should match that generated by Gempak.
    borderBottom = gribmap.getBorderY()
    if gribmap.hasDoubleYBorder:
      borderTop = borderBottom

    if int(borderBottom) > 0 or int(borderTop) > 0:
      # Top and bottom borders may be different.
      frameHieght = frameHieght - ((borderBottom + borderTop)/200.)
    if int(borderWidth) > 0:
      frameWidth = frameWidth - ((borderWidth*2.)/200.)

    fig = plt.figure(figsize=(frameWidth, frameHieght), dpi = 200)
    return (fig, borderWidth, borderBottom)