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
This module provides the WebInterface class for the KnowledgeNode
as well as some HTTP and HTML helper classes.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source: $

from types import DictType
from types import (DictType, ListType)
from pyphant.core.bottle import (template, send_file)
import pyphant.core.bottle

ALLSTRING = "*****ALL*****"


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
        self._setup_routes()

    def _setup_routes(self):
        self.kn.app.add_route('/', self.frontpage)
        self.kn.app.add_route('/images/:filename', self.images)

    def frontpage(self):
        if not self.enabled:
            return template('disabled')
        remote_rows = [['URL', 'UUID', 'Status']]
        for remote in self.kn.remotes:
            remote_rows.append([HTMLLink(remote.url, remote.url),
                                remote.uuid, remote.status])
        remote_table = HTMLTable(remote_rows, border=5)
        return template('frontpage',
                        local_url=HTMLLink(self.kn.url, self.kn.url).getHTML(),
                        local_uuid=self.kn.uuid,
                        remote_table=remote_table.getHTML())

    def images(self, filename):
        send_file(filename, self.rootdir + 'images/', guessmime=True)
