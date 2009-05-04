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
This module provides the WebInterface class for the KnowledgeManager
as well as some HTTP and HTML helper classes.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source: $

from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
import HTMLParser
import logging
from types import DictType


class HTTPAnswer():
    """
    This class provides the possibility to send HTML answers via HTTP.
    """
    def __init__(self,
                 code,
                 message = None,
                 httpheaders = {},
                 contenttype = 'text/html',
                 htmlheaders = {},
                 htmlbody = '',
                 senddefaulterrors = True):
        """
        Initializes the HTTP answer.
        code -- HTTP status code
        message -- human readable reason for the HTTP status code
        httpheaders -- dictionary of HTTP headers
        contenttype -- self explanatory
        htmlheaders -- dictionary of HTML headers, e.g.
                       {'pyphant':{'test':'Testing'}} translates to
                       '<pyphant test = "Testing">'
        htmlbody -- HTML body text
        senddefaulterrors -- if set to True and code >= 400, all arguments
                             except code and message are ignored and a standard
                             error message is sent. Set this to false if you
                             want to provide your own HTML body instead.
        """
        self._code = code
        self._message = message
        self._httpheaders = httpheaders
        self._htmlheaders = htmlheaders
        self._htmlbody = htmlbody
        self._httpheaders['Content-type'] = contenttype
        self._senddefaulterrors = senddefaulterrors

    def sendTo(self, handler):
        """
        Sends the HTML answer via HTTP through a given HTTP handler.
        handler -- HTTP handler
        """
        _logger = logging.getLogger("pyphant")
        if self._code >= 400 and self._senddefaulterrors:
            #send error response
            handler.send_error(self._code, self._message)
        else:
            #send HTTP headers...
            handler.send_response(self._code, self._message)
            for key, value in self._httpheaders.items():
                handler.send_header(key, value)
                _logger.debug("key: %s, value: %s\n", key, value)
            handler.end_headers()
            #send HTML headers...
            handler.wfile.write('<html>\n<head>\n')
            for tag, attrs in self._htmlheaders.items():
                if isinstance(attrs, DictType):
                    handler.wfile.write('<%s '%(tag, ))
                    for key, value in attrs.items():
                        handler.wfile.write('%s="%s" '% (key, value))
                    handler.wfile.write('>\n')
                else:
                    handler.wfile.write('<%s>%s</%s>\n'%(tag, attrs, tag))
            handler.wfile.write('</head>\n')
            #send HTML body...
            handler.wfile.write('<body>\n')
            handler.wfile.write(self._htmlbody + '\n')
            handler.wfile.write('</body></html>\n')
            handler.wfile.write('\n')


class HTMLDict(dict):
    """
    Behaves like a dictionary but provides HTML output via the getHTML method.
    """
    def __init__(self, keylabel, valuelabel):
        """
        Creates an empty dictionary.
        keylabel -- label for the keys
        valuelabel -- label for the values
        """
        self.keylabel = keylabel
        self.valuelabel = valuelabel

    def getHTML(self, printkeys = True):
        """
        Returns HTML code representing the dictionary as a HTML table. If the
        dictionary contains instances that provide a getHTML method themselves,
        then it is used instead of str().
        printkeys -- whether to generate a column for the keys as well
        """
        if printkeys:
            output = '<table border="2" width="100%%"><tr><th>%s</th>\
<th>%s</th></tr>\n'%(self.keylabel, self.valuelabel)
        else:
            output = '<table border="2" width="100%%"><tr><th>%s</th>\
</tr>\n'%(self.valuelabel, )
        for k, v in self.items():
            if hasattr(k, 'getHTML'):
                kout = k.getHTML()
            else:
                kout = str(k)
            if hasattr(v, 'getHTML'):
                vout = v.getHTML()
            else:
                vout = str(v)
            if printkeys:
                output += '<tr width="100%%"><td>%s</td><td>%s</td></tr>\n'\
                          % (kout, vout)
            else:
                output += '<tr width="100%%"><td>%s</td></tr>\n' % (vout, )
        output += '</table>\n'
        return output

    def setDict(self, d):
        """
        Copies the content of the given dictionary to this one.
        All keys are deleted first.
        """
        self.clear()
        for k in d:
            self[k] = d[k]


class HTMLLink():
    """
    This class provides HTML code for hyperlinks.
    """
    def __init__(self, url, linktext, target = None):
        """
        url -- self explanatory
        linktext -- text the user sees to click on
        target -- link target, e.g. '_blank'
        """
        self._url = url
        self._linktext = linktext
        self._target = target

    def getHTML(self):
        """
        Returns the hyperlink as HTML code.
        """
        targetstring = ""
        if self._target != None:
            targetstring = ' target="%s"' % (self._target, )
        return '<a href="%s"%s>%s</a>'\
               % (self._url, targetstring, self._linktext)


