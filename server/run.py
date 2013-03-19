#!/usr/bin/env python
# encoding: utf-8
"""
run.py

BOSS Server.

# Currently only run localization service. 2013-02-23. Kaifei

Created by Kaifei Chen on 2013-02-23.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""


from twisted.internet import reactor

from boss.hybridloc import site as hybridloc_site

def main():
  port = 10000
  reactor.listenTCP(port, hybridloc_site.get_site())
  reactor.run()


if __name__ == '__main__':
  main()

