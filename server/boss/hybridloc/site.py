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
  
  def __init__(self, service):
    self.service = service    
    resource.Resource.__init__(self)
    
  def getChild(self, name, request):
    if name == '':
        return self
    return resource.Resource.getChild(self, name, request)

  def render_GET(self, request):
    return "POST JSON to me!"

  def render_POST(self, request):
    """POST localization request"""
    self.request = request
    self.request.setHeader('Content-type', 'application/json')
    # TODO handle bad request
    content = json.load(self.request.content)
    d = self.service.localize(content)
    d.addCallback(self._respond)
    
    return server.NOT_DONE_YET
    
  def _respond(self, loc):
    print loc
    self.request.setResponseCode(httplib.OK)
    self.request.write(json.dumps(loc))
    self.request.finish()


class RootResource(resource.Resource):
  """Resource representing the root of the HybridLoc http server"""
  def __init__(self, value=None, contents=['localize']):
    resource.Resource.__init__(self)
    if value:
      self.value = value
    else:
      self.value = {'Contents' : contents}

  def getChild(self, name, request):
    if name == '':
        return self
    return resource.Resource.getChild(self, name, request) 

  def render_GET(self, request):
    request.setHeader('Content-type', 'application/json')
    return json.dumps(self.value)


def get_site():
  """Retuen HybridLoc Site (HTTPFactory)"""
  contents = ['localize']
  root = RootResource(contents=contents)
  
  dbname = "loc"
  dbpool = adbapi.ConnectionPool('sqlite3', dbname)
  dbupdate_interval = 10  # Database update interval in second
  wifiloc_service = WifiLocService(dbpool, dbupdate_interval)
  root.putChild('localize', LocalizeResource(HybridLocService(wifiloc_service)))

  site = server.Site(root)
  return site


def _test():
  pass


if __name__ == '__main__':
  _test()