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
from cgi import parse_qs
import re
from types import (DictType, ListType)
ALLSTRING = "*****ALL*****"

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


class HTMLDropdown(object):
    def __init__(self, name, options, select = None):
        self.name = name
        self.options = options
        self.select = select

    def getHTML(self):
        htmlopt = '    <option value="%s"%s>%s</option>\n'
        html = '<select name="%s" size="1">\n' % (self.name, )
        for item in self.options:
            try:
                value, label = item
            except ValueError:
                value = item
                label = item
            selected = ""
            if value == self.select:
                selected = " selected"
            html += (htmlopt % (value, selected, label))
        html += '</select>\n'
        return html


class HTMLTextForm(object):
    def __init__(self, name, size, maxlength, value):
        self.name = name
        self.size = size
        self.maxlength = maxlength
        self.value = value
        self.html = '<input name="%s" type="text" size="%d" \
maxlength="%d" value="%s">'

    def getHTML(self):
        return self.html % (self.name, self.size, self.maxlength, self.value)


class HTMLTable(object):
    def __init__(self, rows, border = 1, headings = True):
        self.rows = rows
        self.border = border
        self.headings = headings

    def getHTML(self):
        if self.rows == []:
            return ""
        html = '<table border="%d">\n' % (self.border, )
        rowcount = 0
        for row in self.rows:
            html += '<tr>\n'
            tag = 'td'
            if rowcount == 0 and self.headings:
                tag = 'th'
            for cell in row:
                html += '<%s>' % (tag, )
                if hasattr(cell, 'getHTML'):
                    html += cell.getHTML()
                else:
                    html += str(cell)
                html += '</%s>\n' % (tag, )
            html += '</tr>\n'
            rowcount += 1
        html += '</table>\n'
        return html


class HTMLButton(object):
    def __init__(self, tag, action, method='post', hidden={}):
        self.tag = tag
        self.action = action
        self.method = method
        self.hidden = hidden
        self.html = \
"""
<form action="%s" method="%s">
    %s
    <input type="submit" value="%s">
</form>
"""
        self.hihtml = \
"""
<input type="hidden" name="%s" value="%s">
"""

    def getHTML(self):
        hidden = ""
        for key, value in self.hidden.iteritems():
            hidden += self.hihtml % (key, value)
        return self.html % (self.action, self.method, hidden, self.tag)


