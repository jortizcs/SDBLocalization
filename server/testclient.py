#!/usr/bin/env python
# encoding: utf-8
"""
testclient.py

Test Client.

Created by Kaifei Chen on 2013-03-12.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""


import httplib
import json
import time
import threading

def _test():
  HOST = '127.0.0.1'
  PORT = 10080
  SERVICE = '/localize'
  URL = 'http://' + HOST + ':' + str(PORT) + SERVICE
  
  ts = '1354058706884971435'
  sigstr = '00:22:90:39:07:12,UNKNOWN,-77 00:17:df:a7:4c:f2,UNKNOWN,-81 dc:7b:94:35:25:02,UNKNOWN,-90 00:17:df:a7:33:12,UNKNOWN,-92 00:22:90:39:07:15,UNKNOWN,-79 00:17:df:a7:4c:f5,UNKNOWN,-79 dc:7b:94:35:25:05,UNKNOWN,-90 00:17:df:a7:33:15,UNKNOWN,-92 00:22:90:39:07:11,UNKNOWN,-77 00:22:90:39:07:16,UNKNOWN,-79 00:17:df:a7:4c:f6,UNKNOWN,-79 00:17:df:a7:4c:f0,UNKNOWN,-79 00:22:90:39:07:10,UNKNOWN,-80 00:17:df:a7:4c:f1,UNKNOWN,-81 dc:7b:94:35:25:01,UNKNOWN,-89 dc:7b:94:35:25:00,UNKNOWN,-91 00:17:df:a7:33:16,UNKNOWN,-91 00:17:df:a7:33:11,UNKNOWN,-92 dc:7b:94:35:25:06,UNKNOWN,-93 00:22:90:39:70:a1,UNKNOWN,-93'
  data = {'type':'localization', 'data':{'wifi':{'timestamp':ts,'sigstr':sigstr}, 'ABS':''}}
  jsondata = json.dumps(data)
  
  conn = httplib.HTTPConnection(HOST, PORT)
  conn.request('POST', SERVICE, jsondata)
  resp = conn.getresponse()
  
  print resp.read()
  
  print time.ctime()
  threading.Timer(1, _test).start()


if __name__ == '__main__':
  _test()
  
