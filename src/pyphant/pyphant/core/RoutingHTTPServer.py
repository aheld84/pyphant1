# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008, Rectorate of the University of Freiburg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This module provides an HTTP server (paste) with URL routing (bottle)
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source: $

import bottle
from paste import httpserver
from paste.translogger import TransLogger
from threading import Thread


class PasteServer(bottle.ServerAdapter):
    def run(self, handler):
        app = TransLogger(handler)
        self.httpserver = httpserver.serve(app, host=self.host,
                                           port=str(self.port),
                                           start_loop=False)
        self.httpserver.serve_forever()


class PasteServerThread(Thread):
    def __init__(self, host, port, app, *args, **kargs):
        Thread.__init__(self, *args, **kargs)
        self.host = host
        self.port = port
        self.app = app
        self.paste_server = None

    def run(self):
        self.paste_server = PasteServer(host=self.host, port=self.port)
        bottle.run(app=self.app, server=self.paste_server)


class RoutingHTTPServer(object):
    """
    paste server with bottle routing and start/stop/pause methods
    usage:
      server = RoutingHTTPServer()
      server.app : Bottle instance, use it to add routes etc.
      server.url : URL server is listening at
    """

    def __init__(self, host=u'127.0.0.1', port=8080, start=False):
        """
        Sets up the server and (optionally) starts it.
        Arguments:
        - `host`: hostname to listen on
        - `port`: port to listen on
        - `start`: flag that indicates whether to start the server
        """
        self.host = host
        self.port = port
        self.app = None
        self.server_thread = None
        self.app = bottle.Bottle()
        self.app.serve = False
        self.is_serving = False

    def _get_url(self):
        return u'http://%s:%d/' % (self.host, self.port)
    url = property(_get_url)

    def start(self):
        """
        Starts or resumes the server.
        """
        if self.is_serving:
            self.app.serve = True
            return
        self.server_thread = PasteServerThread(self.host, self.port, self.app)
        self.server_thread.start()
        self.app.serve = True
        self.is_serving = True

    def pause(self):
        """
        Pauses the server, i.e. denies all requests. Use start() to resume.
        """
        self.app.serve = False

    def stop(self):
        """
        Stops the server.
        """
        self.app.serve = False
        self.server_thread.paste_server.httpserver.server_close()
        self.server_thread = None
        self.is_serving = False