class HTMLDnldForm(HTMLButton):
    def __init__(self, dc_id):
        HTMLButton.__init__(self, " Download ", "/request_dc_url",
                            {"lastkmidindex": "-1",
                             "dcid": dc_id,
                             "mode": "enduser"})
        self.dc_id = dc_id

    def getHTML(self):
        self.hidden['dcid'] = self.dc_id
        return HTMLButton.getHTML(self)


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
        self.redt = re.compile(r'(\d{4,4})-(\d\d)-(\d\d)_(\d\d):(\d\d):(\d\d)')
        self.title = {}
        self.title['frontpage'] = "Pyphant Web Interface"
        self.title['details'] = "Details for DC with ID '%s'"
        self.html = {}
        self.html['disabled'] = "The Pyphant web interface is disabled."
        self.html['frontpage'] = """<h1>Pyphant Web Interface</h1>
Server ID is '%s'
<hr>
%s
<hr>
<h2>Registered KnowledgeManagers</h2>
%s
<hr>
<h2>Find DataContainers</h2>
%s
<hr>
<h2>Search matched %d out of %d DataContainers</h2>
%s
<hr>"""
        self.html['kmurl'] = "Download DataContainer with ID '%s' as \
<a href=\"%s\">HDF5</a><hr>Use the 'back' funtion of your browser to return."
        self.html['kmid'] = "KnowledgeManager server ID is: '%s'"
        self.html['findform'] = """<form action="/" method="get">
    Specify constraints for "and" search:
    <br>
    <br>
    %s
    <br>
    %s
    <br>
    <input type="hidden" name="dosearch" value="True">
    <input type="submit" value=" Find! ">
</form>"""
        self.html['datedescr'] = 'Specify constraints for the date. All input \
after YYYY is optional.<br>If any of the fields is left blank, this is \
interpreted as "no boundary"'

    def cmplower(self, left, right):
        return cmp(left.lower(), right.lower())

    def extract_values(self, dictionary, key):
        values = set()
        for subdict in dictionary.itervalues():
            try:
                value = subdict[key]
                values.add(value)
            except KeyError:
                pass
        return list(values)

    def get_disabled(self):
        """
        Returns an HTTP answer stating that the interface is disabled.
        """
        return HTTPAnswer(200,
                          htmlheaders = {'title':self.title['frontpage']},
                          htmlbody = self.html['disabled'])

    def get_detailslink(self, dc_id, text):
        return HTMLLink('/request_dc_details?dcid=%s' % (dc_id, ),
                        text,
                        '_blank')

    def get_frontpage(self, path):
        """
        Returns an HTTP answer for the front page.
        path -- GET request path
        """
        if self.disabled:
            return self.get_disabled()
        findrows = [['type', 'longname', 'shortname', 'creator', 'machine']]
        if path.startswith('/?'):
            query = parse_qs(path[2:])
        else:
            query = {}
        for key in findrows[0]:
            if not query.has_key(key):
                query[key] = [ALLSTRING]
        if not query.has_key('datefrom'):
            query['datefrom'] = ['']
        if not query.has_key('dateto'):
            query['dateto'] = ['']
        if not query.has_key('dosearch'):
            query['dosearch'] = ["False"]
        datelimit = [query['datefrom'][0], query['dateto'][0]]
        completestr = '-01-01_00:00:00'
        for index, date in enumerate(datelimit):
            if len(date) in [4, 7, 10, 13, 16]:
                date += completestr[len(date) - 4:]
                if index == 0:
                    query['datefrom'] = [date]
                else:
                    query['dateto'] = [date]
        #Registered KMs
        htmlregkm = '<form action="/request_register_km" method="post">'
        htmlregkm += HTMLTextForm("remote_km_host", 30, 1000, "host").getHTML()
        htmlregkm += HTMLTextForm("remote_km_port", 5, 5, "port").getHTML()
        htmlregkm += '<input type="submit" value=" Register! ">'
        htmlregkm += '</form><br>\n'
        if len(self.km._remoteKMs) != 0:
            kmrows = [['URL', 'ID']]
            for kmid, kmurl in self.km._remoteKMs.iteritems():
                kmrows.append([HTMLLink(kmurl, kmurl, "_blank"), kmid])
            kmtable = HTMLTable(kmrows)
            htmlregkm += kmtable.getHTML()
        else:
            htmlregkm += "None"
        #Find DCs
        summarydict = self.km.getSummary()
        tmprow = [self.extract_values(summarydict, key) for key in findrows[0]]
        dropdownrow = []
        for index, unsorted in enumerate(tmprow):
            unsorted.sort(self.cmplower)
            unsorted.insert(0, ALLSTRING)
            select = query[findrows[0][index]][0]
            dropdownrow.append(HTMLDropdown(findrows[0][index],
                                            unsorted, select))
        findrows.append(dropdownrow)
        findtable = HTMLTable(findrows)
        daterows = [['date', 'YYYY-MM-DD_hh:mm:ss'],
                    ['from', HTMLTextForm('datefrom', 19, 19,
                                          query['datefrom'][0])],
                    ['to', HTMLTextForm('dateto', 19, 19, query['dateto'][0])]]
        datetable = HTMLTable(daterows)
        descriptiontable = HTMLTable([[datetable, self.html['datedescr']]],
                                     0, False)
        htmlfindform = self.html['findform'] % (findtable.getHTML(),
                                                descriptiontable.getHTML())
        #Search Result
        htmlresult = ""
        results = 0
        sharpdc = len(summarydict)
        if query['dosearch'][0] == "True":
            datefrom = self.redt.match(query['datefrom'][0])
            if datefrom != None:
                datefrom = datefrom.groups()
            dateto = self.redt.match(query['dateto'][0])
            if dateto != None:
                dateto = dateto.groups()
            resrows = [['details', 'type', 'longname', 'shortname',
                        'creator', 'machine', 'date', 'data']]
            for summary in summarydict.itervalues():
                add = True
                for key in findrows[0]:
                    if query[key][0] != ALLSTRING:
                        add = add and summary[key] == query[key][0]
                dcdate = self.redt.match(summary['date'][:19])
                if dcdate == None:
                    add = False
                else:
                    dcdate = dcdate.groups()
                    if datefrom != None:
                        adddate = True
                        for index in range(len(datefrom)):
                            if int(datefrom[index]) < int(dcdate[index]):
                                adddate = True
                                break
                            elif int(datefrom[index]) > int(dcdate[index]):
                                adddate = False
                                break
                        add = add and adddate
                    if dateto != None:
                        adddate = True
                        for index in range(len(dateto)):
                            if int(dateto[index]) > int(dcdate[index]):
                                adddate = True
                                break
                            elif int(dateto[index]) < int(dcdate[index]):
                                adddate = False
                                break
                        add = add and adddate
                if add:
                    results += 1
                    row = [self.get_detailslink(summary['id'], 'show'),
                           summary['type'],
                           summary['longname'],
                           summary['shortname'],
                           summary['creator'],
                           summary['machine'],
                           summary['date'],
                           HTMLDnldForm(summary['id'])]
                    resrows.append(row)
            htmlresult = HTMLTable(resrows).getHTML()
        htmlrefresh = HTMLButton(" Refresh Knowledge ",
                                 "/request_refresh").getHTML()
        html = self.html['frontpage'] % (self.km.getServerId(),
                                         htmlrefresh,
                                         htmlregkm, htmlfindform,
                                         results, sharpdc, htmlresult)
        return HTTPAnswer(200,
                          htmlheaders = {'title':self.title['frontpage']},
                          htmlbody = html)

    def get_details(self, path):
        """
        Returns an HTTP answer for a detailed view of a DataContainer.
        path -- GET request path
        """
        dc_id = parse_qs(path.split('?')[1])['dcid'][0]
        html = "Details for DC with ID '%s'\n<hr>\n" % (dc_id, )
        try:
            summary = self.km.getSummary(dc_id).copy()
        except:
            msg = "DC ID '%s' not found." % (dc_id, )
            return HTTPAnswer(200,
                              htmlheaders = {'title':msg},
                              htmlbody = msg)
        def makeHTML(summ):
            if summ.has_key('attributes'):
                tmp = HTMLDict('attribute', 'value')
                tmp.setDict(summ['attributes'])
                summ['attributes'] = tmp
            if summ.has_key('columns'):
                tmp = HTMLTable([[self.get_detailslink(col['id'], \
col['longname']) for col in summ['columns']]], headings = False)
                summ['columns'] = tmp
            if summ.has_key('dimensions'):
                if isinstance(summ['dimensions'], ListType):
                    rows = []
                    for dim in summ['dimensions']:
                        try:
                            lnkid = dim['id']
                            row = [self.get_detailslink(lnkid, dim['longname'])]
                        except Exception:
                            row = [dim]
                        rows.append(row)
                    summ['dimensions'] = HTMLTable(rows, headings = False)
            tmp = HTMLDict('key', 'value')
            tmp.setDict(summ)
            return tmp
        summary = makeHTML(summary)
        html += summary.getHTML()
        return HTTPAnswer(200,
                          htmlheaders = {'title':self.title['details'] % dc_id},
                          htmlbody = html)

    def get_kmurl(self, url, dc_id, enduser = False):
        """
        Returns an HTTP answer for DC url requests.
        url -- URL where to download the DC
        dc_id -- emd5 of the DC
        enduser -- Whether the answer is to be send to an end user.
                   In that case the answer is a redirect to 'url'.
        """
        if enduser:
            code = 303
            htmlbody = self.html['kmurl'] % (dc_id, url)
        else:
            code = 201
            htmlbody = self.html['kmurl'] % (dc_id, url)
        return HTTPAnswer(code,
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
