#!/usr/bin/env python
# encoding: utf-8
"""
service.py

HybridLoc localization.

Created by Kaifei Chen on 2013-02-23.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""


from twisted.application import service

from boss.hybridloc.loc import wifiloc


class HybridLoc(object):
  """HybridLoc class"""
  
  def __init__(self, db, content = ['wifi']):
    self._db = db
    self._content = content
    
    if 'wifi' in self._content:
      self._wifiloc = wifiloc.WifiLoc(self._db, dbupdate_interval = 3600)
  
  
  def localize(self, request):
    """Execute hybridLoc localization service, which fuses results of multiple 
    localization services.
  
    Return tuple (building id, (x, y, z), confidence)"""
    # TODO use DeferredList after adding new loc service
    wifiloc_request = request['data']['wifi']
    d = self._wifiloc.localize(wifiloc_request)
    return d
  
  
  def get_precache_data(self):
    """Get precache data in cloud"""
    # Currently we assume only one user
    precache_data = {}
    if 'wifi' in self._content:
      precache_data['wifi'] = self._wifiloc.get_precache_data()
    
    return precache_data