"""
run.tac

Twisted Application Configuration file of BOSS Server.

# Currently only run localization service. 2013-02-23. Kaifei

Created by Kaifei Chen on 2013-02-23.
Copyright (c) 2013 UC Berkeley. All rights reserved.
"""

from twisted.application import internet, service
from twisted.internet import reactor

from boss.hybridloc import site as hybridloc_site

application = service.Application('hybridloc')
port = 10000
site = hybridloc_site.get_site()
server = internet.TCPServer(port, site)
server.setServiceParent(service.IServiceCollection(application))


