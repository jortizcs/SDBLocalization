#!/usr/bin/env python
# encoding: utf-8
"""
wifiloc.py

WiFi RSSI fingerprint localization module.

Created by Kaifei Chen on 2013-02-21.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""

__all__ = ["localize", "update_db"]


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
  # TODO: update from phone rather than local files
  pass


def _test():
  pass


if __name__ == '__main__':
  _test()

