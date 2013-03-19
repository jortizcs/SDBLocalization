#!/usr/bin/env python
# encoding: utf-8
"""
service.py

HybridLoc localization service.

Created by Kaifei Chen on 2013-02-23.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""


class HybridLocService(object):
  """HybridLoc service"""
  
  def __init__(self, wifiloc):
    self._wifiloc = wifiloc
  
  def localize(self, request):
    """Execute hybridLoc localization service, which fuses results of multiple 
    localization services.
  
    Return tuple (building id, (x, y, z), confidence)"""
    # TODO use DeferredList after adding new loc service
    wifiloc_request = request['data']['wifi']
    d = self._wifiloc.localize(wifiloc_request)
    return d


def _test():
  pass


if __name__ == '__main__':
  _test()
