#!/usr/bin/env python
# encoding: utf-8
"""
service.py

BOSS service.

Created by Kaifei Chen on 2013-02-23.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""


from twisted.application import service
from twisted.enterprise import adbapi
from twisted.internet import defer

from zope.interface import implements

from boss.interface import IBOSSService
from boss.hybridloc import hybridloc


class BOSSService(service.Service):
  """BOSS service"""
  
  implements(IBOSSService)
  
  def __init__(self, dbname = "boss.db", content = ['localize', 'precache']):
    # TODO: add other services
    self._db = adbapi.ConnectionPool('sqlite3', database = dbname, 
                                     check_same_thread=False)
    self._content = content
    
    if 'localize' in self._content:
      self._loc = hybridloc.HybridLoc(self._db)
  
  
  def content(self):
    return self._content
  
  
  def localize(self, request):
    # TODO: maintain an instance of _localizer for each user
    if 'localize' in self._content:
      d = self._loc.localize(request)
      return d
    else:
      return defer.fail(NoLocalizerError())
  
  
  def get_precache_data(self):
    # Currently we assume only one user
    precache_data = {}
    if 'localize' in self._content:
      precache_data['localize'] = self._loc.get_precache_data()
    
    return precache_data


class NoLocalizerError(Exception):
  pass
  