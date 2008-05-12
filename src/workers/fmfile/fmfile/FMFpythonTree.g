tree grammar FMFpythonTree;
options {
    language=Python;
    tokenVocab=FMFpython;
    ASTLabelType=CommonTree;
}

@header {
import pkg_resources
pkg_resources.require("Pyphant")
from pyphant.core import DataContainer as DC
import numpy, datetime, math
import Scientific.Physics.PhysicalQuantities as PQ
}

dataContainer returns[ sampleContainer ]
    : config { $sampleContainer = DC.SampleContainer($config.fields, attributes=$config.attributes) }
    ;

config returns [attributes, fields]
@init {
$attributes = {}
}
    : ^(CONFIG referenceSection[$attributes] (commonSection[$attributes])* datadefSection dataSection[$datadefSection.coldefs])
       { $fields = $dataSection.fieldContainers }
    ;

referenceSection [attributes]
    : ^(COMMON_SECTION ^(HEADER ASTERISK 'reference') {atts = $attributes.setdefault(u'*reference', {})}
        ^(BODY (commonitem[atts])+))
    ;

commonSection [attributes]
    : ^(COMMON_SECTION ^(HEADER headername) {atts = $attributes.setdefault($headername.text, {})}
        ^(BODY (commonitem[atts])+))
    ;

headername: .*;

commonitem [attributes]
    : ^(ITEM ^(KEY (key+=.)+) {k = " ".join([k.getText() for k in list_key])} value) {attributes[k] = $value.v}
    ;
    
value returns [v]
    : ^(NUMBER number) {$v = $number.v}
    | ^(VARIABLE ^(IDENTIFIER identifier) quantity) {$v = ($identifier.text, $quantity.v)}
    | datetime {$v = $datetime.v}
    | ^(STRING catchall) {$v = $catchall.v}
    ;
    
catchall returns [v]
    : (acc+=~NEWLINE)* {$v = " ".join([a.getText() for a in list_acc])}
    ;

datetime returns [v]
    : ^(DATETIME ^(DATE date) {$v = $date.v} ^(TIME (time {$v = datetime.datetime.combine($v.date(), $time.v)})?))
    ;

date returns [v]
    : GERMANDATE {
try:
    $v = datetime.datetime.strptime($GERMANDATE.getText(), "\%d.\%m.\%Y")
except:
    $v = datetime.datetime.strptime($GERMANDATE.getText(), "\%d.\%m.\%y")
}
    | ISODATE {$v = datetime.datetime.strptime($ISODATE.getText(), "\%Y-\%m-\%d")}
    ;

time returns [v]
    : h=INT COLON m=INT (COLON s=FLOAT)? {
s = [int("0"+p) for p in s.getText().split('.')]
sec = s[0]
if len(s)==1:
    msec = 0
else:
    msec = s[1]
$v = datetime.time(int(h.getText()), int(m.getText()), sec, msec)
} 
    ;

quantity returns [v]
    : ^(QUANTITY ^(NUMBER number) {$v = $number.v} ^(UNIT (unit {$v = PQ.PhysicalQuantity($v, $unit.v.encode("utf-8"))})?)) 
    ;

number returns [v]
    : (PLUS|MINUS)? absnumber { $v = $absnumber.v }
    ;
    
fragment
absnumber returns [v]
options {
    backtrack=true;
}
        : FLOAT (PLUS|MINUS) IMAG { $v = complex($text) }
        | INT (PLUS|MINUS) IMAG { $v = complex($text) }
        | FLOAT {$v = float($text) }
        | INT { $v = int($text) }
        | IMAG {$v = complex($text) }
        ; 

datadefSection returns [coldefs]
@init {
$coldefs = []
}
    : ^(DATADEF_SECTION ^(HEADER ASTERISK 'data definitions') ^(BODY (colitem {$coldefs.append($colitem.coldef)})+))
    ;

colitem returns [coldef]
    : ^(COLSPEC ^(LONGNAME key=. {longname=key.getText()} (key=. {longname+=u" "+key.getText()})*) colspec) { $coldef = [longname] + $colspec.v }
    ;

colspec returns [v]
    : ^(IDENTIFIER identifier) ^(DEPS deps?) ^(UNIT unit?) {
rdeps = []
try:
    if $deps.v:
        rdeps = $deps.v
except AttributeError:
    pass
runit=1.0
try:
	if $unit.v != None:
        runit=$unit.v
except AttributeError:
    pass
$v = [$identifier.text, rdeps, runit]
}
    ;

unit returns [v]
    : un+=WORD (un+=(ASTERISK|DIV) un+=WORD)* {$v = "".join([u.getText() for u in list_un])}
    ;


identifier: WORD;
/*
identifier
        : WORD ( UNDERSCORE ((LCURLY WORD RCURLY) | WORD | INT)
               | HAT ((LCURLY WORD RCURLY) | WORD | INT)
               )? 
        ;
*/

deps returns [v]
@init {
$v = []
}
    : (identifier {
text = $identifier.text
if text[0]=='(' and text[-1]==')':
    text=text[1:-1]
$v.append(text)
})+
    ;


dataSection[coldefs] returns[fieldContainers]
@init {
fields = []
$fieldContainers = []
for i in xrange(0, len($coldefs)):
    fields.append([])
}
@after {
fieldDict = {}
for col, data in zip($coldefs, fields):
        fieldDict[col[1]]=DC.FieldContainer(numpy.array(data), col[3], longname=col[0], shortname=col[1])
for col in $coldefs:
    if len(col[2])>0:
        fieldDict[col[1]].dimensions = [ fieldDict[key] for key in col[2] ]
$fieldContainers = [fieldDict[cd[1]] for cd in $coldefs]
}
    : ^(DATA_SECTION ^(HEADER ASTERISK 'data') ^(BODY dataitem[fields]*))
    ;

dataitem [fields]
@init {
i = 0
}
    : ^(DATASET (cell
        {
fields[i].append($cell.v)
i += 1
        })* )
    ;

cell returns [v]
@init {
$v=u""
}
    : ^(NUMBER number) {$v = $number.v}
    | ^(STRING (string=. {$v += string.getText()})+)
    ;
