#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
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

"""usage = "usage: %prog [options] archivename"

Converts ZIP or TAR archives to the Full Metadata File (FMF) format. The input archive has to contain either absorption measurements (Riede-INI) or simulated absorption curves (KSH-INI).

Example file header for KSH-INI:

[GLOBAL]
AUTHOR=Kristian O. Sylvester-Hvid
DATE=2007-12-07
TITLE=Simulated abs spectrum for P3HT:PCBM solar cell - 40nm blend layer
[SPALTENBESCHRIFTUNG]
SPALTE1=Wavelength[nm]
SPALTE2=Absorption[]
[MESSDATEN]
300 0.9399939
302 0.94043474


Example file header for Riede-INI:

[GLOBAL]
SUBSTRAT_TYP=T_norm-Space-resolved
SUBSTRAT_NAME=T00039
PIXEL=9
DATUM=26.10.2007
UHRZEIT=16:51:09
OPERATOR=KSH
HALTER=Space_resolved_T_norm
SUBSTRAT_POSITION=2
TISCH_POS_X=74.3000
TISCH_POS_Y=45.0000
FILTERRAD=<ohne>
KOMMENTAR="Absorption measurement of annealed (150C, 15min) T39 with inverted Al reference"
BELEUCHTUNG=0.0000E+0
MESSMODUL=ABS
RELAIS=<keine>
KOMMENTAR_PIXEL=" "
BATCHNUMBER=3276253246
LAMPE=<keine>
REFZELLE=<keine>
REF_CURRENT=0.0000E+0
[MESSUNG]
INTEGRATION_TIME=50
SCANS=10
CORRECT_DYNAMIC_DARK=1
FORGET_PERCENTAGE=100
SATURATION_DETECTION=0
SMOOTH_PIXEL=1
[SPALTENBESCHRIFTUNG]
SPALTE1=Wellenlänge[nm]
SPALTE2=ScopRaw[counts]
SPALTE3=Unkorrigierte Reflexion[counts]
SPALTE4=DarkRef[counts]
SPALTE5=WhiteRef[counts]
[MESSDATEN]
276.1833E+0	257.1975E+0	3.4475E+0	309.2355E+0	294.1412E+0
276.7759E+0	98.5742E+0	-295.3656E-3	114.5368E+0	168.5804E+0
"""
import tarfile,zipfile
import re
import datetime
import StringIO
from optparse import OptionParser
import platform,os
import pyphant.core.Helpers

parser= OptionParser(__doc__)
parser.add_option("-i", "--input-format", dest="iniFormat",default='RiedeINI',
                  help="FORMAT of input data (default is RiedeINI)", metavar="FORMAT",
                  choices=('RiedeINI','KSH-INI'))
(options, args) = parser.parse_args()
archiveName = args[0]
iniFormat = options.iniFormat
print "Converting %s from %s format to Full Metadata File format." % (archiveName,iniFormat)


class archive:
    def __init__(self, archiveName):
        if archiveName.endswith('tar'):
            self.type = 'TAR'
            self.archiveIN = tarfile.TarFile(archiveName)
        elif archiveName.endswith('zip'):
            self.type = 'ZIP'
            self.archiveIN = zipfile.ZipFile(archiveName)

    def names(self):
        if self.type == 'TAR':
            return [item.name for item in self.archiveIN]
        elif self.type == 'ZIP':
            return self.archiveIN.namelist()

    def extractedfile(self,filename):
        if self.type == 'TAR':
            datfile = self.archiveIN.extractfile(filename)
            return datfile.readlines()
        elif self.type == 'ZIP':
            datfile = self.archiveIN.read(filename)
            return StringIO.StringIO(datfile)

    def close(self):
        self.archiveIN.close()

searcher = re.compile("Sim_abs_(\d+)(\w+).dat")
archiveIN = archive(archiveName)

zip = zipfile.ZipFile(archiveName[:-4]+'_patched.zip','w')

def annotation():
    stream = ''
    stream += 'patched date: %s\n' % modDate
    stream += 'patched by: %s\n' % pyphant.core.Helpers.getUsername()
    stream += 'place: Freiburg i. Brsg.\n'
    stream += 'organization: Freiburger Materialforschungszentrum (FMF)\n'
    return stream

for datInfo in archiveIN.names():
    modDate = datetime.datetime.now()
    if iniFormat == 'RiedeINI':
        stream = ''
    elif iniFormat == 'KSH-INI':
        stream = "; -*- coding: utf-8 -*-\n"
#    datFile = archiveIN.extractfile(datInfo)
    width = searcher.match(datInfo)
    modus = None
    x = None
    y = None
    for line in archiveIN.extractedfile(datInfo):
        if line.startswith('[GLOBAL]'):
            line = '[*reference]\n'
        elif line.startswith('[SPALTENBESCHRIFTUNG]'):
            line = '[*data definitions]\n'
        elif line.startswith('[MESSDATEN]'):
            modus = '*data'
            line = '[*data]\n'
        elif line.startswith('SPALTE1'):
            line = 'wavelength: \\lambda [nm]\n'
        if iniFormat == 'RiedeINI':
            if line.startswith('TITLE'):
                stream += annotation()
                stream += "WIDTH=%s %s\n" % width.groups()
            elif line.startswith('SPALTE2'):
                line = 'scope raw intensity: I(\\lambda)\n'
            elif line.startswith('SPALTE3'):
                line = 'uncorrected reflexion: R(\\lambda)\n'
            elif line.startswith('SPALTE4'):
                line = 'dark reference intensity: I_d(\\lambda)\n'
            elif line.startswith('SPALTE5'):
                line = 'white reference intensity: I_0(\\lambda)\n'
            elif not line.startswith('['):
                words = line.split('=')
                if len(words)>1:
                    line = "%s: %s" % (words[0].lower().replace(' ','-'),words[1])
            if line.startswith('tisch_pos_x'):
                x = line.split(':')[1][:-2]
                line = 'horizontal_table_position: x = %s mm\n' % x
            if line.startswith('tisch_pos_y'):
                y = line.split(':')[1][:-2]
                line = 'vertical_table_position: y = %s mm\n' % y
            if line.startswith('kommentar:'):
                stream += annotation()
                line = 'title: %s at (x,y)=(%s,%s)\"\n' % (line.split(':')[1][1:-3],x,y)
        elif iniFormat == 'KSH-INI':
            if line.startswith('AUTHOR') or line.startswith('OPERATOR'):
                line = 'author: %s\n' % line.split('=')[1][:-2]
            elif line.startswith('TITLE'):
                stream += annotation()
                stream += "thickness: h = %s %s\n" % width.groups()
            elif line.startswith('SPALTE2'):
                line = 'absorption: A(\\lambda)\n'
        line = line.replace('<','').replace('>','').replace('\x0d','')
        line = line.replace('\" \"','ohne')
        stream += line
    info=zipfile.ZipInfo(datInfo,date_time=modDate.utctimetuple()[:6])
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 2175008768L
    if iniFormat == 'RiedeINI':
        zip.writestr(info,stream.encode('cp1252'))
    elif iniFormat == 'KSH-INI':
        zip.writestr(info,stream.encode('utf-8'))
archiveIN.close()
zip.close()
