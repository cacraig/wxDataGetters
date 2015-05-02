import matplotlib
matplotlib.use('Agg')

import pygrib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid,cm
import numpy as np
from pylab import rcParams
from matplotlib.colors import LinearSegmentedColormap
from objects import coltbls
from subprocess import call, STDOUT
import concurrent.futures
import os

# See: /home/vagrant/GEMPAK7/gempak/tables/stns/geog.tbl 
# !------------------------------------------------------------------------------
# !G      GEOG NAME           CENLAT  CENLON   LLLAT   LLLON   URLAT   URLON PROJ
# !(8)    (18)              (8)     (8)     (8)     (8)     (8)     (8)      (30)
# !------------------------------------------------------------------------------
# NC      NORTH CAROLINA       35.50  -79.25   30.00  -87.25   41.00  -71.25 NPS
# WA      WASHINGTON           47.25 -120.00   41.75 -128.00   52.75 -112.00 NPS
# WWE     WINTER WX AREA       36.00  -78.00   18.00 -106.00   54.00  -50.00 NPS
# OK      OKLAHOMA             35.75  -97.25   30.25 -105.25   41.25  -89.25 NPS
# MA      MASSACHUSETTS        42.25  -72.25   36.75  -80.25   47.75  -64.25 NPS (LABELED NEUS)
# CENTUS  CENTRAL US           36.15  -91.20   24.70 -105.40   47.60  -77.00 STR/90;-95;0

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
  def __init__(self, constants):

    self.regionBounds = {
      #                              CENLAT  CENLON   LLLAT   LLLON   URLAT   URLON PROJ
      # NC      NORTH CAROLINA       35.50  -79.25   30.00  -87.25   41.00  -71.25  laea
      "CONUS": (None, None, 19,-119, 50, -56, "stere"), \
      "NC" : (35.50, -79.25, 30.00, -87.25, 41.00, -71.25, "laea"), \
      "WA" : (47.25, -120.00, 41.75, -128.00, 52.75, -112.00, "laea"), \
      "OK" : (35.75, -97.25,30.25, -105.25, 41.25,  -89.25, "laea"), \
    }
    self.regions   = ['NC','WA','CONUS','OK'] 
    self.constants = constants
    call("mkdir -p " + self.constants.numPyTmpDir, shell=True)
    self.isPng = ['CONUS']
    self.snowSum = None
    self.snowSum12 = None
    self.snowSum24 = None
    self.snowSum72 = None
    self.snowSum120 = None
    return

  def plot2mTemp(self, model, times, runTime, modelDataPath):
    level = "sfc"
    variable = "tmpf"
    baseDir = "data"
    imgDir = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable
    call("mkdir -p " + imgDir, shell=True)
    runHour = runTime[-2:]

    for region in self.regions:

      borderBottomCmd = '' # Reset any bottom border.

      # Sub regions (contourf is broken right now for global models Sub regions. Use gempak...)
      # if model == 'gfs' and region != 'CONUS':
      #   continue

      for time in times:

        if model == 'nam' or model == 'nam4km':
          # Requires time in format 00-99
          g2File = self.getGrib2File(modelDataPath, runHour, model, time[-2:])
        else:
          # Requires time in format 000-999
          g2File = self.getGrib2File(modelDataPath, runHour, model, time)
        
        convertExtension = ".gif"
        if region in self.isPng:
          convertExtension = ".png"


        tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
        saveFileName = imgDir + "/" + region +"_f" + time + convertExtension
        try:
          grbs=pygrib.open(g2File)
          grbs.seek(0)
          gTemp2m = grbs.select(name='2 metre temperature', typeOfLevel='heightAboveGround', level=2)[0]
        except Exception, e:
          print e
          pass

        temp2m = gTemp2m.values

        # Convert Kelvin to (F)
        temp2m = ((temp2m- 273.15)* 1.8000) + 32.00
        m, fig, borderWidth, proj, borderBottom = self.getRegionProjection(region)

        lat, lon = gTemp2m.latlons()

        if borderBottom > 1.0:
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

        # TURNING OFF MESHGRID FOR GFS FOR NOW. DAMN SHAPE BUG yo.
        if region == 'CONUS' and model != 'gfs':
          cs = m.pcolormesh(x, y, temp2m, cmap=plt.cm.jet, vmin=-25, vmax=115)
        else:
          CLEVELS= [(c*5)-25 for c in range(29)]
          cs = m.contourf(x,y,temp2m,CLEVELS,cmap=plt.cm.jet, vmin=-25, vmax=115)

        # m.drawcoastlines()
        m.drawmapboundary()
        # Overlay 32 degree isotherm
        cc = m.contour(x,y,temp2m, [32], cmap=plt.cm.winter, vmin=32, vmax=32)

        #m.drawstates()
        #m.drawcountries()
        #m.drawcoastlines()
        # m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0]) # 19.00;-119.00;50.00;-56.00
        # m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])

        # FOR SETTING COLOR BARS!!!!!
        # cb = plt.colorbar(cs, orientation='vertical', ticks=[(c*10)-25 for c in range(29)])
        # cb.outline.set_color('white')

        # axes_obj = plt.getp(ax,'axes')                        #get the axes' property handler
        # plt.setp(plt.getp(axes_obj, 'yticklabels'), color='w') #set yticklabels color
        # plt.setp(plt.getp(axes_obj, 'xticklabels'), color='w') #set xticklabels color
                       
        # plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='w') # set colorbar  
        #                                                                 # yticklabels color
        # #### two new lines ####
        # cb.outline.set_color('w')                   #set colorbar box color
        # cb.ax.yaxis.set_tick_params(color='w')      #set colorbar ticks color 
        # cb.ax.set_yticklabels([(c*10)-25 for c in range(29)])# vertically oriented colorbar        #### two new lines ####
        # fig.set_facecolor('black')
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

        fig.clf()
        plt.close()

    return

  def plotSnowFall(self, model, times, runTime, modelDataPath, previousTime):
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

    # nam.t18z.awip3281.tm00.grib2
    for region in self.regions:
      # Clear snow sums for each region.
      self.snowSum    = None
      self.snowSum12  = None
      self.snowSum24  = None
      self.snowSum72  = None
      self.snowSum120 = None

      for time in times:
        # skip the 0th hour.
        if int(time) == 0:
          continue

        if model == "nam":
          shortTime = time[-2:]
          shortTimePrevious = previous[-2:]
          runHour = runTime[-2:]
          startFile = self.getGrib2File(modelDataPath, runHour, model, shortTimePrevious)
          endFile = self.getGrib2File(modelDataPath, runHour, model, shortTime)
          try:
            self.doSnowPlot(startFile, endFile, region, model, level, variable, time, imgDir)
          except Exception, e:
            print e

        if model == "gfs":
          runHour = runTime[-2:]
          startFile = self.getGrib2File(modelDataPath, runHour, model, previous)
          endFile = self.getGrib2File(modelDataPath, runHour, model, time)
          try:
            self.doSnowPlot(startFile, endFile, region, model, level, variable, time, imgDir)
          except Exception, e:
            print e

        # Set the previous time for next iteration.
        previous = time
      # Save accumulation data.
      #self.saveAccumulationData(variable, region, model)

    return

  def doSnowPlot(self, startFile, endFile, region, model, level, variable, time, imgDir):

    variableAccum = variable + "_accum"
    tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
    saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
    accumTmpFileName = "init_" + model + "_" + level + "_" + variableAccum + "_f" + time + ".png"
    accumSaveFileName = imgDir + "_accum" + "/" + region +"_f" + time + ".gif"
    borderBottomCmd = "" # Reset bottom border.

    print "Region: " + region
    print "TIME: " + time
    print "START FILE: " + startFile
    print "END FILE: " + endFile

    # if int(time) == 3:
    #   # skip third hour.
    #   return

    try:
      grbs=pygrib.open(startFile)
      grbs.seek(0)
      grbSwemPrevious = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]
    except Exception, e:
      print "Failure on loading grib [START] file = " + startFile
      print "Region" + region
      print "Model" + model
      print e
      return

    try:
      grbs=pygrib.open(endFile)
      grbs.seek(0)
      grbSwemCurrent = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]
      grbT500 = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=500)[0]
      grbT850 = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=850)[0]
      grbT2m = grbs.select(name='2 metre temperature', typeOfLevel='heightAboveGround', level=2)[0]
    except Exception, e:
      print "Failure on loading grib [END] file = " + endFile
      print "Region" + region
      print "Model" + model
      print e
      return

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
    swemAccum = np.where(swemAccum > 0, swemAccum, 0)
    swemAccum.clip(0)
    dtot.clip(0)


    snow = swemAccum/25.4 * 10
    if int(time) > 3:
      # Set Hour accumulation

      if self.snowSum is None:
        self.snowSum = snow
      else:
        self.snowSum += snow
      
      print "MAX SNOW: " + str(np.max(snow))

      # 120 hour accum.
      if self.snowSum120 is None:
        self.snowSum120 = snow
      else:
        self.snowSum120 += snow

      # 72 hour accum.
      if self.snowSum72 is None:
        self.snowSum72 = snow
      else:
        self.snowSum72 += snow

      # 24 hour accum
      if self.snowSum24 is None:
        self.snowSum24 = snow
      else:
        self.snowSum24 += snow

      # 12 hour accum
      if self.snowSum12 is None:
        self.snowSum12 = snow
      else:
        self.snowSum12 += snow
    
    m, fig, borderWidth, proj, borderBottom = self.getRegionProjection(region)

    if borderBottom > 1.0:
      borderBottomCmd = " -gravity south -splice 0x" + str(int(borderBottom))

    lat, lon = grbT2m.latlons()

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
    if self.snowSum is not None:
      print "---------------------------------------------------------------------------"
      print "--------------Drawing snow Accum plot for time: " + time + "---------------"
      print "--------------SAVING TO: " + accumSaveFileName
      print "----------------------------------------------------------------------------"
      ax = fig.add_axes([1,1,1,1],axisbg='k')
      cs = plt.contourf(x,y,self.snowSum, SNOWP_LEVS, extend='max',cmap=coltbls.snow2())
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
      tempFileName = "init_" + model + "_" + level + "_" + variable + "120" + "_f" + time + ".png"
      saveFileName = imgDir120 + "/" + region +"_f" + time + ".gif"
      ax = fig.add_axes([1,1,1,1],axisbg='k')
      cs = plt.contourf(x, y, self.snowSum120, SNOWP_LEVS, extend='max', cmap=coltbls.snow2())
      m.drawmapboundary()

      fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
      call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
      call("rm " + tempFileName, shell=True)
      self.snowSum120 = None
      fig.clf()

    if int(time) % 72 == 0 and int(time) > 0:
      # do plot
      #save to model/snow72/*
      imgDir72 = imgDir + "72"
      call("mkdir -p " + imgDir72, shell=True)
      tempFileName = "init_" + model + "_" + level + "_" + variable + "72" + "_f" + time + ".png"
      saveFileName = imgDir72 + "/" + region +"_f" + time + ".gif"
      ax = fig.add_axes([1,1,1,1],axisbg='k')
      cs = plt.contourf(x, y, self.snowSum72, SNOWP_LEVS, extend='max', cmap=coltbls.snow2())
      m.drawmapboundary()

      fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
      call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
      call("rm " + tempFileName, shell=True)
      self.snowSum72 = None
      fig.clf()

    if int(time) % 24 == 0 and int(time) > 0:
      # do plot
      #save to model/snow24/*
      imgDir24 = imgDir + "24"
      call("mkdir -p " + imgDir24, shell=True)
      tempFileName = "init_" + model + "_" + level + "_" + variable + "24" + "_f" + time + ".png"
      saveFileName = imgDir24 + "/" + region +"_f" + time + ".gif"
      ax = fig.add_axes([1,1,1,1],axisbg='k')
      cs = plt.contourf(x, y, self.snowSum24, SNOWP_LEVS, extend='max', cmap=coltbls.snow2())
      m.drawmapboundary()

      fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
      call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
      call("rm " + tempFileName, shell=True)
      self.snowSum24 = None
      fig.clf()

    if int(time) % 12 == 0 and int(time) > 0:
      # do plot
      #save to model/snow12/*
      imgDir12 = imgDir + "12"
      call("mkdir -p " + imgDir12, shell=True)
      tempFileName = "init_" + model + "_" + level + "_" + variable + "12" + "_f" + time + ".png"
      saveFileName = imgDir12 + "/" + region +"_f" + time + ".gif"
      ax = fig.add_axes([1,1,1,1],axisbg='k')
      cs = plt.contourf(x, y, self.snowSum12, SNOWP_LEVS, extend='max', cmap=coltbls.snow2())
      m.drawmapboundary()

      fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
      call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
      call("rm " + tempFileName, shell=True)
      self.snowSum12 = None
      fig.clf()
    
    plt.close()



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

  def getGrib2File(self, modelDataPath, runHour, model, time):
    g2file = ""
    if model == 'nam':
      g2file = modelDataPath + model + "/" + "nam.t" + runHour + "z.awip32"+ time +".tm00.grib2"
    # elif model == 'gfs':
    #   g2file = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ time 
    elif model == 'gfs':
      # gfs.t18z.pgrb2.0p25.f009
      g2file = modelDataPath + model + "/" + "gfs.t" + runHour + "z.pgrb2.0p25.f"+ time 
    elif model == 'nam4km':
      # nam.t00z.conusnest.hiresf03.tm00.grib2
      g2file = modelDataPath + model + "/" + "nam.t" + runHour + "z.conusnest.hiresf"+ time +".tm00.grib2"
    return g2file

  def getRegionProjection(self, region):
    borderWidth = 1.
    frameWidth = 6.402
    frameHieght = 5.121
    fig = None
    proj = None
    borderBottom = 1.

    if region == "CONUS":
      proj = 'stere'
      m = Basemap(llcrnrlat=19,urcrnrlat=50,\
                  llcrnrlon=-119,urcrnrlon=-56, \
                  resolution='l',projection=proj,\
                  lat_ts=50,lat_0=90,lon_0=-100., fix_aspect=False)
      # fig = plt.figure(figsize=(6.402,5.121))
      borderWidth = 61. # In Pixels. Should match that generated by Gempak.
      borderBottom = 40.
      frameWidth = frameWidth - ((borderWidth*2.)/200.)
      frameHieght = frameHieght - ((borderBottom)/200.)
      fig = plt.figure(figsize=(frameWidth, frameHieght), dpi = 200)
      
    if region == "NC":
      proj = 'laea'
      # NC      NORTH CAROLINA       30.00  -87.25   41.00  -71.25  CLAT: 35.50 CLON: -79.25
      m = Basemap(llcrnrlat=30.00,urcrnrlat=41.00,\
            llcrnrlon=-87.25,urcrnrlon=-71.25, \
            resolution='l',projection=proj,\
            lat_ts=20,lat_0=35.50,lon_0=-79.25, fix_aspect=False)

      #fig = plt.figure(figsize=(6.402,5.121))
      borderWidth = 35. # In Pixels. Should match that generated by Gempak.
      frameWidth = frameWidth - ((borderWidth*2.)/200.)
      fig = plt.figure(figsize=(frameWidth,frameHieght), dpi = 200)
    if region == "WA":
      proj = 'laea'
      # WA      WASHINGTON   41.75 -128.00   52.75 -112.00  CLAT: 47.25 CLON: -120.00
      m = Basemap(llcrnrlat=41.75,urcrnrlat=52.75,\
            llcrnrlon=-128.00,urcrnrlon=-112.00, \
            resolution='l',projection=proj,\
            lat_ts=50,lat_0=47.25,lon_0=-120.00, fix_aspect=False)
      #fig = plt.figure(figsize=(6.062,5.121))
      borderWidth = 135. # In Pixels. Should match that generated by Gempak.
      frameWidth = frameWidth - ((borderWidth*2.)/200.)
      fig = plt.figure(figsize=(frameWidth,frameHieght), dpi = 200)
    if region == "OK":
      proj = 'laea'
      # OK      OKLAHOMA   30.25 -105.25   41.25  -89.25 CLAT: 35.75  CLON: -97.25
      m = Basemap(llcrnrlat=30.25,urcrnrlat=41.25,\
            llcrnrlon=-105.25,urcrnrlon=-89.25, \
            resolution='l',projection=proj,\
            lat_ts=50,lat_0=35.75,lon_0=-97.25, fix_aspect=False)
      #fig = plt.figure(figsize=(6.062,5.121))
      borderWidth = 37. # In Pixels. Should match that generated by Gempak.
      frameWidth = frameWidth - ((borderWidth*2.)/200.)
      fig = plt.figure(figsize=(frameWidth,frameHieght), dpi = 200)

    return (m,fig, borderWidth, proj, borderBottom)