class WebInterface(object):
    """
    Provides the web frontend and backend for the KM web interface.
    """
    def __init__(self, knowledge_manager, disabled):
        """
        knowledge_manager -- KM instance the web interface is bound to
        disabled -- whether the web interface should be disabled.
        """
        self.disabled = disabled
        self.km = knowledge_manager
        self.title = {}
        self.title['frontpage'] = "Pyphant Web Interface"
        self.html = {}
        self.html['disabled'] = "The Pyphant web interface is disabled."
        self.html['frontpage'] = "<h1>Pyphant Web Interface</h1>"
        self.html['kmurl'] = "Download DataContainer with ID '%s' as \
<a href=\"%s\">HDF5</a>"
        self.html['kmid'] = "KnowledgeManager server ID is: '%s'"

    def get_disabled(self):
        """
        Returns an HTTP answer stating that the interface is disabled.
        """
        return HTTPAnswer(200,
                          htmlheaders = {'title':self.title['frontpage']},
                          htmlbody = self.html['disabled'])

    def get_frontpage(self):
        """
        Returns an HTTP answer for the front page.
        """
        if self.disabled:
            return self.get_disabled()
        #TODO:
        return HTTPAnswer(200,
                          htmlheaders = {'title':self.title['frontpage']},
                          htmlbody = self.html['frontpage'])

    def get_kmurl(self, url, dc_id):
        """
        Returns an HTTP answer for DC url requests.
        url -- URL where to download the DC
        dc_id -- emd5 of the DC
        """
        if self.disabled:
            htmlbody = ""
        else:
            htmlbody =  self.html['kmurl'] % (dc_id, url)
        return HTTPAnswer(201,
                          None,
                          {'location':url},
                          'text/html',
                          {'pyphant':{'hdf5url':url},
                           'title':"DC ID '%s'" % (dc_id, )},
                          htmlbody)

    def get_kmid(self, km_id):
        """
        Returns an HTTP answer for KM ID requests.
        km_id -- KnowledgeManager server ID
        """
        if self.disabled:
            htmlbody = ""
        else:
            htmlbody = self.html['kmid'] % km_id
        return HTTPAnswer(200,
                          None,
                          {},
                          'text/html',
                          {'pyphant':{'kmid':km_id}},
                          htmlbody)

    def get_updatequery(self, query_dict):
        """
        Returns an HTTP answer with updated query dictionary.
        query_dict -- query dictionary
        """
        htmlheaders = {'pyphant':dict(query_dict)}
        htmlheaders['pyphant']['lastkmidindex']\
            = str(htmlheaders['pyphant']['lastkmidindex'])
        return HTTPAnswer(404,
                          "Query updated.",
                          {},
                          'text/html',
                          htmlheaders,
                          "",
                          False)

    def get_internalerror(self, excep):
        """
        Returns an HTTP answer in case of an internal error.
        excep -- exception that occured.
        """
        HTTPAnswer(500,
                   "Internal server error occured.\n\
Additional information: %s" % (excep.message, ))


class KMHTMLParser(HTMLParser.HTMLParser):
    """
    Helper class for the KnowledgeManager. This class provides HTML parsing for
    KnowledgeManager HTML anwsers.
    """
    def __init__(self):
        """
        Initializes the parser.
        """
        HTMLParser.HTMLParser.__init__(self)
        self._isinhead = False
        self._isinbody = False
        self.headitems = {} # tag : attributes
        self.bodytext = ''

    def handle_starttag(self, tag, attrs):
        """
        Handles the beginning of an HTML tag.
        """
        if tag == 'head':
            self._isinhead = True
        elif tag == 'body':
            self._isinbody = True
        elif self._isinhead:
            attrsdict = {}
            for pairs in attrs:
                attrsdict[pairs[0]] = pairs[1]
            self.headitems[tag] = attrsdict

    def handle_startendtag(self, tag, attrs):
        """
        Handles XHTML style tags.
        """
        if self._isinhead:
            attrsdict = {}
            for pairs in attrs:
                attrsdict[pairs[0]] = pairs[1]
            self.headitems[tag] = attrsdict

    def handle_endtag(self, tag):
        """
        Handles the end of an HTML tag.
        """
        if tag == 'head':
            self._isinhead = False
        elif tag == 'body':
            self._isinbody = False

    def handle_data(self, data):
        """
        Handles data between tags
        """
        if self._isinbody:
            self.bodytext += data


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """
    Threaded HTTP Server for the KnowledgeManager.
    """
    stop_server = False
    _logger = logging.getLogger("pyphant")

    def start(self):
        """
        Servers forever until stop_server is set to True.
        """
        while not self.stop_server:
            self.handle_request()
        self._logger.info("Stopped HTTP server.")
