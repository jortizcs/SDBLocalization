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


def localize(userId):
  '''Execute hybridLoc localization service, which fuses results of multiple 
  localization services.
  
  Return tuple (building id, (x, y, z), confidence)'''
  ipAddr = user.get_wifichip_ipaddr(userId)
  hybridLoc = wifiloc.localize(ipAddr)
  return hybridLoc


def _test():
  pass


if __name__ == '__main__':
  _test()
