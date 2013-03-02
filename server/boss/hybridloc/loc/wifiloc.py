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


def localize(ipAddr):
  '''Localize user using WiFi RSSI fingerprints database and WiFi RSSI 
  signature from IP address ipAddr.
  
  Return tuple (building id, (x, y, z), confidence)'''
  sig = _get_signature(ipAddr)
  loc = _find_knn(sig)
  confidence = _get_confidence(loc, sig)
  (buildingId, (x, y, z)) = _get_coordinate(loc)
  
  return (buildingId, (x, y, z), confidence)


def _get_signature(ipAddr):
  '''Get WiFi RSSI signature from WiFi chip with IP address ipAddr.
  
  Return list of (MAC Address, RSSI)'''
  return [("FF:FF:FF:FF:FF:FF", -60)]


def _find_knn(sig):
  '''Find k-nearest neighbor of sigature in database
  
  Return list of (building id, (x, y, z))'''
  return [(0, (0, 0, 0))]


def _get_confidence(loc, sig):
  '''Get confidence based on the localization and signature.
  
  Return float of confidence in range [0.0, 1.0]'''
  return 1.0


def _get_coordinate(loc):
  '''Get location coordinate based on k-nearest neighbors loc.
  
  Return tuple (buildingId, (x, y, z))'''
  return (0, (0, 0, 0))


def update_db():
  '''Update WiFi RSSI fingerprint database.'''
  locdbconn = sqlite3.connect(os.path.dirname(__file__) + "/loc.db")
  locdbc = locdbconn.cursor()
  
  wifitablename = "wifi"
  locdbc.execute("CREATE TABLE IF NOT EXISTS " + wifitablename + 
                 ''' (timestamp text, building text, room text, object text, 
                 x real, y real, signature text, 
                 PRIMARY KEY (timestamp, building))''')
  # TODO: update from phone rather than local files
  directory = os.path.dirname(__file__) + "/tmpdata/wifiloc/"
  configfilename = directory + "Config.csv"
  # use 'U' for universal newlines
  configfile = open(configfilename, 'rU')
  # list of tuple 
  # (filename, timestamp, building, room, object, x, y, purpose, smartphone)
  fileinfos = [tuple(fileinfo.split(",")) for fileinfo in configfile]
  for fileinfo in fileinfos:
    f = open(directory + fileinfo[0])
    siginfos = _get_signatures_from_file(f, float("infinity"))
    for sig, timestamp in siginfos:
      try:
        locdbc.execute("INSERT INTO " + wifitablename + " VALUES (?,?,?,?,?,?,?)"
                      , (timestamp,)+fileinfo[2:7]+(sig,))
      except sqlite3.IntegrityError:
        pass
  locdbconn.commit()
  locdbconn.close()


def _get_signatures_from_file(file, maxnum):
  '''Get WiFi signatures from a text log file.
  
  Return list of tuple of (sig, timestamp), both of which are string'''
  siginfos = []
  records = file.readlines()
  if len(records) > 0:
    currecord = records[0]
    if currecord.count(';') >= 2:
      for i in range(1, len(records)): # ignore last line because it can be incomplete
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
          #wifirecords = itemlist[2].split(' ')
          ## list of (mac, ssid, rssi)
          #sig = [tuple(r.split(",")) for r in wifirecords]
          sig = itemlist[2]
          #sigs.append(sig);
          #timestamps.append(timestamp/(10^(mag + 3)));
          siginfos.append((sig, timestamp))
          if len(siginfos) >= maxnum:
            break
        else:
          pass
        currecord = nextrecord
  return siginfos


def _test():
  pass


if __name__ == '__main__':
  _test()

