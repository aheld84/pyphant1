# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
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
TODO
"""
__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$:

import xml.sax


class XMLElement(object):

    def __init__(self, name, attrs, parent, content=''):
        self.name = name
        self.attributes = attrs
        self.parent = parent
        self.children = {}
        self.content = content
        if parent != None:
            parent[name] = self

    def __getitem__(self, key):
        return self.children[key]

    def __setitem__(self, key, item):
        self.children[key] = item


class XMLHandler(xml.sax.handler.ContentHandler):

    def __init__(self):
        self.current_element = None
        self.root_element = None

    def startElement(self, name, attrs):
        if self.root_element == None:
            element = XMLElement(name, attrs, None)
            self.root_element = element
            self.current_element = element
        else:
            element = XMLElement(name, attrs, self.current_element)
            self.current_element = element

    def endElement(self, name):
        assert name == self.current_element.name
        self.current_element = self.current_element.parent

    def characters(self, content):
        if self.current_element != None:
            self.current_element.content += content


def getXMLRoot(filename_or_stream):
    handler = XMLHandler()
    xml.sax.parse(filename_or_stream, handler)
    return handler.root_element
