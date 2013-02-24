#!/usr/bin/env python
# encoding: utf-8
"""
run.py

BOSS Server.

# Currently only run localization service. 2013-02-23. Kaifei

Created by Kaifei Chen on 2013-02-23.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""

from boss.hybridloc import hybridloc


def main():
  print hybridloc.localize(0)


if __name__ == '__main__':
  main()

