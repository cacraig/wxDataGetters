import pygrib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid,cm
import numpy as np
from pylab import rcParams
from matplotlib.colors import LinearSegmentedColormap
import coltbls
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
      "CONUS": (19,-119, 50, -56, "stere"), \
      "NC" : (30.00, -87.25, 41.00, -71.25, "merc"), \
      "WA" : (41.75, -128.00, 52.75, -112.00, "merc") \
    }
    self.regions   = ['CONUS','NC','WA'] 
    self.constants = constants
    self.isPng = ['CONUS']
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
      if model == 'gfs' and region != 'CONUS':
        continue

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

        if model == "gfs" and region is not "CONUS":
          # GFS model (and some others) come with (0 - 360) Longitudes.
          # This must be converted to (-180 - 180) when using Mercator.
          lon = self.convertLon360to180(lon, temp2m)
        
        # TURNING OFF MESHGRID FOR GFS FOR NOW. DAMN SHAPE BUG yo.
        # if model == 'gfs'and proj != 'merc':
        #   x = np.arange(-180, 180.5, 1.0).reshape((361,720))
        #   y = np.arange(-90, 91, 1.0).reshape((361,720))
        #   x,y = np.meshgrid(x,y)
        #   x,y = m(x,y)
        # else:
        x,y = m(lon,lat)
        ax = fig.add_axes([1,1,1,1], axisbg='k') # This needs to be here or else the figsize*DPI calc will not work!
                                                 # I have no idea why. Just a Matplotlib quirk I guess.

        # TURNING OFF MESHGRID FOR GFS FOR NOW. DAMN SHAPE BUG yo.
        if proj != 'merc' and model != 'gfs':
          cs = m.pcolormesh(x, y, temp2m, cmap=plt.cm.jet)
        else:
          cs = m.contourf(x,y,temp2m,20,cmap=plt.cm.jet)

        # m.drawcoastlines()
        m.drawmapboundary()


        # m.drawstates()
        # m.drawcountries()
        # m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0]) # 19.00;-119.00;50.00;-56.00
        # m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])

        # FOR SETTING COLOR BARS!!!!!
        # cb = plt.colorbar(cs, orientation='vertical')
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
        
        # PNG optimization
        # pngquant -o lossy.png --force --quality=70-80 input.png
        # optipng -o1 -strip all -out out.png -clobber input.png

        print "convert -background none "+ tempFileName + " " + borderBottomCmd + " -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName

        print "pngquant -o "+ os.getcwd()+ "/" + tempFileName + " --force --quality=70-80 "+ os.getcwd()+ "/" + tempFileName
        fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor())
        call("pngquant -o "+ tempFileName + " --force --quality=45-60 "+ tempFileName, shell=True)
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
    imgDir24 = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable + "24"
    imgDir72 = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable + "72"
    imgDir120 = baseDir+"/"+ model+"/"+runTime+"/"+level+"/"+variable + "120"
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
    for region in self.regions:
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
          tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
          saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
          self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)

          # Get 24 hour snowfall totals
          if int(time) % 24 == 0 and int(time) > 0:
            startTime = self.getAccumulationStartTime(24, time)
            variableAccum = variable + "24"
            #save to model/snow24/*
            call("mkdir -p " + imgDir24, shell=True)
            startFile = self.getGrib2File(modelDataPath, runHour, model, startTime[-2:])
            endFile = self.getGrib2File(modelDataPath, runHour, model, shortTime)
            tempFileName = "init_" + model + "_" + level + "_" + variableAccum + "_f" + time + ".png"
            saveFileName = imgDir24 + "/" + region +"_f" + time + ".gif"
            self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)
          # Get 72 hour snowfall totals
          if int(time) % 72 == 0 and int(time) > 0:
            startTime = self.getAccumulationStartTime(72, time)
            variableAccum = variable + "72"
            #save to model/snow24/*
            call("mkdir -p " + imgDir72, shell=True)
            startFile = self.getGrib2File(modelDataPath, runHour, model, startTime[-2:])
            endFile = self.getGrib2File(modelDataPath, runHour, model, shortTime)
            tempFileName = "init_" + model + "_" + level + "_" + variableAccum + "_f" + time + ".png"
            saveFileName = imgDir72 + "/" + region +"_f" + time + ".gif"
            self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)

        if model == "gfs":
          runHour = runTime[-2:]
          startFile = self.getGrib2File(modelDataPath, runHour, model, previous)
          endFile = self.getGrib2File(modelDataPath, runHour, model, time)
          tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
          saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
          self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)

          # Get 24 hour snowfall totals
          if int(time) % 24 == 0 and int(time) > 0:
            startTime = self.getAccumulationStartTime(24, time)
            variableAccum = variable + "24"
            #save to model/snow24/*
            call("mkdir -p " + imgDir24, shell=True)
            startFile = self.getGrib2File(modelDataPath, runHour, model, startTime)
            endFile = self.getGrib2File(modelDataPath, runHour, model, time)
            tempFileName = "init_" + model + "_" + level + "_" + variableAccum + "_f" + time + ".png"
            saveFileName = imgDir24 + "/" + region +"_f" + time + ".gif"
            self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)
          # Get 72 hour snowfall totals
          if int(time) % 72 == 0 and int(time) > 0:
            startTime = self.getAccumulationStartTime(72, time)
            variableAccum = variable + "72"
            #save to model/snow72/*
            call("mkdir -p " + imgDir72, shell=True)
            startFile = self.getGrib2File(modelDataPath, runHour, model, startTime)
            endFile = self.getGrib2File(modelDataPath, runHour, model, time)
            tempFileName = "init_" + model + "_" + level + "_" + variableAccum + "_f" + time + ".png"
            saveFileName = imgDir72 + "/" + region +"_f" + time + ".gif"
            self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)
          # Get 120 hour snowfall totals
          if int(time) % 120 == 0 and int(time) > 0:
            startTime = self.getAccumulationStartTime(120, time)
            variableAccum = variable + "120"
            #save to model/snow120/*
            call("mkdir -p " + imgDir120, shell=True)
            startFile = self.getGrib2File(modelDataPath, runHour, model, startTime)
            endFile = self.getGrib2File(modelDataPath, runHour, model, time)
            tempFileName = "init_" + model + "_" + level + "_" + variableAccum + "_f" + time + ".png"
            saveFileName = imgDir120 + "/" + region +"_f" + time + ".gif"
            self.doSnowPlot(startFile, endFile, region, model, tempFileName, saveFileName)

        # Set the previous time for next iteration.
        previous = time

    return

  def doSnowPlot(self, startFile, endFile, region, model, tempFileName, saveFileName, isGFS0p25 = False):

    borderBottomCmd = "" # Reset bottom border.

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

    m, fig, borderWidth, proj, borderBottom = self.getRegionProjection(region)

    if borderBottom > 1.0:
      borderBottomCmd = " -gravity south -splice 0x" + str(int(borderBottom))

    lat, lon = grbT2m.latlons()

    if model == "gfs" and proj == 'merc':
      # GFS model (and some others) come with (0 - 360) Longitudes.
      # This must be converted to (-180 - 180) when using Mercator.
      lon = self.convertLon360to180(lon, data['2'])

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


    print "convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + borderBottomCmd + " " + saveFileName
    fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0,facecolor=fig.get_facecolor())
    call("convert -background none "+ tempFileName + " " + borderBottomCmd + " -transparent '#000000' -matte -bordercolor none -border " + str(int(borderWidth)) + "x0 " + saveFileName, shell=True)
    call("rm " + tempFileName, shell=True)

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
      proj = 'merc'
      # NC      NORTH CAROLINA       30.00  -87.25   41.00  -71.25
      m = Basemap(llcrnrlat=30.00,urcrnrlat=41.00,\
            llcrnrlon=-87.25,urcrnrlon=-71.25, \
            resolution='l',projection=proj,\
            lat_ts=20, fix_aspect=False)

      #fig = plt.figure(figsize=(6.402,5.121))
      borderWidth = 34. # In Pixels. Should match that generated by Gempak.
      frameWidth = frameWidth - ((borderWidth*2.)/200.)
      fig = plt.figure(figsize=(frameWidth,frameHieght), dpi = 200)
    if region == "WA":
      proj = 'merc'
      # WA      WASHINGTON   41.75 -128.00   52.75 -112.00 
      m = Basemap(llcrnrlat=41.75,urcrnrlat=52.75,\
            llcrnrlon=-128.00,urcrnrlon=-112.00, \
            resolution='l',projection='merc',\
            lat_ts=50, fix_aspect=False)
      #fig = plt.figure(figsize=(6.062,5.121))
      borderWidth = 136. # In Pixels. Should match that generated by Gempak.
      frameWidth = frameWidth - ((borderWidth*2.)/200.)
      fig = plt.figure(figsize=(frameWidth,frameHieght), dpi = 200)

    return (m,fig, borderWidth, proj, borderBottom)