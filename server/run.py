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
import socket
import json


def main():
  # TODO: UGLY NASTY blocking implementation of server, move to twisted soon!
  HOST = ""
  PORT = 10000
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind((HOST, PORT))
  sock.listen(1)
  
  while True:
    conn, addr = sock.accept()
    requestStr = conn.recv(1024)
    try:
      request = json.loads(requestStr)  #Ahhh, ugly
    except:
      conn.close()
      continue
      
    if request["type"] == "localization":
      loc = hybridloc.localize(request)
      print loc
      try:
        conn.sendall(json.dumps(loc))
      except:
        pass
    
    conn.close()


if __name__ == '__main__':
  main()

