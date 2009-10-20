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
from pyphant.core.KnowledgeManager import DCNotFoundError
from types import StringTypes
from pyphant.core.SQLiteWrapper import SQLiteWrapper


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
        return template('message', heading='Parameter Error',
                        message=verr.args[0], back_url='/')
    return True

def order_bar(keys, order_by, order_asc):
    keydict = dict([(key, key) for key in keys])
    extra = cond(order_asc, (" +", " -"))
    keydict[order_by] = "<i>%s</i>%s" % (order_by, extra) 
    return [HTMLJSButton(keydict[key],
                         "set_order_by('%s');" % key) for key in keys]
    

class HTMLLink():
    """
    This class provides HTML code for hyperlinks.
    """
    def __init__(self, url, linkobj, target = None):
        """
        url -- self explanatory
        linkobj -- obj the user sees to click on
        target -- link target, e.g. '_blank'
        """
        self._url = url
        self._linkobj = linkobj
        self._target = target

    def getHTML(self):
        """
        Returns the hyperlink as HTML code.
        """
        targetstring = ""
        if self._target != None:
            targetstring = ' target="%s"' % (self._target, )
        if hasattr(self._linkobj, 'getHTML'):
            linkhtml = self._linkobj.getHTML()
        else:
            linkhtml = str(self._linkobj)
        return '<a href="%s"%s>%s</a>'\
               % (self._url, targetstring, linkhtml)


class HTMLDropdown(object):
    def __init__(self, name, options, select=None, onchange=None):
        self.name = name
        self.options = options
        self.select = select
        self.onchange = onchange

    def getHTML(self):
        htmlopt = '    <option value="%s"%s>%s</option>\n'
        onchg = cond(self.onchange is None,
                     ('', 'onchange="%s"' % self.onchange))
        html = '<select name="%s" size="1" %s>\n' % (self.name, onchg)
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
                 cellspacing=0, cellpadding=4):
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


class HTMLJSButton(object):
    def __init__(self, tag, action):
        self.tag = tag
        self.action = action
        self.html = """<div onclick="%s" """\
                    """onmouseover="document.body.style.cursor='pointer';" """\
                    """onmouseout="document.body.style.cursor='default';"  """\
                    """><u>%s</u></div>"""

    def getHTML(self):
        return self.html % (self.action, self.tag)


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

class HTMLSummaryLink(HTMLLink):
    def __init__(self, emd5_tag):
        qry = urlencode({'id':emd5_tag[0]})
        HTMLLink.__init__(self, '/summary?' + qry, emd5_tag[1])


class HTMLFCScheme(object):
    def __init__(self, fc_id, kn):
        self.dom = kn.km.search(['shortname', 'latex_unit'],
                                {'type':'field', 'dim_of':fc_id})
        self.rng = kn.km.search(['shortname', 'latex_unit'],
                                {'type':'field', 'id':fc_id})[0]
        self.latex = '$%s$(%s)[%s]'
        self.html = """<pre class="LaTeX">%s</pre>"""

    def getSpaced(self):
        domstr = ''
        for shortname, unit in self.dom:
            domstr += "$%s$[%s],&nbsp;&nbsp;" % (shortname, unit)
        return self.latex  % (self.rng[0], domstr[:-13], self.rng[1])

    def getHTML(self):
        return self.html % self.getSpaced()


class HTMLSCScheme(object):
    def __init__(self, sc_id, kn):
        columns = kn.km.search(['id'], {'type':'field', 'col_of':sc_id})
        self.fc_schemes = [HTMLFCScheme(col[0], kn) for col in columns]
        self.shortname = kn.km.search(['shortname'], {'type':'sample',
                                                      'id':sc_id})[0][0]
        self.html = """<pre class="LaTeX">%s</pre>"""

    def getSpaced(self):
        lstr = '$%s$(' % self.shortname
        for fc_scheme in self.fc_schemes:
            lstr += fc_scheme.getSpaced() + ',&nbsp;&nbsp;'
        return lstr[:-13] + ')'

    def getHTML(self):
        return self.html % self.getSpaced()


class HTMLChildrenTable(HTMLTable):
    def __init__(self, dc_id, kn):
        child = cond(dc_id.endswith('field'), ('dim_of', 'col_of'))
        result = kn.km.search(
            ['id', 'longname'], {'type':'field', child:dc_id})
        rows = [[HTMLSummaryLink(res) for res in result]]
        HTMLTable.__init__(self, rows, headings=False)


class HTMLAttrTable(HTMLTable):
    def __init__(self, dc_id, kn):
        with SQLiteWrapper(kn.km.dbase) as wrapper:
            attrs = wrapper[dc_id]['attributes']
        rows = [('attribute', 'value')]
        rows.extend(attrs.items())
        HTMLTable.__init__(self, rows)


