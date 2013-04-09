#!/usr/bin/env python
# encoding: utf-8
"""
service.py

HybridLoc localization service.

Created by Kaifei Chen on 2013-02-23.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""


from twisted.application import service

from boss.hybridloc.loc import wifiloc

class HybridLoc(object):
  """HybridLoc class"""
  
  def __init__(self, db):
    self._db = db
    self._wifiloc = wifiloc.WifiLoc(self._db, dbupdate_interval = 3600)
  
  def localize(self, request):
    """Execute hybridLoc localization service, which fuses results of multiple 
    localization services.
  
    Return tuple (building id, (x, y, z), confidence)"""
    # TODO use DeferredList after adding new loc service
    wifiloc_request = request['data']['wifi']
    d = self._wifiloc.localize(wifiloc_request)
    return d


  def _offload(self, loc, host):
    """Offload datac from server to client for local calculation"""
    pass
