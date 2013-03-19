#!/usr/bin/env python
# encoding: utf-8
"""
user.py

BOSS user manager module. It maintains a user information table, including 
WiFi chip device IP address, accelerometer chip device IP address, etc.

Created by Kaifei Chen on 2013-02-23.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""

# TODO: user manager should be part of BOSS, but I temporarily implement my
# version. It should maintain a user information table, in which there are
# information like primary WiFi chip IP address, primary accelerometer chip 
# IP address, etc.

__all__ = ["get_wifichip_ipaddr"]


import sqlite3


def get_wifichip_ipaddr(userId):
  """Look up user WiFi chip IP address from user manager.
  
  Return string of IP address"""
  
  return '127.0.0.1'


def _test():
  pass


if __name__ == '__main__':
  _test()

