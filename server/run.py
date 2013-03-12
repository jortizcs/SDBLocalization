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
    request = json.loads(conn.recv(1024))  #Ahhh, ugly
    if request["type"] == "localization":
      loc = hybridloc.localize(request)
      conn.sendall(json.dumps(loc))
      print loc


if __name__ == '__main__':
  main()

