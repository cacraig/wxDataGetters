import pygrib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid,cm
import numpy as np
from pylab import rcParams
from matplotlib.colors import LinearSegmentedColormap
import coltbls
from subprocess import call, STDOUT

# Plot SnowFall!
class grib2Plot:

  '''''
  Intialize the grib2Plot class with everything we need!

  @return void
  '''''
  def __init__(self):
    return

  def plotSnowFall(self, model="gfs", times = ["048","051"], runTime="2015031312", modelDataPath="/vagrant", previousTime = "045"):
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
    #       startFile = "gfs.t" + runHour + "z.pgrb2.0p25.f"+ previous 
    #       endFile = "gfs.t" + runHour + "z.pgrb2.0p25.f"+ time
    #       tempFileName = "init_" + model + "_" + level + "_" + variable + "_f" + time + ".png"
    #       saveFileName = imgDir + "/" + region +"_f" + time + ".gif"
    #       self.doSnowPlot(startFile, endFile, region, model,tempFileName, saveFileName, True)
    #       previous = time

    if model == "gfs":
      for region in regions:
        for time in times:
          runHour = runTime[-2:]
          startFile = modelDataPath + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ previous 
          endFile = modelDataPath + "/" + "gfs.t" + runHour + "z.pgrb2full.0p50.f"+ time
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

    # data = data[:]
    lat, lon = grbT2m.latlons()

    if model == "gfs" and not isGFS0p25:
      x = np.arange(-180, 180.5, .5)
      y = np.arange(-90, 91, .5)
      x,y = np.meshgrid(x,y)
      x,y = m(x,y)
    else:
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

    fig.savefig(tempFileName, dpi=200, bbox_inches='tight', pad_inches=0)
    call("convert "+ tempFileName + " -transparent '#000000' " + saveFileName, shell=True)
    #call("rm " + tempFileName)


    fig.clf()

    return

g2plot = grib2Plot()
g2plot.plotSnowFall()

# rcParams['figure.figsize'] = (8.26,15)

# def forceAspect(ax,aspect=1):
#     im = ax.get_images()
#     extent =  im[0].get_extent()
#     ax.set_aspect(abs((extent[1]-extent[0])/(extent[3]-extent[2]))/aspect)

# plt.figure()
# grib='/vagrant/gfs.t12z.pgrb2.0p25.f048'
# model = "gfs"
# grbs=pygrib.open(grib)

# grbs.seek(0)


# # for grb in grbs:
# #   print grb
# # exit(1)
# #Water equivalent of accumulated snow depth
# grbSwemPrevious = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]


# grib='/vagrant/gfs.t12z.pgrb2.0p25.f051'
# model = "gfs"
# grbs=pygrib.open(grib)

# grbs.seek(0)
# grbSwemCurrent = grbs.select(name='Water equivalent of accumulated snow depth', typeOfLevel='surface', level=0)[0]
# grbT500 = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=500)[0]
# grbT850 = grbs.select(name='Temperature', typeOfLevel='isobaricInhPa', level=850)[0]
# grbT2m = grbs.select(name='2 metre temperature', typeOfLevel='heightAboveGround', level=2)[0]
# data = {}
# data['500'] = grbT500.values
# data['850'] = grbT850.values
# data['2']   = grbT2m.values
# data['swemCurr'] = grbSwemCurrent.values
# data['swemPrev'] = grbSwemPrevious.values

# d = np.maximum(data['850'],data['2'])
# d = np.maximum(d, data['500']) 

# dmax = np.where(d >=271.16, d, np.nan)
# dmin = np.where(d <271.16, d, np.nan)

# dmin = (12 + (271.16 - dmin))
# dmax = (12 + 2*(271.16 - dmax))
# dmin = np.nan_to_num(dmin)
# dmax = np.nan_to_num(dmax)
# dtot = dmin + dmax # Total Snow water equivalent ratios

# swemAccum =  data['swemCurr'] - data['swemPrev']

# snow = swemAccum/25.4 * dtot
# print swemAccum.min()
# print snow.min()

# # data = data[:]
# lat, lon = grbT2m.latlons()



# # lon[:] = [x - 180 for x in lon]
# # shift so lons go -180 to 180

# m = Basemap(llcrnrlat=19,urcrnrlat=50,\
#              llcrnrlon=-119,urcrnrlon=-56, \
#             resolution='l',projection='stere',\
#             lat_ts=50,lat_0=90,lon_0=-100.)

# #data,lon = shiftgrid(180.,data['500'][:],lon[:],start=False)
# # print lon.min()
# # exit(1)
# # lon1 = lon.copy()
# # for n, l in enumerate(lon1):
# #     print l
# #     exit(1)
# #     if l >= 180:
# #        lon1[n]=lon1[n]-360. 
# # lon = lon1
# # print lon

# # m = Basemap(projection='merc',llcrnrlat=19,urcrnrlat=50,\
# #             llcrnrlon=-125,urcrnrlon=-56,lat_ts=50,resolution='i', fix_aspect=False)

# # FOR GFS 0.5 degree for whatever reason.
# if model == "gfs.0p5":
#   x = np.arange(-180, 180.5, .5)
#   y = np.arange(-90, 91, .5)
#   x,y = np.meshgrid(x,y)
#   x,y = m(x,y)
# else:
#   x,y = m(lon,lat)




# fig = plt.figure(figsize=(8.26,6.402))
# #fig = plt.gcf()
# #ax = fig.add_subplot(111, aspect='equal')
# #x, y = m(lon,lat)

# SNOWP_LEVS = [0.25,0.5,0.75,1,1.5,2,2.5,3,4,5,6,8,10,12,14,16,18]
# cs = plt.contourf(x,y,swemAccum,SNOWP_LEVS, extend='max',cmap=coltbls.snow2())

# #cs = m.pcolormesh(x,y,swemAccum,shading='flat',cmap=plt.cm.Greys) #, vmin=240, vmax=310
# # cr = m.pcolormesh(x,y,dmax,shading='flat',cmap=plt.cm.Greys, vmin=0, vmax=25)
# # adjustFigAspect(fig, 1.25)
# # Get current size
# #fig_size = plt.rcParams["figure.figsize"]
# #print fig.dpi
# # Prints: [8.0, 6.0]
# # print "Current size:", fig_size
# #DPI = fig.get_dpi()
# #fig.set_size_inches(2000.0/float(DPI),1024.0/float(DPI))

# #fig.set_size_inches(8.26,5)
# # Set figure width to 12 and height to 9
# #fig_size[0] = 8.26
# #fig_size[1] = 5
# #plt.rcParams["figure.figsize"] = fig_size

# m.drawcoastlines()
# #m.fillcontinents()
# m.drawmapboundary()
# m.drawstates()
# m.drawcountries()
# # m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0]) # 19.00;-119.00;50.00;-56.00
# # m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])
# # plt.figsize = (10.83,13.55)
# plt.colorbar(cs, orientation='vertical')

# fig.savefig("testmax.png",dpi=200, bbox_inches='tight', pad_inches=0)
# fig.clf()
