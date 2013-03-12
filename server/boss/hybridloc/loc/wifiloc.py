#!/usr/bin/env python
# encoding: utf-8
"""
wifiloc.py

WiFi RSSI fingerprint localization module.

Created by Kaifei Chen on 2013-02-21.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""

__all__ = ["localize", "update_db"]


import os
import sqlite3
import numpy
import collections


def localize(sigstr):
  '''Localize user using WiFi RSSI fingerprints database and WiFi RSSI 
  signature from signature.
  
  Return tuple ((building, (x, y, z)), confidence)'''
  locs, _ = _find_knn(sigstr, 10)
  confidence = _get_confidence(locs, sigstr)
  (building, (x, y, z)) = _get_coordinate(locs)
  
  return ((building, (x, y, z)), confidence)


def _find_knn(sigstr, k):
  '''Find k-nearest neighbor of sigature in database
  
  Return tuple (list of (building, (x, y, z)), list of signature distance), 
  with each list length max(k, dbsize)'''
  # TODO: speed bottleneck, try to improve speed!
  locdbname = "loc.db"
  locdbconn = sqlite3.connect(os.path.dirname(__file__) + "/" + locdbname)
  locdbc = locdbconn.cursor()

  #distitem format: ((building, (x, y, z)), signature distance)
  distitems = []
  wifitablename = "wifi"
  #sigrecord format: (timestamp, building, room, object, x, y, z, signature)
  for sigrecord in locdbc.execute("SELECT * FROM " + wifitablename):
    dbsigstr = sigrecord[-1]
    dist = _get_sig_dist(sigstr, dbsigstr)
    distitems.append(((sigrecord[1], sigrecord[4:7]), dist))
  
  distitems.sort(key=lambda distitem:distitem[1])
  
  return zip(*distitems[0:k])


def _get_sig_dist(sigstr1, sigstr2):
  '''Get signature list form signature string.
  
  Return list of (MAC:RSSI)'''
  dftminrssi = -150  # default minimum RSSI
  siglist1 = _get_sig_list(sigstr1)
  siglist2 = _get_sig_list(sigstr2)
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


def _get_sig_list(sigstr):
  '''Get signature list form signature string.
  
  Return list of (MAC:RSSI)'''
  # rssisample format: (MAC Address, SSID, RSSI)
  rssisamples = sigstr.split(" ")
  macs = [sample.split(",")[0] for sample in rssisamples]
  rssis = [sample.split(",")[2] for sample in rssisamples]  # Received Signal Strength Indexes
  siglist = zip(macs, rssis)
  
  return siglist


def _get_confidence(locs, sigstr):
  '''Get confidence based on the localization and signature.
  
  Return float of confidence in range [0.0, 1.0]'''
  return 1.0


def _get_coordinate(locs):
  '''Get location coordinate based on k-nearest neighbors locations.
  
  Return tuple (building, (x, y, z))'''
  buildings = zip(*locs)[0]
  building = collections.Counter(buildings).most_common(1)[0][0]
  coordinates = zip(*locs)[1]
  coordinate = tuple([sum(x)/len(x) for x in zip(*coordinates)])
  return (building, coordinate)


def update_db():
  '''Update WiFi RSSI fingerprint database.'''
  locdbname = "loc.db"
  locdbconn = sqlite3.connect(os.path.dirname(__file__) + "/" + locdbname)
  locdbc = locdbconn.cursor()
  
  wifitablename = "wifi"
  locdbc.execute("CREATE TABLE IF NOT EXISTS " + wifitablename + 
                 ''' (timestamp text, building text, room text, object text, 
                 x real, y real, z real, signature text, 
                 PRIMARY KEY (timestamp, building))''')
  # TODO: update from phone rather than local files
  directory = os.path.dirname(__file__) + "/tmpdata/wifiloc/"
  configfilename = directory + "Config.csv"
  # use 'U' for universal newlines
  configfile = open(configfilename, 'rU')
  # list of tuple of sigrecord:
  # (filename, timestamp, building, room, object, x, y, z, purpose, smartphone)
  fileinfos = [tuple(fileinfo.split(",")) for fileinfo in configfile]
  for fileinfo in fileinfos:
    if fileinfo[8] == "Train":
      f = open(directory + fileinfo[0])
      #sigitem format: (timestamp string, signature string)
      sigitems = _get_sig_items_from_file(f, float("infinity"))
      for timestamp, sigstr in sigitems:
        try:
          #sigrecord format: (timestamp, building, room, object, x, y, z, signature)
          sigrecord = (timestamp,) + fileinfo[2:8] + (sigstr,)
          locdbc.execute("INSERT INTO "+wifitablename+" VALUES (?,?,?,?,?,?,?,?)"
                        , sigrecord)
        except sqlite3.IntegrityError:
          pass
  locdbconn.commit()
  locdbconn.close()


def _get_sig_items_from_file(file, maxnum):
  '''Get WiFi signatures items from a text log file.
  
  Return list of tuple of sigitem (timestamp, sigstr), 
  both of which are strings'''
  #sigitem format: (timestamp string, signature string)
  sigitems = []
  records = file.readlines()
  if len(records) > 0:
    currecord = records[0]
    if currecord.count(';') >= 2:
      for i in range(1, len(records)): #last line may be incomplete
        nextrecord = records[i]
        itemlist = currecord.split("#")[0].split(";")
        (timestamp, des) = itemlist[0:2]  #timestamp, description
        if des == "metadata_log_format":
          if len(itemlist) == 2:  # this record is not complete
            break
          logformat = itemlist[2]
          if int(logformat) == 3:  # nanosecond timing
            mag = 6  # magnitude to millisecond
          else:
            raise ValueError("Cannot recognize log format %s in file %s"
                             % (logformat, file.name))
        elif des.find("wifi") != -1:
          if len(itemlist) == 2:  # this record is not complete
            break
          ## TODO: SSID contains no ?, ", $, [, \, ], +
          ## But currently we assume SSID has no ' ', and we use ' ' to
          ## separate different SSID records
          sigstr = itemlist[2].split(" \n")[0]
          sigitems.append((timestamp, sigstr))
          if len(sigitems) >= maxnum:
            break
        else:
          pass
        currecord = nextrecord
  return sigitems


def _test():
  pass


if __name__ == '__main__':
  _test()

