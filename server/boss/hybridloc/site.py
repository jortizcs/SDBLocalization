#!/usr/bin/env python
# encoding: utf-8
"""
site.py

HybridLoc localization http site.

Created by Kaifei Chen on 2013-03-15.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""


from twisted.web import resource, server
from twisted.enterprise import adbapi

from boss.hybridloc.service import HybridLocService
from boss.hybridloc.loc.wifiloc.service import WifiLocService
import json
import httplib


class LocalizeResource(resource.Resource):
  """Resource representing localization service."""
  def __init__(self, locservice):
    self._locservice = locservice    
    resource.Resource.__init__(self)
  
  
  def getChild(self, name, request):
    if name == '':
        return self
    return resource.Resource.getChild(self, name, request)
  
  
  def render_GET(self, request):
    return "POST JSON to me!"
  
  
  def render_POST(self, request):
    """POST localization request"""
    request.setHeader('Content-type', 'application/json')
    # TODO handle bad request
    content = json.load(request.content)
    d = self._locservice.localize(content)
    d.addCallback(self._respond, request)
    
    return server.NOT_DONE_YET
  
  
  def _respond(self, loc, request):
    request.setResponseCode(httplib.OK)
    request.write(json.dumps(loc))
    request.finish()


class RootResource(resource.Resource):
  """Resource representing the root of the HybridLoc http server"""
  def __init__(self, value=None, contents=['localize']):
    resource.Resource.__init__(self)
    if value:
      self._value = value
    else:
      self._value = {'Contents' : contents}
  
  
  def getChild(self, name, request):
    if name == '':
        return self
    return resource.Resource.getChild(self, name, request)
  
  
  def render_GET(self, request):
    request.setHeader('Content-type', 'application/json')
    return json.dumps(self._value)


def get_site():
  """Return HybridLoc Site (HTTPFactory)"""
  contents = ['localize']
  root = RootResource(contents=contents)
  
  dbname = "loc.db"
  dbpool = adbapi.ConnectionPool('sqlite3', database = dbname, 
                                 check_same_thread=False)
  dbupdate_interval = 3600  # Database update interval in second
  wifiloc_service = WifiLocService(dbpool, dbupdate_interval)
  root.putChild('localize', LocalizeResource(HybridLocService(wifiloc_service)))
  
  site = server.Site(root)
  return site


def _test():
  pass


if __name__ == '__main__':
  _test()
