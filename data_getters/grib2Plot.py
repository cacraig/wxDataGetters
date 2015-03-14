import pygrib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid,cm
import numpy as np
from pylab import rcParams
from matplotlib.colors import LinearSegmentedColormap
import coltbls
from subprocess import call, STDOUT

# See: /home/vagrant/GEMPAK7/gempak/tables/stns/geog.tbl 
# !------------------------------------------------------------------------------
# !G      GEOG NAME           CENLAT  CENLON   LLLAT   LLLON   URLAT   URLON PROJ
# !(8)    (18)              (8)     (8)     (8)     (8)     (8)     (8)      (30)
# !------------------------------------------------------------------------------
# NC      NORTH CAROLINA       35.50  -79.25   30.00  -87.25   41.00  -71.25 NPS
# WA      WASHINGTON           47.25 -120.00   41.75 -128.00   52.75 -112.00 NPS

# setup north polar stereographic basemap.
# The longitude lon_0 is at 6-o'clock, and the
# latitude circle boundinglat is tangent to the edge
# of the map at lon_0. Default value of lat_ts
# (latitude of true scale) is pole.
# m = Basemap(projection='npstere',boundinglat=10,lon_0=270,resolution='l')


# Plot SnowFall!
class Grib2Plot:

  '''''
  Intialize the grib2Plot class with everything we need!

  @return void
  '''''
  def __init__(self):
    self.regionBounds = {
      "CONUS": (19,-119, 50, -56, "stere"), \
      "NC" : (30.00, -87.25, 41.00, -71.25, "merc"), \
      "WA" : (41.75, -128.00, 52.75, -112.00, "merc") \
    }
    return

  def plotSnowFall(self, model, times, runTime, modelDataPath, previousTime):
    previous = previousTime
    regions = ['CONUS']
    level = "sfc"
    variable = "snow"
    baseDir = "data"
    imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable
    call("mkdir -p " + imgDir, shell=True)

    # if model == "gfs":
    #   for region in regions:
    #     for time in times:
    #       runHour = runTime[-2:]
    #       startFile = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2.0p25.f"+ previous 
    #       endFile = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2.0p25.f"+ time
    #       tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
    #       saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
    #       self.doSnowPlot(startFile, endFile, region, model,tempFileName, saveFileName, True)
    #       previous = time

    # nam.t18z.awip3281.tm00.grib2
    if model == "nam":
      for region in regions:
        for time in times:
          shortTime = time[-2:]
          shortTimePrevious = previous[-2:]
          runHour = runTime[-2:]
          startFile = modelDataPath + model + "/" + "nam.t" + runHour + "z.awip32"+ shortTimePrevious +".tm00.grib2"
          endFile = modelDataPath + model + "/" + "nam.t" + runHour + "z.awip32"+ shortTime +".tm00.grib2"
          tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
          saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
          self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)

          # Get 24 hour snowfall totals
          if int(time) % 24 == 0 and int(time) > 0:
            startTime = self.getAccumulationStartTime(24, time)
            #save to model/snow24/*
            imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable+"24"
            call("mkdir -p " + imgDir, shell=True)
            startFile = modelDataPath + model + "/" + "nam.t" + runHour + "z.awip32"+ startTime +".tm00.grib2"
            endFile = modelDataPath + model + "/" + "nam.t" + runHour + "z.awip32"+ time +".tm00.grib2"
            tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
            saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
            self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)
          # Get 72 hour snowfall totals
          if int(time) % 72 == 0 and int(time) > 0:
            startTime = self.getAccumulationStartTime(72, time)
            #save to model/snow24/*
            imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable+"72"
            call("mkdir -p " + imgDir, shell=True)
            startFile = modelDataPath + model + "/" + "nam.t" + runHour + "z.awip32"+ startTime +".tm00.grib2"
            endFile = modelDataPath + model + "/" + "nam.t" + runHour + "z.awip32"+ time +".tm00.grib2"
            tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
            saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
            self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)
          previous = time

    if model == "gfs":
      for region in regions:
        for time in times:
          runHour = runTime[-2:]
          startFile = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ previous 
          endFile = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ time
          tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
          saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
          self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)

          # Get 24 hour snowfall totals
          if int(time) % 24 == 0 and int(time) > 0:
            startTime = self.getAccumulationStartTime(24, time)
            #save to model/snow24/*
            imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable+"24"
            call("mkdir -p " + imgDir, shell=True)
            startFile = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ startTime 
            endFile = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ time
            tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
            saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
            self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)
          # Get 72 hour snowfall totals
          if int(time) % 72 == 0 and int(time) > 0:
            startTime = self.getAccumulationStartTime(72, time)
            #save to model/snow72/*
            imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable+"72"
            call("mkdir -p " + imgDir, shell=True)
            startFile = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ startTime 
            endFile = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ time
            tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
            saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
            self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)
          # Get 120 hour snowfall totals
          if int(time) % 120 == 0 and int(time) > 0:
            startTime = self.getAccumulationStartTime(120, time)
            #save to model/snow120/*
            imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable+"120"
            call("mkdir -p " + imgDir, shell=True)
            startFile = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ startTime 
            endFile = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ time
            tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
            saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
            self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)
          previous = time

    return

  def doSnowPlot(self, startFile, endFile, region, model, tempFileName, saveFileName, isGFS0p25 = False):

    try:
      grbs=pygrib.open(startFile)
      grbs.seek(0)
      grbSwemPrevious = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]
    except Exception, e:
      print e
      return

    try:
      grbs=pygrib.open(endFile)
      grbs.seek(0)
      grbSwemCurrent = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]
    except Exception, e:
      print e
      return

    grbT500 = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=500)[0]
    grbT850 = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=850)[0]
    grbT2m = grbs.select(name='2 metre temperature', typeOfLevel='heightAboveGround', level=2)[0]
    data = {}
    data['500'] = grbT500.values
    data['850'] = grbT850.values
    data['2']   = grbT2m.values
    data['swemCurr'] = grbSwemCurrent.values
    data['swemPrev'] = grbSwemPrevious.values
    d = np.maximum(data['850'],data['2'])
    d = np.maximum(d, data['500']) 

    dmax = np.where(d >=271.16, d, np.nan)
    dmin = np.where(d <271.16, d, np.nan)

    dmin = (12 + (271.16 - dmin))
    dmax = (12 + 2*(271.16 - dmax))
    dmin = np.nan_to_num(dmin)
    dmax = np.nan_to_num(dmax)
    dtot = dmin + dmax # Total Snow water equivalent ratios

    swemAccum =  data['swemCurr'] - data['swemPrev']

    snow = swemAccum/25.4 * dtot
    print swemAccum.min()
    print snow.min()

    m = Basemap(llcrnrlat=19,urcrnrlat=50,\
                llcrnrlon=-119,urcrnrlon=-56, \
                resolution='l',projection='stere',\
                lat_ts=50,lat_0=90,lon_0=-100.)

    lat, lon = grbT2m.latlons()

    # if model == "gfs" and not isGFS0p25:
    #   x = np.arange(-180, 180.5, .5)
    #   y = np.arange(-90, 91, .5)
    #   x,y = np.meshgrid(x,y)
    #   x,y = m(x,y)
    # else:
    x,y = m(lon,lat)

    fig = plt.figure(figsize=(8.26,6.402))
    ax = fig.add_axes([1,1,1,1],axisbg='k')
    SNOWP_LEVS = [0.25,0.5,0.75,1,1.5,2,2.5,3,4,5,6,8,10,12,14,16,18]
    cs = plt.contourf(x,y,swemAccum,SNOWP_LEVS, extend='max',cmap=coltbls.snow2())

    # m.drawcoastlines()
    #m.fillcontinents()
    m.drawmapboundary()
    # m.drawstates()
    # m.drawcountries()
    # m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0]) # 19.00;-119.00;50.00;-56.00
    # m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])
    # plt.figsize = (10.83,13.55)
    #plt.colorbar(cs, orientation='vertical')
    print "convert "+ tempFileName + " -transparent '#000000' " + saveFileName
    fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0)
    call("convert "+ tempFileName + " -transparent '#000000' " + saveFileName, shell=True)
    call("rm " + tempFileName, shell=True)


    fig.clf()

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