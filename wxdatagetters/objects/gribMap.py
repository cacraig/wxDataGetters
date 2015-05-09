import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap

'''''
This Class defines a GribMap which has properties:
basemap: A matplotlib basemap
borderX: Border (padding) Width.
borderY: Border (padding) Height.
'''''
class GribMap:
  '''''
  This class represents an instance of a GribMap.

  @return void
  '''''
  def __init__(self, **kwargs):

    # Default Attributes.
    self.llcrnrlat  = None
    self.urcrnrlat  = None
    self.llcrnrlon  = None
    self.urcrnrlon  = None
    self.resolution = 'l'
    self.projection = None
    self.lat_ts = None
    self.lat_0  = None
    self.lon_0 = None 
    self.fix_aspect = None
    self.borderX = 0.
    self.borderY = 0.
    self.hasDoubleYBorder = False
    
    # Dynamically set all object attributes from unpacked kwargs.
    for key, value in kwargs.items():
      setattr(self, key, value)

    self.basemap = Basemap(llcrnrlat=self.llcrnrlat, urcrnrlat=self.urcrnrlat,\
                       llcrnrlon=self.llcrnrlon,urcrnrlon=self.urcrnrlon, \
                       resolution=self.resolution,projection=self.projection,\
                       lat_ts=self.lat_ts,lat_0=self.lat_0,lon_0=self.lon_0, fix_aspect=self.fix_aspect)
    return

  def getBorderX(self):
    return self.borderX
  
  def getBorderY(self):
    return self.borderY

  def getBaseMap(self):
    return self.basemap
