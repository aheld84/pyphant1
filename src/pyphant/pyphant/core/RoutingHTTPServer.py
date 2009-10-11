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

import pyphant.core.bottle
from paste import httpserver
from paste.translogger import TransLogger
from threading import Thread
from time import sleep, time
import logging
from urllib2 import (urlopen, URLError, HTTPError)


class UnreachableError(Exception):
    pass


class PasteServer(pyphant.core.bottle.ServerAdapter):
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

    def run(self):
        self.paste_server = PasteServer(host=self.host, port=self.port)
        try:
            pyphant.core.bottle.run(app=self.app, server=self.paste_server)
        except Exception as exep:
            self.error = exep


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
        self.host = host.lower()
        self.port = int(port)
        self.server_thread = None
        self.app = pyphant.core.bottle.Bottle()
        self.app.serve = False
        self.is_serving = False
        self.logger = logging.getLogger('pyphant')
        if start:
            self.start()

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
        self.logger.info("Waiting for server thread to start...")
        while not hasattr(self.server_thread, 'paste_server') \
                  and not hasattr(self.server_thread, 'error'):
            sleep(0.1)
        while not hasattr(self.server_thread.paste_server, 'httpserver') \
                  and not hasattr(self.server_thread, 'error'):
            sleep(0.1)
        isup = False
        t1 = time()
        while not hasattr(self.server_thread, 'error') and not isup \
                  and time() - t1 < 10.0:
            sleep(0.1)
            try:
                stream = None
                stream = urlopen(self.url, timeout=3.0)
                isup = True
            except HTTPError:
                isup = True
            except (URLError, IOError):
                pass
            finally:
                if stream != None:
                    stream.close()
        if hasattr(self.server_thread, 'error'):
            self.logger.error("Could not start server thread. Reason: %s" \
                                     % self.server_thread.error.__str__())
            raise self.server_thread.error
        if not isup:
            msg = "Server started, but is not responding."
            self.logger.error(msg)
            self.stop()
            raise UnreachableError()
        self.logger.info("Server thread started.")
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
        try:
            self.server_thread.paste_server.httpserver.server_close()
        except AttributeError:
            pass
        self.logger.info("Waiting for server thread to stop...")
        self.server_thread.join(10.0)
        if self.server_thread.isAlive():
            self.logger.error("Could not stop server thread!")
        else:
            self.logger.info("Server thread stopped.")
        self.server_thread = None
        self.is_serving = False