class WebInterface(object):
    """
    Web interface for the KnowledgeNode class.
    """

    anystr = '-- any --'

    def __init__(self, knowledge_node, enabled):
        """
        knowledge_node -- KN instance the web interface is bound to
        enabled -- whether the web interface should be enabled upon start.
        """
        self.enabled = enabled
        self.kn = knowledge_node
        from pyphant import __path__ as ppath
        self.rootdir = ppath[0] + '/web/'
        self.url_link = HTMLLink(self.kn.url, self.kn.url).getHTML()
        self.menu = HTMLTable(
            [[HTMLLink('/search', 'Browse Data Containers'),
              HTMLLink('/remotes/', 'Manage Remotes'),
              HTMLLink('/log/', 'Show Log')
              ]], headings=False, border=0).getHTML()
        self._setup_routes()

    def _setup_routes(self):
        self.kn.app.add_route('/', self.frontpage)
        self.kn.app.add_route('/images/:filename', self.images)
        self.kn.app.add_route('/remote_action', self.remote_action)
        self.kn.app.add_route('/favicon.ico', self.favicon)
        self.kn.app.add_route('/log/', self.log)
        self.kn.app.add_route('/remotes/', self.remotes)
        self.kn.app.add_route('/summary', self.summary)
        self.kn.app.add_route('/script/:filename', self.script)
        self.kn.app.add_route('/search', self.search)

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
        remote_table = HTMLTable(remote_rows)
        return template('remotes', remote_table=remote_table.getHTML())

    def images(self, filename):
        if not self.enabled:
            return template('disabled')
        send_file(filename, self.rootdir + 'images/', guessmime=False,
                  mimetype=self.kn.mimetypes.guess_type(filename)[0])

    def script(self, filename):
        if not self.enabled:
            return template('disabled')
        send_file(filename, self.rootdir + 'script/', guessmime=False,
                  mimetype='application/javascript')

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
        return self.remotes()

    def favicon(self):
        return self.images('favicon.ico')

    def log(self):
        if not self.enabled:
            return template('disabled')
        with open(getPyphantPath() + 'pyphant.log') as logfile:
            loglines = logfile.readlines()
        return template('log', loglines=''.join(loglines), url=self.url_link)

    def summary(self):
        if not self.enabled:
            return template('disabled')
        qry = request.GET
        val_id = validate_keys(['id'], qry)
        if not val_id is True:
            return val_id
        if qry['id'].endswith('.field'):
            return self.fieldcontainer(qry['id'])
        elif qry['id'].endswith('.sample'):
            return self.samplecontainer(qry['id'])
        else:
            return template(
                'message', heading='Parameter Error', back_url='/',
                message="Not an emd5: '%s'" % qry['id'])

    def common_summary(self, dc_id):
        dctype = cond(dc_id.endswith('field'), ('field', 'sample'))
        keys = ['machine', 'creator', 'date', 'hash', 'longname']
        result = self.kn.km.search(keys, {'type':dctype, 'id':dc_id})
        if result == []:
            raise DCNotFoundError(template(
                'message', heading='Parameter Error', back_url='/',
                message="Could not find data container '%s'" % dc_id))
        return zip(keys, result[0])

    def fieldcontainer(self, fc_id):
        try:
            common_rows = self.common_summary(fc_id)
        except DCNotFoundError, dcnferr:
            return dcnferr.args[0]
        rows = [['scheme', HTMLFCScheme(fc_id, self.kn)]]
        rows.extend(common_rows[:-1])
        rows.append(['dimensions', HTMLChildrenTable(fc_id, self.kn)])
        rows.append(['attributes', HTMLAttrTable(fc_id, self.kn)])
        htmlsumm = HTMLTable(rows, headings=False)
        return template('fieldcontainer', summary=htmlsumm,
                        longname=common_rows[4][1])

    def samplecontainer(self, sc_id):
        try:
            common_rows = self.common_summary(sc_id)
        except DCNotFoundError, dcnferr:
            return dcnferr.args[0]
        scheme = HTMLSCScheme(sc_id, self.kn)
        rows = [['scheme', scheme]]
        rows.extend(common_rows[:-1])
        rows.append(['columns', HTMLChildrenTable(sc_id, self.kn)])
        rows.append(['attributes', HTMLAttrTable(fc_id, self.kn)])
        htmlsumm = HTMLTable(rows, headings=False)
        return template('samplecontainer', summary=htmlsumm,
                        longname=common_rows[4][1])

    def search(self):
        if not self.enabled:
            return template('disabled')
        common_keys = ['type', 'machine', 'creator', 'longname', 'shortname']
        complete = dict([(key, self.anystr) for key in common_keys])
        complete.update({'order_by':'date', 'order_asc':'True', 'offset':'0',
                         'jump':'False'})
        qry = request.GET
        for key in complete:
            if not key in qry:
                qry[key] = complete[key]
        order_asc = (qry['order_asc'] == 'True')
        order_by = qry['order_by']
        body_onload = cond(
            qry['jump'] == 'True',
            (""" onload="window.location.hash='result_view';" """, ""))
        offset = int(qry['offset'])
        search_dict = dict([(key, qry[key]) for key in common_keys \
                            if qry[key] != self.anystr])
        optionss = [[(self.anystr, )] \
                    + self.kn.km.search([key], search_dict, distinct=True) \
                    for key in common_keys]
        rows = [common_keys]
        rows.append([HTMLDropdown(key, [opt[0] for opt in opts],
                                  qry[key], "document.search_form.submit();") \
                     for key, opts in zip(common_keys, optionss)])
        common = HTMLTable(rows).getHTML()
        missing_keys = ['date'] \
                       + [key for key in common_keys \
                          if qry[key] == self.anystr] \
                       + ['id']
        search_result = self.kn.km.search(
            missing_keys, search_dict, order_by=order_by,
            order_asc=order_asc, limit=-1, offset=offset)
        rows = [order_bar(missing_keys[:-1], order_by, order_asc) + ['details']]
        rows.extend([srow[:-1] + (HTMLSummaryLink((srow[-1], 'click')), ) \
                     for srow in search_result])
        result = HTMLTable(rows).getHTML()
        return template('search',
                        common=common,
                        attributes='attributes...',
                        special='special...',
                        result=result,
                        order_by=order_by,
                        order_asc=qry['order_asc'],
                        body_onload=body_onload)
