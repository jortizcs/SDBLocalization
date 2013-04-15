#!/usr/bin/env python
# encoding: utf-8
"""
service.py

WiFi RSSI fingerprint localization service.

Created by Kaifei Chen on 2013-02-21.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""


from twisted.application import service
from twisted.enterprise import adbapi
from twisted.internet import reactor, defer, task
from twisted.python import log

import os
import numpy
import collections
import sqlite3


class WifiLoc(object):
  """WifiLoc class"""
  
  def __init__(self, db, dbupdate_interval):
    self._wifitablename = 'wifi'
    self._db = db
    self._lc = task.LoopingCall(self._update_db)
    reactor.callLater(0, self._lc.start, dbupdate_interval)
    
    self._precache_data = []
    self.interim = 100
  
  
  def localize(self, request):
    """Localize user using WiFi RSSI fingerprints database and WiFi RSSI 
    signature from signature.
    
    Return Deferred of tuple ((building, (x, y, z)), confidence)"""
    sigstr = request['sigstr']
    d = self._find_knn(sigstr, k = 10)
    d.addCallback(self._knn_found, sigstr = sigstr)
    
    return d


  @defer.inlineCallbacks
  def _find_knn(self, sigstr, k):
    """Find k-nearest neighbor of sigature in database
    
    Return tuple (list of (building, (x, y, z)), list of signature distance), 
    with each list length max(k, dbsize)"""
    operation = "SELECT * FROM " + self._wifitablename
    d = self._db.runQuery(operation)
    dbsigrecords = yield d
    
    # TODO speed bottleneck, try to improve speed!
    #distitem format: ((building, (x, y, z)), signature distance)
    distitems = []
    #sigrecord format: (timestamp, building, room, object, x, y, z, signature)
    for dbsigrecord in dbsigrecords:
      dbsigstr = dbsigrecord[-1]
      dist = self._get_sig_dist(sigstr, dbsigstr)
      distitems.append(((dbsigrecord[1], dbsigrecord[4:7]), dist))
      
    distitems.sort(key=lambda distitem:distitem[1])
    
    defer.returnValue(zip(*distitems[0:k]))
  
  
  def _knn_found(self, distitems, sigstr):
    """Callback function after found KNN in database
    
    Return tuple ((building, (x, y, z)), confidence)"""
    locs, _ = distitems
    (building, (x, y, z)) = self._get_coordinate(locs)
    confidence = self._get_confidence(locs, sigstr)
    
    # precache
    reactor.callLater(0, self._precache, (building, (x, y, z)))
    
    return ((building, (x, y, z)), confidence)
  
  
  def _get_sig_dist(self, sigstr1, sigstr2):
    """Get signature list form signature string.
    
    Return list of (MAC:RSSI)"""
    dftminrssi = -150  # default minimum RSSI
    siglist1 = self._get_sig_list(sigstr1)
    siglist2 = self._get_sig_list(sigstr2)
    maclist1 = zip(*siglist1)[0]
    maclist2 = zip(*siglist2)[0]
    siglist1.extend([(mac, dftminrssi) for mac in maclist2 if mac not in maclist1])
    siglist2.extend([(mac, dftminrssi) for mac in maclist1 if mac not in maclist2])
    siglist1.sort(key=lambda sample:sample[0])  # sort by MAC address
    siglist2.sort(key=lambda sample:sample[0])
    rssilist1 = map(int, zip(*siglist1)[1])
    rssilist2 = map(int, zip(*siglist2)[1])
    rssiarray1 = numpy.array(rssilist1)
    rssiarray2 = numpy.array(rssilist2)
    dist = numpy.linalg.norm(rssiarray1-rssiarray2)/numpy.sqrt(len(rssilist1))
    
    return dist
  
  
  def _get_sig_list(self, sigstr):
    """Get signature list form signature string.
    
    Return list of (MAC:RSSI)"""
    # rssisample format: (MAC Address, SSID, RSSI)
    rssisamples = sigstr.split(' ')
    macs = [sample.split(',')[0] for sample in rssisamples]
    rssis = [sample.split(',')[2] for sample in rssisamples]  # Received Signal Strength Indexes
    siglist = zip(macs, rssis)
    
    return siglist
  
  
  def _get_confidence(self, locs, sigstr):
    """Get confidence based on the localization and signature.
    
    Return float of confidence in range [0.0, 1.0]"""
    return 1.0
  
  
  def _get_coordinate(self, locs):
    """Get location coordinate based on k-nearest neighbors locations.
    
    Return tuple (building, (x, y, z))"""
    buildings = zip(*locs)[0]
    building = collections.Counter(buildings).most_common(1)[0][0]
    coordinates = zip(*locs)[1]
    coordinate = tuple([sum(x)/len(x) for x in zip(*coordinates)])
    return (building, coordinate)
  
  
  def _precache(self, loc):
    #Put data in local variable
    (near, area_ids) = self._near_grey_area(loc)
    if near == True:
      self._append_precache_data(loc[0], area_ids)


  def _near_grey_area(self, loc):
    (building, (x, y, z)) = loc
    area_ids = []
    if building == "SODA":
      if x > 655-self.interim and y < 342+self.interim:
        area_ids.append(1)
      if 854+self.interim > x > 500-self.interim and 998+self.interim > y > 898-self.interim:
        area_ids.append(2)
      if 456+self.interim > x and y > 1154-self.interim:
        area_ids.append(3)
      
    if area_ids != []:
      return (True, area_ids)
    else:
      return (False, None)
  
  
  @defer.inlineCallbacks
  def _append_precache_data(self, building, area_ids):
    operation = "SELECT * FROM " + self._wifitablename
    d = self._db.runQuery(operation)
    dbsigrecords = yield d
    
    #distitem format: ((building, (x, y, z)), signature distance)
    distitems = []
    #sigrecord format: (timestamp, building, room, object, x, y, z, signature)
    for dbsigrecord in dbsigrecords:
      dbbuilding = dbsigrecord[1]
      if building == dbbuilding:
        dbx = dbsigrecord[4]
        dby = dbsigrecord[5]
        if (1 in area_ids) \
           and dbx > 655-self.interim \
           and dby < 342+self.interim:
          self._precache_data.append(dbsigrecord)
        if (2 in area_ids) \
           and 854+self.interim > dbx > 500-self.interim \
           and 998+self.interim > dby > 898-self.interim:
          self._precache_data.append(dbsigrecord)
        if (3 in area_ids) \
           and 456+self.interim > dbx \
           and dby > 1154-self.interim:
          self._precache_data.append(dbsigrecord)
    self._precache_data = list(set(self._precache_data))
  
  
  def get_precache_data(self):
    ret_data, self._precache_data = self._precache_data, []
    return ret_data
  
  
  @defer.inlineCallbacks
  def _update_db(self):
    """Update WiFi RSSI fingerprint database."""
    log.msg("Start updating database")
    operation = "CREATE TABLE IF NOT EXISTS " + self._wifitablename + \
                " (timestamp text, building text, room text, object text, \
                   x real, y real, z real, signature text, \
                   PRIMARY KEY (timestamp, building))"
    yield self._db.runQuery(operation)
    
    # TODO: update from phone rather than local files
    directory = os.path.dirname(__file__) + '/tmpdata/wifiloc/'
    configfilename = directory + 'Config.csv'
    # use 'U' for universal newlines
    configfile = open(configfilename, 'rU')
    # list of tuple of sigrecord:
    # (filename, timestamp, building, room, object, x, y, z, purpose, smartphone)
    fileinfos = [tuple(fileinfo.split(',')) for fileinfo in configfile]
    for fileinfo in fileinfos:
      if fileinfo[8] == 'Train':
        f = open(directory + fileinfo[0])
        #sigitem format: (timestamp string, signature string)
        sigitems = self._get_sig_items_from_file(f, float('infinity'))
        for timestamp, sigstr in sigitems:
          try:
            #sigrecord format: (timestamp, building, room, object, x, y, z, signature)
            sigrecord = (timestamp,) + fileinfo[2:8] + (sigstr,)
            operation = "INSERT INTO " + self._wifitablename + \
                        " VALUES (?,?,?,?,?,?,?,?)"
            yield self._db.runQuery(operation, sigrecord)
          except sqlite3.IntegrityError:
            pass
    log.msg("Database updated")
  
  
  def _get_sig_items_from_file(self, file, maxnum):
    """Get WiFi signatures items from a text log file.
    
    Return list of tuple of sigitem (timestamp, sigstr), 
    both of which are strings"""
    #sigitem format: (timestamp string, signature string)
    sigitems = []
    records = file.readlines()
    if len(records) > 0:
      currecord = records[0]
      if currecord.count(';') >= 2:
        for i in range(1, len(records)): #last line may be incomplete
          nextrecord = records[i]
          itemlist = currecord.split('#')[0].split(';')
          (timestamp, des) = itemlist[0:2]  #timestamp, description
          if des == 'metadata_log_format':
            if len(itemlist) == 2:  # this record is not complete
              break
            logformat = itemlist[2]
            if int(logformat) == 3:  # nanosecond timing
              mag = 6  # magnitude to millisecond
            else:
              raise ValueError("Cannot recognize log format %s in file %s"
                               % (logformat, file.name))
          elif des.find('wifi') != -1:
            if len(itemlist) == 2:  # this record is not complete
              break
            ## TODO: SSID contains no ?, ', $, [, \, ], +
            ## But currently we assume SSID has no ' ', and we use ' ' to
            ## separate different SSID records
            sigstr = itemlist[2].split(' \n')[0]
            sigitems.append((timestamp, sigstr))
            if len(sigitems) >= maxnum:
              break
          else:
            pass
          currecord = nextrecord
    return sigitems