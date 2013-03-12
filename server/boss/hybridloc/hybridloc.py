#!/usr/bin/env python
# encoding: utf-8
"""
hybridloc.py

HybridLoc localization module.

Created by Kaifei Chen on 2013-02-23.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""

__all__ = ["localize"]


from boss.hybridloc.loc import wifiloc
from boss import user


def localize(request):
  '''Execute hybridLoc localization service, which fuses results of multiple 
  localization services.
  
  Return tuple (building id, (x, y, z), confidence)'''
  wifisigstr = request["data"]["wifi"]["sigstr"]
  wifiloc.update_db()
  wifilocation, wificonf = wifiloc.localize(wifisigstr)
  hybridlocation = wifilocation
  return hybridlocation


def _test():
  pass


if __name__ == '__main__':
  _test()
