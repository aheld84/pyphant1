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

from __future__ import with_statement

"""
This module provides the WebInterface class for the KnowledgeNode
as well as some HTTP and HTML helper classes.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source: $

from types import DictType
from types import (DictType, ListType)
from pyphant.core.bottle import (template, send_file, request)
from pyphant.core.Helpers import getPyphantPath
from urllib import urlencode
from pyphant.core.KnowledgeNode import RemoteError
from types import StringTypes


def cond(condition, results):
    if condition:
        return results[0]
    else:
        return results[1]

def validate(value_validator_message_list):
    valid = True
    error_msg = ""
    for value, validator, message in value_validator_message_list:
        if not validator(value):
            valid = False
            if "%s" in message:
                message = message % value.__repr__()
            error_msg += "<p>%s</p>\n" % message
    if not valid:
        raise ValueError(error_msg)

def validate_keys(keys, mapping):
    try:
        validate([(k, lambda k: k in mapping, "Missing parameter: %s") \
                  for k in keys])
    except ValueError, verr:
        return template('message', heading='Value Error',
                        message=verr.args[0], back_url='/')
    return True


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
    def __init__(self, rows, border=1, headings=True,
                 cellspacing=0, cellpadding=0):
        self.rows = rows
        self.border = int(border)
        self.cellpadding = int(cellpadding)
        self.cellspacing = int(cellspacing)
        self.headings = headings

    def getHTML(self):
        if self.rows == []:
            return ""
        html = '<table border="%d" cellpadding="%d" cellspacing="%d">\n' \
               % (self.border, self.cellpadding, self.cellspacing)
        rowcount = 0
        for row in self.rows:
            html += '<tr>\n'
            tag = 'td'
            if rowcount == 0 and self.headings:
                tag = 'th'
            for cell in row:
                span = 1
                if isinstance(cell, tuple):
                    span = cell[1]
                    cell = cell[0]
                html += '<%s colspan="%d">' % (tag, span)
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

class HTMLImage(object):
    def __init__(self, src, width, height, alt):
        self.src = src
        self.width = width
        self.height = height
        self.alt = alt
        self.html = '<img src="%s" alt="%s" width="%d" height="%d" />'

    def getHTML(self):
        return self.html % (self.src, self.alt, self.width, self.height)


class HTMLStatus(object):
    def __init__(self, status):
        self.status = status

    def getHTML(self):
        return HTMLImage('/images/%s.gif' % self.status,
                         width=12, height=12, alt=self.status).getHTML()


class WebInterface(object):
    """
    Web interface for the KnowledgeNode class.
    """
    def __init__(self, knowledge_node, enabled):
        """
        knowledge_node -- KN instance the web interface is bound to
        enabled -- whether the web interface should be enabled upon start.
        """
        self.enabled = enabled
        self.kn = knowledge_node
        from pyphant import __path__ as ppath
        self.rootdir = ppath[0] + '/templates/'
        self.url_link = HTMLLink(self.kn.url, self.kn.url).getHTML()
        self.menu = HTMLTable(
            [['&#124;', HTMLLink('/remotes/', 'Manage Remotes'),
              '&#124;', HTMLLink('/log/', 'Show Log'),
              '&#124;']],
            border=0, cellspacing=2, cellpadding=2, headings=False).getHTML()
        self._setup_routes()

    def _setup_routes(self):
        self.kn.app.add_route('/', self.frontpage)
        self.kn.app.add_route('/images/:filename', self.images)
        self.kn.app.add_route('/remote_action', self.remote_action)
        self.kn.app.add_route('/favicon.ico', self.favicon)
        self.kn.app.add_route('/log/', self.log)
        self.kn.app.add_route('/remotes/', self.remotes)

    def frontpage(self):
        if not self.enabled:
            return template('disabled')
        return template('frontpage',
                        local_url=self.url_link,
                        local_uuid=self.kn.uuid[9:],
                        menu=self.menu)

    def remotes(self):
        if not self.enabled:
            return template('disabled')
        remote_rows = [[('URL', 2), 'UUID', ('Action', 2)]]
        for remote in self.kn.remotes:
            endisstr = cond(remote._status == 2, ('enable', 'disable'))
            qdict = {'host':remote.host, 'port':remote.port, 'action':endisstr}
            endis = HTMLLink('/remote_action?' + urlencode(qdict), endisstr)
            qdict['action'] = 'remove'
            rem = HTMLLink('/remote_action?' + urlencode(qdict), 'remove')
            uuid = remote.uuid
            if uuid != None:
                uuid = uuid[9:]
            remote_rows.append([HTMLStatus(remote.status),
                                HTMLLink(remote.url, remote.url),
                                uuid, endis, rem])
        remote_table = HTMLTable(remote_rows, border=2,
                                 cellspacing=2, cellpadding=2)
        return template('remotes', remote_table=remote_table.getHTML())

    def images(self, filename):
        if not self.enabled:
            return template('disabled')
        send_file(filename, self.rootdir + 'images/', guessmime=False,
                  mimetype=self.kn.mimetypes.guess_type(filename)[0])

    def remote_action(self):
        if not self.enabled:
            return template('disabled')
        qry = request.GET
        action_dict = {'enable':self.kn.enable_remote,
                       'disable':self.kn.disable_remote,
                       'remove':self.kn.remove_remote,
                       'add':self.kn.register_remote}
        valk = validate_keys(['host', 'port', 'action'], qry)
        if not valk is True:
            return valk
        try:
            validate([(qry['port'],
                       lambda p: p.isdigit() and int(p) < 65536,
                       "Parameter 'port' has to be between 0 and 65535."),
                      (qry['action'],
                       lambda a: a in action_dict,
                       "Invalid value for parameter 'action': %s")]
                     )
        except ValueError, valerr:
            return template('message', heading='Parameter Error',
                            message=valerr.args[0], back_url='/remotes/')
        port = int(qry['port'])
        try:
            action_dict[qry['action']](qry['host'], port)
        except RemoteError, remerr:
            return template('message', heading='Error', message=remerr.args[0],
                            back_url='/remotes/')
        return template('message', heading='Remote action',
                        message="Successfully performed action.",
                        back_url='/remotes/')

    def favicon(self):
        return self.images('favicon.ico')

    def log(self):
        if not self.enabled:
            return template('disabled')
        with open(getPyphantPath() + 'pyphant.log') as logfile:
            loglines = logfile.readlines()
        return template('log', loglines=''.join(loglines), url=self.url_link)
