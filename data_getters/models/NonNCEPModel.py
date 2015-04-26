import time
from bs4 import BeautifulSoup
import urllib2
import datetime, re, os


class NonNCEPModel:

  def __init__(self):

    self.modelUrls = {
      'ecmwf':'data-portal.ecmwf.int/', \
      'ukmet': '', \
      'CMC'  : '' \
    }

    self.isNCEPSource = False
    return

  def getFiles(self):
    return

  def getName(self):
    return self.name