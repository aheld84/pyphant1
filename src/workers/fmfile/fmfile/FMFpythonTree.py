# $ANTLR 3.0.1 FMFpythonTree.g 2008-04-03 08:14:09

from antlr3 import *
from antlr3.tree import *
from antlr3.compat import set, frozenset

import pkg_resources
pkg_resources.require("Pyphant")
from pyphant.core import DataContainer as DC
import numpy, datetime, math
import Scientific.Physics.PhysicalQuantities as PQ



# for convenience in actions
HIDDEN = BaseRecognizer.HIDDEN

# token types
PUNCTUATION=62
DOLLAR=45
EXPONENT=51
LBRACK=28
RWORD=60
ESC=54
DIGITS=49
DATA_SECTION=8
EQUALS=34
FLOAT=57
EOF=-1
ASTERISK=32
LPAREN=30
QUANTITY=19
DATASET=11
LONGNAME=23
WORD=61
HAT=43
TIME=15
RPAREN=31
COMMON_SECTION=6
IDENTIFIER=18
DEPS=24
PLUS=35
BODY=9
DIGIT=37
HEADER=5
COMMENT=27
GREATERTHAN=48
RBRACK=29
LESSTHAN=47
ITEM=10
ISODATE=56
KEY=12
DATETIME=13
NUMBER=16
LITERAL=63
LCURLY=40
UNDERSCORE=42
INT=58
MINUS=38
LETTERS=50
PERCENTAGE=46
IINT=53
GERMANDATE=55
COLON=33
NMINUS=39
CONFIG=4
UNIT=20
WS=26
NEWLINE=25
VARIABLE=17
NPLUS=36
FFLOAT=52
RCURLY=41
DATADEF_SECTION=7
COLSPEC=22
DIV=44
DATE=14
STRING=21
IMAG=59

# token names
tokenNames = [
    "<invalid>", "<EOR>", "<DOWN>", "<UP>",
    "CONFIG", "HEADER", "COMMON_SECTION", "DATADEF_SECTION", "DATA_SECTION",
    "BODY", "ITEM", "DATASET", "KEY", "DATETIME", "DATE", "TIME", "NUMBER",
    "VARIABLE", "IDENTIFIER", "QUANTITY", "UNIT", "STRING", "COLSPEC", "LONGNAME",
    "DEPS", "NEWLINE", "WS", "COMMENT", "LBRACK", "RBRACK", "LPAREN", "RPAREN",
    "ASTERISK", "COLON", "EQUALS", "PLUS", "NPLUS", "DIGIT", "MINUS", "NMINUS",
    "LCURLY", "RCURLY", "UNDERSCORE", "HAT", "DIV", "DOLLAR", "PERCENTAGE",
    "LESSTHAN", "GREATERTHAN", "DIGITS", "LETTERS", "EXPONENT", "FFLOAT",
    "IINT", "ESC", "GERMANDATE", "ISODATE", "FLOAT", "INT", "IMAG", "RWORD",
    "WORD", "PUNCTUATION", "LITERAL", "'reference'", "'data definitions'",
    "'data'", "','"
]



class FMFpythonTree(TreeParser):
    grammarFileName = "FMFpythonTree.g"
    tokenNames = tokenNames

    def __init__(self, input):
        TreeParser.__init__(self, input)
        self.ruleMemo = {}








    # $ANTLR start dataContainer
    # FMFpythonTree.g:16:1: dataContainer returns [ sampleContainer ] : config ;
    def dataContainer(self, ):

        sampleContainer = None

        config1 = None


        try:
            try:
                # FMFpythonTree.g:17:5: ( config )
                # FMFpythonTree.g:17:7: config
                self.following.append(self.FOLLOW_config_in_dataContainer56)
                config1 = self.config()
                self.following.pop()
                if self.failed:
                    return sampleContainer
                if self.backtracking == 0:
                    sampleContainer = DC.SampleContainer(config1.fields, attributes=config1.attributes)





            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return sampleContainer

    # $ANTLR end dataContainer

    class config_return(object):
        def __init__(self):
            self.start = None
            self.stop = None
            self.tree = None

            self.attributes = None
            self.fields = None


    # $ANTLR start config
    # FMFpythonTree.g:20:1: config returns [attributes, fields] : ^( CONFIG referenceSection[$attributes] ( commonSection[$attributes] )* datadefSection dataSection[$datadefSection.coldefs] ) ;
    def config(self, ):

        retval = self.config_return()
        retval.start = self.input.LT(1)

        datadefSection2 = None

        dataSection3 = None



        retval.attributes = {}

        try:
            try:
                # FMFpythonTree.g:24:5: ( ^( CONFIG referenceSection[$attributes] ( commonSection[$attributes] )* datadefSection dataSection[$datadefSection.coldefs] ) )
                # FMFpythonTree.g:24:7: ^( CONFIG referenceSection[$attributes] ( commonSection[$attributes] )* datadefSection dataSection[$datadefSection.coldefs] )
                self.match(self.input, CONFIG, self.FOLLOW_CONFIG_in_config85)
                if self.failed:
                    return retval

                self.match(self.input, DOWN, None)
                if self.failed:
                    return retval
                self.following.append(self.FOLLOW_referenceSection_in_config87)
                self.referenceSection(retval.attributes)
                self.following.pop()
                if self.failed:
                    return retval
                # FMFpythonTree.g:24:46: ( commonSection[$attributes] )*
                while True: #loop1
                    alt1 = 2
                    LA1_0 = self.input.LA(1)

                    if (LA1_0 == COMMON_SECTION) :
                        alt1 = 1


                    if alt1 == 1:
                        # FMFpythonTree.g:24:47: commonSection[$attributes]
                        self.following.append(self.FOLLOW_commonSection_in_config91)
                        self.commonSection(retval.attributes)
                        self.following.pop()
                        if self.failed:
                            return retval


                    else:
                        break #loop1


                self.following.append(self.FOLLOW_datadefSection_in_config96)
                datadefSection2 = self.datadefSection()
                self.following.pop()
                if self.failed:
                    return retval
                self.following.append(self.FOLLOW_dataSection_in_config98)
                dataSection3 = self.dataSection(datadefSection2)
                self.following.pop()
                if self.failed:
                    return retval

                self.match(self.input, UP, None)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    retval.fields = dataSection3





            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end config


    # $ANTLR start referenceSection
    # FMFpythonTree.g:28:1: referenceSection[attributes] : ^( COMMON_SECTION ^( HEADER ASTERISK 'reference' ) ^( BODY ( commonitem[atts] )+ ) ) ;
    def referenceSection(self, attributes):

        try:
            try:
                # FMFpythonTree.g:29:5: ( ^( COMMON_SECTION ^( HEADER ASTERISK 'reference' ) ^( BODY ( commonitem[atts] )+ ) ) )
                # FMFpythonTree.g:29:7: ^( COMMON_SECTION ^( HEADER ASTERISK 'reference' ) ^( BODY ( commonitem[atts] )+ ) )
                self.match(self.input, COMMON_SECTION, self.FOLLOW_COMMON_SECTION_in_referenceSection129)
                if self.failed:
                    return

                self.match(self.input, DOWN, None)
                if self.failed:
                    return
                self.match(self.input, HEADER, self.FOLLOW_HEADER_in_referenceSection132)
                if self.failed:
                    return

                self.match(self.input, DOWN, None)
                if self.failed:
                    return
                self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_referenceSection134)
                if self.failed:
                    return
                self.match(self.input, 64, self.FOLLOW_64_in_referenceSection136)
                if self.failed:
                    return

                self.match(self.input, UP, None)
                if self.failed:
                    return
                if self.backtracking == 0:
                    atts = attributes.setdefault(u'*reference', {})

                self.match(self.input, BODY, self.FOLLOW_BODY_in_referenceSection150)
                if self.failed:
                    return

                self.match(self.input, DOWN, None)
                if self.failed:
                    return
                # FMFpythonTree.g:30:16: ( commonitem[atts] )+
                cnt2 = 0
                while True: #loop2
                    alt2 = 2
                    LA2_0 = self.input.LA(1)

                    if (LA2_0 == ITEM) :
                        alt2 = 1


                    if alt2 == 1:
                        # FMFpythonTree.g:30:17: commonitem[atts]
                        self.following.append(self.FOLLOW_commonitem_in_referenceSection153)
                        self.commonitem(atts)
                        self.following.pop()
                        if self.failed:
                            return


                    else:
                        if cnt2 >= 1:
                            break #loop2

                        if self.backtracking > 0:
                            self.failed = True
                            return

                        eee = EarlyExitException(2, self.input)
                        raise eee

                    cnt2 += 1



                self.match(self.input, UP, None)
                if self.failed:
                    return

                self.match(self.input, UP, None)
                if self.failed:
                    return




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return

    # $ANTLR end referenceSection


    # $ANTLR start commonSection
    # FMFpythonTree.g:33:1: commonSection[attributes] : ^( COMMON_SECTION ^( HEADER headername ) ^( BODY ( commonitem[atts] )+ ) ) ;
    def commonSection(self, attributes):

        headername4 = None


        try:
            try:
                # FMFpythonTree.g:34:5: ( ^( COMMON_SECTION ^( HEADER headername ) ^( BODY ( commonitem[atts] )+ ) ) )
                # FMFpythonTree.g:34:7: ^( COMMON_SECTION ^( HEADER headername ) ^( BODY ( commonitem[atts] )+ ) )
                self.match(self.input, COMMON_SECTION, self.FOLLOW_COMMON_SECTION_in_commonSection178)
                if self.failed:
                    return

                self.match(self.input, DOWN, None)
                if self.failed:
                    return
                self.match(self.input, HEADER, self.FOLLOW_HEADER_in_commonSection181)
                if self.failed:
                    return

                if self.input.LA(1) == DOWN:
                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return
                    self.following.append(self.FOLLOW_headername_in_commonSection183)
                    headername4 = self.headername()
                    self.following.pop()
                    if self.failed:
                        return

                    self.match(self.input, UP, None)
                    if self.failed:
                        return

                if self.backtracking == 0:
                    atts = attributes.setdefault(self.input.getTokenStream().toString(
                        self.input.getTreeAdaptor().getTokenStartIndex(headername4.start),
                        self.input.getTreeAdaptor().getTokenStopIndex(headername4.start)
                        ), {})

                self.match(self.input, BODY, self.FOLLOW_BODY_in_commonSection197)
                if self.failed:
                    return

                self.match(self.input, DOWN, None)
                if self.failed:
                    return
                # FMFpythonTree.g:35:16: ( commonitem[atts] )+
                cnt3 = 0
                while True: #loop3
                    alt3 = 2
                    LA3_0 = self.input.LA(1)

                    if (LA3_0 == ITEM) :
                        alt3 = 1


                    if alt3 == 1:
                        # FMFpythonTree.g:35:17: commonitem[atts]
                        self.following.append(self.FOLLOW_commonitem_in_commonSection200)
                        self.commonitem(atts)
                        self.following.pop()
                        if self.failed:
                            return


                    else:
                        if cnt3 >= 1:
                            break #loop3

                        if self.backtracking > 0:
                            self.failed = True
                            return

                        eee = EarlyExitException(3, self.input)
                        raise eee

                    cnt3 += 1



                self.match(self.input, UP, None)
                if self.failed:
                    return

                self.match(self.input, UP, None)
                if self.failed:
                    return




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return

    # $ANTLR end commonSection

    class headername_return(object):
        def __init__(self):
            self.start = None
            self.stop = None
            self.tree = None



    # $ANTLR start headername
    # FMFpythonTree.g:38:1: headername : ( . )* ;
    def headername(self, ):

        retval = self.headername_return()
        retval.start = self.input.LT(1)

        try:
            try:
                # FMFpythonTree.g:38:11: ( ( . )* )
                # FMFpythonTree.g:38:13: ( . )*
                # FMFpythonTree.g:38:13: ( . )*
                while True: #loop4
                    alt4 = 2
                    LA4_0 = self.input.LA(1)

                    if (LA4_0 == 3) :
                        alt4 = 2
                    elif ((CONFIG <= LA4_0 <= 67)) :
                        alt4 = 1


                    if alt4 == 1:
                        # FMFpythonTree.g:38:13: .
                        self.matchAny(self.input)
                        if self.failed:
                            return retval


                    else:
                        break #loop4






            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end headername


    # $ANTLR start commonitem
    # FMFpythonTree.g:40:1: commonitem[attributes] : ^( ITEM ^( KEY (key+= . )+ ) value ) ;
    def commonitem(self, attributes):

        key = None
        list_key = None
        value5 = None


        try:
            try:
                # FMFpythonTree.g:41:5: ( ^( ITEM ^( KEY (key+= . )+ ) value ) )
                # FMFpythonTree.g:41:7: ^( ITEM ^( KEY (key+= . )+ ) value )
                self.match(self.input, ITEM, self.FOLLOW_ITEM_in_commonitem233)
                if self.failed:
                    return

                self.match(self.input, DOWN, None)
                if self.failed:
                    return
                self.match(self.input, KEY, self.FOLLOW_KEY_in_commonitem236)
                if self.failed:
                    return

                self.match(self.input, DOWN, None)
                if self.failed:
                    return
                # FMFpythonTree.g:41:20: (key+= . )+
                cnt5 = 0
                while True: #loop5
                    alt5 = 2
                    LA5_0 = self.input.LA(1)

                    if ((CONFIG <= LA5_0 <= 67)) :
                        alt5 = 1


                    if alt5 == 1:
                        # FMFpythonTree.g:41:21: key+= .
                        key = self.input.LT(1)
                        self.matchAny(self.input)
                        if self.failed:
                            return
                        if list_key is None:
                            list_key = []
                        list_key.append(key)



                    else:
                        if cnt5 >= 1:
                            break #loop5

                        if self.backtracking > 0:
                            self.failed = True
                            return

                        eee = EarlyExitException(5, self.input)
                        raise eee

                    cnt5 += 1



                self.match(self.input, UP, None)
                if self.failed:
                    return
                if self.backtracking == 0:
                    k = " ".join([k.getText() for k in list_key])

                self.following.append(self.FOLLOW_value_in_commonitem248)
                value5 = self.value()
                self.following.pop()
                if self.failed:
                    return

                self.match(self.input, UP, None)
                if self.failed:
                    return
                if self.backtracking == 0:
                    attributes[k] = value5





            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return

    # $ANTLR end commonitem


    # $ANTLR start value
    # FMFpythonTree.g:44:1: value returns [v] : ( ^( NUMBER number ) | ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime | ^( STRING catchall ) );
    def value(self, ):

        v = None

        number6 = None

        identifier7 = None

        quantity8 = None

        datetime9 = None

        catchall10 = None


        try:
            try:
                # FMFpythonTree.g:45:5: ( ^( NUMBER number ) | ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime | ^( STRING catchall ) )
                alt6 = 4
                LA6 = self.input.LA(1)
                if LA6 == NUMBER:
                    alt6 = 1
                elif LA6 == VARIABLE:
                    alt6 = 2
                elif LA6 == DATETIME:
                    alt6 = 3
                elif LA6 == STRING:
                    alt6 = 4
                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return v

                    nvae = NoViableAltException("44:1: value returns [v] : ( ^( NUMBER number ) | ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime | ^( STRING catchall ) );", 6, 0, self.input)

                    raise nvae

                if alt6 == 1:
                    # FMFpythonTree.g:45:7: ^( NUMBER number )
                    self.match(self.input, NUMBER, self.FOLLOW_NUMBER_in_value277)
                    if self.failed:
                        return v

                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return v
                    self.following.append(self.FOLLOW_number_in_value279)
                    number6 = self.number()
                    self.following.pop()
                    if self.failed:
                        return v

                    self.match(self.input, UP, None)
                    if self.failed:
                        return v
                    if self.backtracking == 0:
                        v = number6



                elif alt6 == 2:
                    # FMFpythonTree.g:46:7: ^( VARIABLE ^( IDENTIFIER identifier ) quantity )
                    self.match(self.input, VARIABLE, self.FOLLOW_VARIABLE_in_value291)
                    if self.failed:
                        return v

                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return v
                    self.match(self.input, IDENTIFIER, self.FOLLOW_IDENTIFIER_in_value294)
                    if self.failed:
                        return v

                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return v
                    self.following.append(self.FOLLOW_identifier_in_value296)
                    identifier7 = self.identifier()
                    self.following.pop()
                    if self.failed:
                        return v

                    self.match(self.input, UP, None)
                    if self.failed:
                        return v
                    self.following.append(self.FOLLOW_quantity_in_value299)
                    quantity8 = self.quantity()
                    self.following.pop()
                    if self.failed:
                        return v

                    self.match(self.input, UP, None)
                    if self.failed:
                        return v
                    if self.backtracking == 0:
                        v = (self.input.getTokenStream().toString(
                            self.input.getTreeAdaptor().getTokenStartIndex(identifier7.start),
                            self.input.getTreeAdaptor().getTokenStopIndex(identifier7.start)
                            ), quantity8)



                elif alt6 == 3:
                    # FMFpythonTree.g:47:7: datetime
                    self.following.append(self.FOLLOW_datetime_in_value310)
                    datetime9 = self.datetime()
                    self.following.pop()
                    if self.failed:
                        return v
                    if self.backtracking == 0:
                        v = datetime9



                elif alt6 == 4:
                    # FMFpythonTree.g:48:7: ^( STRING catchall )
                    self.match(self.input, STRING, self.FOLLOW_STRING_in_value321)
                    if self.failed:
                        return v

                    if self.input.LA(1) == DOWN:
                        self.match(self.input, DOWN, None)
                        if self.failed:
                            return v
                        self.following.append(self.FOLLOW_catchall_in_value323)
                        catchall10 = self.catchall()
                        self.following.pop()
                        if self.failed:
                            return v

                        self.match(self.input, UP, None)
                        if self.failed:
                            return v

                    if self.backtracking == 0:
                        v = catchall10




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end value


    # $ANTLR start catchall
    # FMFpythonTree.g:51:1: catchall returns [v] : (acc+=~ NEWLINE )* ;
    def catchall(self, ):

        v = None

        acc = None
        list_acc = None

        try:
            try:
                # FMFpythonTree.g:52:5: ( (acc+=~ NEWLINE )* )
                # FMFpythonTree.g:52:7: (acc+=~ NEWLINE )*
                # FMFpythonTree.g:52:7: (acc+=~ NEWLINE )*
                while True: #loop7
                    alt7 = 2
                    LA7_0 = self.input.LA(1)

                    if ((CONFIG <= LA7_0 <= DEPS) or (WS <= LA7_0 <= 67)) :
                        alt7 = 1


                    if alt7 == 1:
                        # FMFpythonTree.g:52:8: acc+=~ NEWLINE
                        acc = self.input.LT(1)
                        if (CONFIG <= self.input.LA(1) <= DEPS) or (WS <= self.input.LA(1) <= 67):
                            self.input.consume();
                            self.errorRecovery = False
                            self.failed = False

                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return v

                            mse = MismatchedSetException(None, self.input)
                            self.recoverFromMismatchedSet(
                                self.input, mse, self.FOLLOW_set_in_catchall354
                                )
                            raise mse


                        if list_acc is None:
                            list_acc = []
                        list_acc.append(acc)



                    else:
                        break #loop7


                if self.backtracking == 0:
                    v = " ".join([a.getText() for a in list_acc])





            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end catchall


    # $ANTLR start datetime
    # FMFpythonTree.g:55:1: datetime returns [v] : ^( DATETIME ^( DATE date ) ^( TIME ( time )? ) ) ;
    def datetime(self, ):

        v = None

        date11 = None

        time12 = None


        try:
            try:
                # FMFpythonTree.g:56:5: ( ^( DATETIME ^( DATE date ) ^( TIME ( time )? ) ) )
                # FMFpythonTree.g:56:7: ^( DATETIME ^( DATE date ) ^( TIME ( time )? ) )
                self.match(self.input, DATETIME, self.FOLLOW_DATETIME_in_datetime381)
                if self.failed:
                    return v

                self.match(self.input, DOWN, None)
                if self.failed:
                    return v
                self.match(self.input, DATE, self.FOLLOW_DATE_in_datetime384)
                if self.failed:
                    return v

                self.match(self.input, DOWN, None)
                if self.failed:
                    return v
                self.following.append(self.FOLLOW_date_in_datetime386)
                date11 = self.date()
                self.following.pop()
                if self.failed:
                    return v

                self.match(self.input, UP, None)
                if self.failed:
                    return v
                if self.backtracking == 0:
                    v = date11

                self.match(self.input, TIME, self.FOLLOW_TIME_in_datetime392)
                if self.failed:
                    return v

                if self.input.LA(1) == DOWN:
                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return v
                    # FMFpythonTree.g:56:53: ( time )?
                    alt8 = 2
                    LA8_0 = self.input.LA(1)

                    if (LA8_0 == INT) :
                        alt8 = 1
                    if alt8 == 1:
                        # FMFpythonTree.g:56:54: time
                        self.following.append(self.FOLLOW_time_in_datetime395)
                        time12 = self.time()
                        self.following.pop()
                        if self.failed:
                            return v
                        if self.backtracking == 0:
                            v = datetime.datetime.combine(v.date(), time12)





                    self.match(self.input, UP, None)
                    if self.failed:
                        return v


                self.match(self.input, UP, None)
                if self.failed:
                    return v




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end datetime


    # $ANTLR start date
    # FMFpythonTree.g:59:1: date returns [v] : ( GERMANDATE | ISODATE );
    def date(self, ):

        v = None

        GERMANDATE13 = None
        ISODATE14 = None

        try:
            try:
                # FMFpythonTree.g:60:5: ( GERMANDATE | ISODATE )
                alt9 = 2
                LA9_0 = self.input.LA(1)

                if (LA9_0 == GERMANDATE) :
                    alt9 = 1
                elif (LA9_0 == ISODATE) :
                    alt9 = 2
                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return v

                    nvae = NoViableAltException("59:1: date returns [v] : ( GERMANDATE | ISODATE );", 9, 0, self.input)

                    raise nvae

                if alt9 == 1:
                    # FMFpythonTree.g:60:7: GERMANDATE
                    GERMANDATE13 = self.input.LT(1)
                    self.match(self.input, GERMANDATE, self.FOLLOW_GERMANDATE_in_date422)
                    if self.failed:
                        return v
                    if self.backtracking == 0:

                        try:
                            v = datetime.datetime.strptime(GERMANDATE13.getText(), "%d.%m.%Y")
                        except:
                            v = datetime.datetime.strptime(GERMANDATE13.getText(), "%d.%m.%y")




                elif alt9 == 2:
                    # FMFpythonTree.g:66:7: ISODATE
                    ISODATE14 = self.input.LT(1)
                    self.match(self.input, ISODATE, self.FOLLOW_ISODATE_in_date432)
                    if self.failed:
                        return v
                    if self.backtracking == 0:
                        v = datetime.datetime.strptime(ISODATE14.getText(), "%Y-%m-%d")




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end date


    # $ANTLR start time
    # FMFpythonTree.g:69:1: time returns [v] : h= INT COLON m= INT ( COLON s= FLOAT )? ;
    def time(self, ):

        v = None

        h = None
        m = None
        s = None

        try:
            try:
                # FMFpythonTree.g:70:5: (h= INT COLON m= INT ( COLON s= FLOAT )? )
                # FMFpythonTree.g:70:7: h= INT COLON m= INT ( COLON s= FLOAT )?
                h = self.input.LT(1)
                self.match(self.input, INT, self.FOLLOW_INT_in_time457)
                if self.failed:
                    return v
                self.match(self.input, COLON, self.FOLLOW_COLON_in_time459)
                if self.failed:
                    return v
                m = self.input.LT(1)
                self.match(self.input, INT, self.FOLLOW_INT_in_time463)
                if self.failed:
                    return v
                # FMFpythonTree.g:70:25: ( COLON s= FLOAT )?
                alt10 = 2
                LA10_0 = self.input.LA(1)

                if (LA10_0 == COLON) :
                    alt10 = 1
                if alt10 == 1:
                    # FMFpythonTree.g:70:26: COLON s= FLOAT
                    self.match(self.input, COLON, self.FOLLOW_COLON_in_time466)
                    if self.failed:
                        return v
                    s = self.input.LT(1)
                    self.match(self.input, FLOAT, self.FOLLOW_FLOAT_in_time470)
                    if self.failed:
                        return v



                if self.backtracking == 0:

                    s = [int("0"+p) for p in s.getText().split('.')]
                    sec = s[0]
                    if len(s)==1:
                        msec = 0
                    else:
                        msec = s[1]
                    v = datetime.time(int(h.getText()), int(m.getText()), sec, msec)






            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end time


    # $ANTLR start quantity
    # FMFpythonTree.g:81:1: quantity returns [v] : ^( QUANTITY ^( NUMBER number ) ^( UNIT ( unit )? ) ) ;
    def quantity(self, ):

        v = None

        number15 = None

        unit16 = None


        try:
            try:
                # FMFpythonTree.g:82:5: ( ^( QUANTITY ^( NUMBER number ) ^( UNIT ( unit )? ) ) )
                # FMFpythonTree.g:82:7: ^( QUANTITY ^( NUMBER number ) ^( UNIT ( unit )? ) )
                self.match(self.input, QUANTITY, self.FOLLOW_QUANTITY_in_quantity497)
                if self.failed:
                    return v

                self.match(self.input, DOWN, None)
                if self.failed:
                    return v
                self.match(self.input, NUMBER, self.FOLLOW_NUMBER_in_quantity500)
                if self.failed:
                    return v

                self.match(self.input, DOWN, None)
                if self.failed:
                    return v
                self.following.append(self.FOLLOW_number_in_quantity502)
                number15 = self.number()
                self.following.pop()
                if self.failed:
                    return v

                self.match(self.input, UP, None)
                if self.failed:
                    return v
                if self.backtracking == 0:
                    v = number15

                self.match(self.input, UNIT, self.FOLLOW_UNIT_in_quantity508)
                if self.failed:
                    return v

                if self.input.LA(1) == DOWN:
                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return v
                    # FMFpythonTree.g:82:59: ( unit )?
                    alt11 = 2
                    LA11_0 = self.input.LA(1)

                    if (LA11_0 == WORD) :
                        alt11 = 1
                    if alt11 == 1:
                        # FMFpythonTree.g:82:60: unit
                        self.following.append(self.FOLLOW_unit_in_quantity511)
                        unit16 = self.unit()
                        self.following.pop()
                        if self.failed:
                            return v
                        if self.backtracking == 0:
                            v = PQ.PhysicalQuantity(v, unit16.encode("utf-8"))





                    self.match(self.input, UP, None)
                    if self.failed:
                        return v


                self.match(self.input, UP, None)
                if self.failed:
                    return v




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end quantity


    # $ANTLR start number
    # FMFpythonTree.g:85:1: number returns [v] : ( PLUS | MINUS )? absnumber ;
    def number(self, ):

        v = None

        absnumber17 = None


        try:
            try:
                # FMFpythonTree.g:86:5: ( ( PLUS | MINUS )? absnumber )
                # FMFpythonTree.g:86:7: ( PLUS | MINUS )? absnumber
                # FMFpythonTree.g:86:7: ( PLUS | MINUS )?
                alt12 = 2
                LA12_0 = self.input.LA(1)

                if (LA12_0 == PLUS or LA12_0 == MINUS) :
                    alt12 = 1
                if alt12 == 1:
                    # FMFpythonTree.g:
                    if self.input.LA(1) == PLUS or self.input.LA(1) == MINUS:
                        self.input.consume();
                        self.errorRecovery = False
                        self.failed = False

                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return v

                        mse = MismatchedSetException(None, self.input)
                        self.recoverFromMismatchedSet(
                            self.input, mse, self.FOLLOW_set_in_number539
                            )
                        raise mse





                self.following.append(self.FOLLOW_absnumber_in_number546)
                absnumber17 = self.absnumber()
                self.following.pop()
                if self.failed:
                    return v
                if self.backtracking == 0:
                    v = absnumber17.v





            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end number

    class absnumber_return(object):
        def __init__(self):
            self.start = None
            self.stop = None
            self.tree = None

            self.v = None


    # $ANTLR start absnumber
    # FMFpythonTree.g:89:1: fragment absnumber returns [v] options {backtrack=true; } : ( FLOAT ( PLUS | MINUS ) IMAG | INT ( PLUS | MINUS ) IMAG | FLOAT | INT | IMAG );
    def absnumber(self, ):

        retval = self.absnumber_return()
        retval.start = self.input.LT(1)

        try:
            try:
                # FMFpythonTree.g:94:9: ( FLOAT ( PLUS | MINUS ) IMAG | INT ( PLUS | MINUS ) IMAG | FLOAT | INT | IMAG )
                alt13 = 5
                LA13 = self.input.LA(1)
                if LA13 == FLOAT:
                    LA13_1 = self.input.LA(2)

                    if (LA13_1 == PLUS or LA13_1 == MINUS) :
                        alt13 = 1
                    elif (LA13_1 == 3) :
                        alt13 = 3
                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        nvae = NoViableAltException("89:1: fragment absnumber returns [v] options {backtrack=true; } : ( FLOAT ( PLUS | MINUS ) IMAG | INT ( PLUS | MINUS ) IMAG | FLOAT | INT | IMAG );", 13, 1, self.input)

                        raise nvae

                elif LA13 == INT:
                    LA13_2 = self.input.LA(2)

                    if (LA13_2 == PLUS or LA13_2 == MINUS) :
                        alt13 = 2
                    elif (LA13_2 == 3) :
                        alt13 = 4
                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        nvae = NoViableAltException("89:1: fragment absnumber returns [v] options {backtrack=true; } : ( FLOAT ( PLUS | MINUS ) IMAG | INT ( PLUS | MINUS ) IMAG | FLOAT | INT | IMAG );", 13, 2, self.input)

                        raise nvae

                elif LA13 == IMAG:
                    alt13 = 5
                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return retval

                    nvae = NoViableAltException("89:1: fragment absnumber returns [v] options {backtrack=true; } : ( FLOAT ( PLUS | MINUS ) IMAG | INT ( PLUS | MINUS ) IMAG | FLOAT | INT | IMAG );", 13, 0, self.input)

                    raise nvae

                if alt13 == 1:
                    # FMFpythonTree.g:94:11: FLOAT ( PLUS | MINUS ) IMAG
                    self.match(self.input, FLOAT, self.FOLLOW_FLOAT_in_absnumber592)
                    if self.failed:
                        return retval
                    if self.input.LA(1) == PLUS or self.input.LA(1) == MINUS:
                        self.input.consume();
                        self.errorRecovery = False
                        self.failed = False

                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        mse = MismatchedSetException(None, self.input)
                        self.recoverFromMismatchedSet(
                            self.input, mse, self.FOLLOW_set_in_absnumber594
                            )
                        raise mse


                    self.match(self.input, IMAG, self.FOLLOW_IMAG_in_absnumber600)
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        retval.v = complex(self.input.toString(retval.start, self.input.LT(-1)))



                elif alt13 == 2:
                    # FMFpythonTree.g:95:11: INT ( PLUS | MINUS ) IMAG
                    self.match(self.input, INT, self.FOLLOW_INT_in_absnumber614)
                    if self.failed:
                        return retval
                    if self.input.LA(1) == PLUS or self.input.LA(1) == MINUS:
                        self.input.consume();
                        self.errorRecovery = False
                        self.failed = False

                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        mse = MismatchedSetException(None, self.input)
                        self.recoverFromMismatchedSet(
                            self.input, mse, self.FOLLOW_set_in_absnumber616
                            )
                        raise mse


                    self.match(self.input, IMAG, self.FOLLOW_IMAG_in_absnumber622)
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        retval.v = complex(self.input.toString(retval.start, self.input.LT(-1)))



                elif alt13 == 3:
                    # FMFpythonTree.g:96:11: FLOAT
                    self.match(self.input, FLOAT, self.FOLLOW_FLOAT_in_absnumber636)
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        retval.v = float(self.input.toString(retval.start, self.input.LT(-1)))



                elif alt13 == 4:
                    # FMFpythonTree.g:97:11: INT
                    self.match(self.input, INT, self.FOLLOW_INT_in_absnumber650)
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        retval.v = int(self.input.toString(retval.start, self.input.LT(-1)))



                elif alt13 == 5:
                    # FMFpythonTree.g:98:11: IMAG
                    self.match(self.input, IMAG, self.FOLLOW_IMAG_in_absnumber664)
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        retval.v = complex(self.input.toString(retval.start, self.input.LT(-1)))




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end absnumber


    # $ANTLR start datadefSection
    # FMFpythonTree.g:101:1: datadefSection returns [coldefs] : ^( DATADEF_SECTION ^( HEADER ASTERISK 'data definitions' ) ^( BODY ( colitem )+ ) ) ;
    def datadefSection(self, ):

        coldefs = None

        colitem18 = None



        coldefs = []

        try:
            try:
                # FMFpythonTree.g:105:5: ( ^( DATADEF_SECTION ^( HEADER ASTERISK 'data definitions' ) ^( BODY ( colitem )+ ) ) )
                # FMFpythonTree.g:105:7: ^( DATADEF_SECTION ^( HEADER ASTERISK 'data definitions' ) ^( BODY ( colitem )+ ) )
                self.match(self.input, DATADEF_SECTION, self.FOLLOW_DATADEF_SECTION_in_datadefSection698)
                if self.failed:
                    return coldefs

                self.match(self.input, DOWN, None)
                if self.failed:
                    return coldefs
                self.match(self.input, HEADER, self.FOLLOW_HEADER_in_datadefSection701)
                if self.failed:
                    return coldefs

                self.match(self.input, DOWN, None)
                if self.failed:
                    return coldefs
                self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_datadefSection703)
                if self.failed:
                    return coldefs
                self.match(self.input, 65, self.FOLLOW_65_in_datadefSection705)
                if self.failed:
                    return coldefs

                self.match(self.input, UP, None)
                if self.failed:
                    return coldefs
                self.match(self.input, BODY, self.FOLLOW_BODY_in_datadefSection709)
                if self.failed:
                    return coldefs

                self.match(self.input, DOWN, None)
                if self.failed:
                    return coldefs
                # FMFpythonTree.g:105:70: ( colitem )+
                cnt14 = 0
                while True: #loop14
                    alt14 = 2
                    LA14_0 = self.input.LA(1)

                    if (LA14_0 == COLSPEC) :
                        alt14 = 1


                    if alt14 == 1:
                        # FMFpythonTree.g:105:71: colitem
                        self.following.append(self.FOLLOW_colitem_in_datadefSection712)
                        colitem18 = self.colitem()
                        self.following.pop()
                        if self.failed:
                            return coldefs
                        if self.backtracking == 0:
                            coldefs.append(colitem18)



                    else:
                        if cnt14 >= 1:
                            break #loop14

                        if self.backtracking > 0:
                            self.failed = True
                            return coldefs

                        eee = EarlyExitException(14, self.input)
                        raise eee

                    cnt14 += 1



                self.match(self.input, UP, None)
                if self.failed:
                    return coldefs

                self.match(self.input, UP, None)
                if self.failed:
                    return coldefs




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return coldefs

    # $ANTLR end datadefSection


    # $ANTLR start colitem
    # FMFpythonTree.g:108:1: colitem returns [coldef] : ^( COLSPEC ^( LONGNAME key= . (key= . )* ) colspec ) ;
    def colitem(self, ):

        coldef = None

        key = None
        colspec19 = None


        try:
            try:
                # FMFpythonTree.g:109:5: ( ^( COLSPEC ^( LONGNAME key= . (key= . )* ) colspec ) )
                # FMFpythonTree.g:109:7: ^( COLSPEC ^( LONGNAME key= . (key= . )* ) colspec )
                self.match(self.input, COLSPEC, self.FOLLOW_COLSPEC_in_colitem740)
                if self.failed:
                    return coldef

                self.match(self.input, DOWN, None)
                if self.failed:
                    return coldef
                self.match(self.input, LONGNAME, self.FOLLOW_LONGNAME_in_colitem743)
                if self.failed:
                    return coldef

                self.match(self.input, DOWN, None)
                if self.failed:
                    return coldef
                key = self.input.LT(1)
                self.matchAny(self.input)
                if self.failed:
                    return coldef
                if self.backtracking == 0:
                    longname=key.getText()

                # FMFpythonTree.g:109:59: (key= . )*
                while True: #loop15
                    alt15 = 2
                    LA15_0 = self.input.LA(1)

                    if ((CONFIG <= LA15_0 <= 67)) :
                        alt15 = 1


                    if alt15 == 1:
                        # FMFpythonTree.g:109:60: key= .
                        key = self.input.LT(1)
                        self.matchAny(self.input)
                        if self.failed:
                            return coldef
                        if self.backtracking == 0:
                            longname+=u" "+key.getText()



                    else:
                        break #loop15



                self.match(self.input, UP, None)
                if self.failed:
                    return coldef
                self.following.append(self.FOLLOW_colspec_in_colitem761)
                colspec19 = self.colspec()
                self.following.pop()
                if self.failed:
                    return coldef

                self.match(self.input, UP, None)
                if self.failed:
                    return coldef
                if self.backtracking == 0:
                    coldef = [longname] + colspec19





            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return coldef

    # $ANTLR end colitem


    # $ANTLR start colspec
    # FMFpythonTree.g:112:1: colspec returns [v] : ^( IDENTIFIER identifier ) ^( DEPS ( deps )? ) ^( UNIT ( unit )? ) ;
    def colspec(self, ):

        v = None

        deps20 = None

        unit21 = None

        identifier22 = None


        try:
            try:
                # FMFpythonTree.g:113:5: ( ^( IDENTIFIER identifier ) ^( DEPS ( deps )? ) ^( UNIT ( unit )? ) )
                # FMFpythonTree.g:113:7: ^( IDENTIFIER identifier ) ^( DEPS ( deps )? ) ^( UNIT ( unit )? )
                self.match(self.input, IDENTIFIER, self.FOLLOW_IDENTIFIER_in_colspec786)
                if self.failed:
                    return v

                self.match(self.input, DOWN, None)
                if self.failed:
                    return v
                self.following.append(self.FOLLOW_identifier_in_colspec788)
                identifier22 = self.identifier()
                self.following.pop()
                if self.failed:
                    return v

                self.match(self.input, UP, None)
                if self.failed:
                    return v
                self.match(self.input, DEPS, self.FOLLOW_DEPS_in_colspec792)
                if self.failed:
                    return v

                if self.input.LA(1) == DOWN:
                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return v
                    # FMFpythonTree.g:113:39: ( deps )?
                    alt16 = 2
                    LA16_0 = self.input.LA(1)

                    if (LA16_0 == WORD) :
                        alt16 = 1
                    if alt16 == 1:
                        # FMFpythonTree.g:113:39: deps
                        self.following.append(self.FOLLOW_deps_in_colspec794)
                        deps20 = self.deps()
                        self.following.pop()
                        if self.failed:
                            return v




                    self.match(self.input, UP, None)
                    if self.failed:
                        return v

                self.match(self.input, UNIT, self.FOLLOW_UNIT_in_colspec799)
                if self.failed:
                    return v

                if self.input.LA(1) == DOWN:
                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return v
                    # FMFpythonTree.g:113:53: ( unit )?
                    alt17 = 2
                    LA17_0 = self.input.LA(1)

                    if (LA17_0 == WORD) :
                        alt17 = 1
                    if alt17 == 1:
                        # FMFpythonTree.g:113:53: unit
                        self.following.append(self.FOLLOW_unit_in_colspec801)
                        unit21 = self.unit()
                        self.following.pop()
                        if self.failed:
                            return v




                    self.match(self.input, UP, None)
                    if self.failed:
                        return v

                if self.backtracking == 0:

                    rdeps = []
                    try:
                        if deps20:
                            rdeps = deps20
                    except AttributeError:
                        pass
                    runit=1.0
                    try:
                    	if unit21 != None:
                            runit=unit21
                    except AttributeError:
                        pass
                    v = [self.input.getTokenStream().toString(
                        self.input.getTreeAdaptor().getTokenStartIndex(identifier22.start),
                        self.input.getTreeAdaptor().getTokenStopIndex(identifier22.start)
                        ), rdeps, runit]






            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end colspec


    # $ANTLR start unit
    # FMFpythonTree.g:130:1: unit returns [v] : un+= WORD (un+= ( ASTERISK | DIV ) un+= WORD )* ;
    def unit(self, ):

        v = None

        un = None
        list_un = None

        try:
            try:
                # FMFpythonTree.g:131:5: (un+= WORD (un+= ( ASTERISK | DIV ) un+= WORD )* )
                # FMFpythonTree.g:131:7: un+= WORD (un+= ( ASTERISK | DIV ) un+= WORD )*
                un = self.input.LT(1)
                self.match(self.input, WORD, self.FOLLOW_WORD_in_unit828)
                if self.failed:
                    return v
                if list_un is None:
                    list_un = []
                list_un.append(un)

                # FMFpythonTree.g:131:16: (un+= ( ASTERISK | DIV ) un+= WORD )*
                while True: #loop18
                    alt18 = 2
                    LA18_0 = self.input.LA(1)

                    if (LA18_0 == ASTERISK or LA18_0 == DIV) :
                        alt18 = 1


                    if alt18 == 1:
                        # FMFpythonTree.g:131:17: un+= ( ASTERISK | DIV ) un+= WORD
                        un = self.input.LT(1)
                        if self.input.LA(1) == ASTERISK or self.input.LA(1) == DIV:
                            self.input.consume();
                            self.errorRecovery = False
                            self.failed = False

                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return v

                            mse = MismatchedSetException(None, self.input)
                            self.recoverFromMismatchedSet(
                                self.input, mse, self.FOLLOW_set_in_unit833
                                )
                            raise mse


                        if list_un is None:
                            list_un = []
                        list_un.append(un)

                        un = self.input.LT(1)
                        self.match(self.input, WORD, self.FOLLOW_WORD_in_unit841)
                        if self.failed:
                            return v
                        if list_un is None:
                            list_un = []
                        list_un.append(un)



                    else:
                        break #loop18


                if self.backtracking == 0:
                    v = "".join([u.getText() for u in list_un])





            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end unit

    class identifier_return(object):
        def __init__(self):
            self.start = None
            self.stop = None
            self.tree = None



    # $ANTLR start identifier
    # FMFpythonTree.g:135:1: identifier : WORD ;
    def identifier(self, ):

        retval = self.identifier_return()
        retval.start = self.input.LT(1)

        try:
            try:
                # FMFpythonTree.g:135:11: ( WORD )
                # FMFpythonTree.g:135:13: WORD
                self.match(self.input, WORD, self.FOLLOW_WORD_in_identifier858)
                if self.failed:
                    return retval




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end identifier


    # $ANTLR start deps
    # FMFpythonTree.g:144:1: deps returns [v] : ( identifier )+ ;
    def deps(self, ):

        v = None

        identifier23 = None



        v = []

        try:
            try:
                # FMFpythonTree.g:148:5: ( ( identifier )+ )
                # FMFpythonTree.g:148:7: ( identifier )+
                # FMFpythonTree.g:148:7: ( identifier )+
                cnt19 = 0
                while True: #loop19
                    alt19 = 2
                    LA19_0 = self.input.LA(1)

                    if (LA19_0 == WORD) :
                        alt19 = 1


                    if alt19 == 1:
                        # FMFpythonTree.g:148:8: identifier
                        self.following.append(self.FOLLOW_identifier_in_deps882)
                        identifier23 = self.identifier()
                        self.following.pop()
                        if self.failed:
                            return v
                        if self.backtracking == 0:

                            text = self.input.getTokenStream().toString(
                                self.input.getTreeAdaptor().getTokenStartIndex(identifier23.start),
                                self.input.getTreeAdaptor().getTokenStopIndex(identifier23.start)
                                )
                            if text[0]=='(' and text[-1]==')':
                                text=text[1:-1]
                            v.append(text)




                    else:
                        if cnt19 >= 1:
                            break #loop19

                        if self.backtracking > 0:
                            self.failed = True
                            return v

                        eee = EarlyExitException(19, self.input)
                        raise eee

                    cnt19 += 1






            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end deps


    # $ANTLR start dataSection
    # FMFpythonTree.g:157:1: dataSection[coldefs] returns [fieldContainers] : ^( DATA_SECTION ^( HEADER ASTERISK 'data' ) ^( BODY ( dataitem[fields] )* ) ) ;
    def dataSection(self, coldefs):

        fieldContainers = None


        fields = []
        fieldContainers = []
        for i in xrange(0, len(coldefs)):
            fields.append([])

        try:
            try:
                # FMFpythonTree.g:173:5: ( ^( DATA_SECTION ^( HEADER ASTERISK 'data' ) ^( BODY ( dataitem[fields] )* ) ) )
                # FMFpythonTree.g:173:7: ^( DATA_SECTION ^( HEADER ASTERISK 'data' ) ^( BODY ( dataitem[fields] )* ) )
                self.match(self.input, DATA_SECTION, self.FOLLOW_DATA_SECTION_in_dataSection919)
                if self.failed:
                    return fieldContainers

                self.match(self.input, DOWN, None)
                if self.failed:
                    return fieldContainers
                self.match(self.input, HEADER, self.FOLLOW_HEADER_in_dataSection922)
                if self.failed:
                    return fieldContainers

                self.match(self.input, DOWN, None)
                if self.failed:
                    return fieldContainers
                self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_dataSection924)
                if self.failed:
                    return fieldContainers
                self.match(self.input, 66, self.FOLLOW_66_in_dataSection926)
                if self.failed:
                    return fieldContainers

                self.match(self.input, UP, None)
                if self.failed:
                    return fieldContainers
                self.match(self.input, BODY, self.FOLLOW_BODY_in_dataSection930)
                if self.failed:
                    return fieldContainers

                if self.input.LA(1) == DOWN:
                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return fieldContainers
                    # FMFpythonTree.g:173:55: ( dataitem[fields] )*
                    while True: #loop20
                        alt20 = 2
                        LA20_0 = self.input.LA(1)

                        if (LA20_0 == DATASET) :
                            alt20 = 1


                        if alt20 == 1:
                            # FMFpythonTree.g:173:55: dataitem[fields]
                            self.following.append(self.FOLLOW_dataitem_in_dataSection932)
                            self.dataitem(fields)
                            self.following.pop()
                            if self.failed:
                                return fieldContainers


                        else:
                            break #loop20



                    self.match(self.input, UP, None)
                    if self.failed:
                        return fieldContainers


                self.match(self.input, UP, None)
                if self.failed:
                    return fieldContainers



                if self.backtracking == 0:

                    fieldDict = {}
                    for col, data in zip(coldefs, fields):
                        fieldDict[col[1]]=DC.FieldContainer(numpy.array(data), col[3], longname=col[0], shortname=col[1])
                    for col in coldefs:
                        if len(col[2])>0:
                            fieldDict[col[1]].dimensions = [ fieldDict[key] for key in col[2] ]
                    fieldContainers = [fieldDict[cd[1]] for cd in coldefs]



            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return fieldContainers

    # $ANTLR end dataSection


    # $ANTLR start dataitem
    # FMFpythonTree.g:176:1: dataitem[fields] : ^( DATASET ( cell )* ) ;
    def dataitem(self, fields):

        cell24 = None



        i = 0

        try:
            try:
                # FMFpythonTree.g:180:5: ( ^( DATASET ( cell )* ) )
                # FMFpythonTree.g:180:7: ^( DATASET ( cell )* )
                self.match(self.input, DATASET, self.FOLLOW_DATASET_in_dataitem961)
                if self.failed:
                    return

                if self.input.LA(1) == DOWN:
                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return
                    # FMFpythonTree.g:180:17: ( cell )*
                    while True: #loop21
                        alt21 = 2
                        LA21_0 = self.input.LA(1)

                        if (LA21_0 == NUMBER or LA21_0 == STRING) :
                            alt21 = 1


                        if alt21 == 1:
                            # FMFpythonTree.g:180:18: cell
                            self.following.append(self.FOLLOW_cell_in_dataitem964)
                            cell24 = self.cell()
                            self.following.pop()
                            if self.failed:
                                return
                            if self.backtracking == 0:

                                fields[i].append(cell24)
                                i += 1




                        else:
                            break #loop21



                    self.match(self.input, UP, None)
                    if self.failed:
                        return





            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return

    # $ANTLR end dataitem


    # $ANTLR start cell
    # FMFpythonTree.g:187:1: cell returns [v] : ( ^( NUMBER number ) | ^( STRING (string= . )+ ) );
    def cell(self, ):

        v = None

        string = None
        number25 = None



        v=u""

        try:
            try:
                # FMFpythonTree.g:191:5: ( ^( NUMBER number ) | ^( STRING (string= . )+ ) )
                alt23 = 2
                LA23_0 = self.input.LA(1)

                if (LA23_0 == NUMBER) :
                    alt23 = 1
                elif (LA23_0 == STRING) :
                    alt23 = 2
                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return v

                    nvae = NoViableAltException("187:1: cell returns [v] : ( ^( NUMBER number ) | ^( STRING (string= . )+ ) );", 23, 0, self.input)

                    raise nvae

                if alt23 == 1:
                    # FMFpythonTree.g:191:7: ^( NUMBER number )
                    self.match(self.input, NUMBER, self.FOLLOW_NUMBER_in_cell1005)
                    if self.failed:
                        return v

                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return v
                    self.following.append(self.FOLLOW_number_in_cell1007)
                    number25 = self.number()
                    self.following.pop()
                    if self.failed:
                        return v

                    self.match(self.input, UP, None)
                    if self.failed:
                        return v
                    if self.backtracking == 0:
                        v = number25



                elif alt23 == 2:
                    # FMFpythonTree.g:192:7: ^( STRING (string= . )+ )
                    self.match(self.input, STRING, self.FOLLOW_STRING_in_cell1019)
                    if self.failed:
                        return v

                    self.match(self.input, DOWN, None)
                    if self.failed:
                        return v
                    # FMFpythonTree.g:192:16: (string= . )+
                    cnt22 = 0
                    while True: #loop22
                        alt22 = 2
                        LA22_0 = self.input.LA(1)

                        if ((CONFIG <= LA22_0 <= 67)) :
                            alt22 = 1


                        if alt22 == 1:
                            # FMFpythonTree.g:192:17: string= .
                            string = self.input.LT(1)
                            self.matchAny(self.input)
                            if self.failed:
                                return v
                            if self.backtracking == 0:
                                v += string.getText()



                        else:
                            if cnt22 >= 1:
                                break #loop22

                            if self.backtracking > 0:
                                self.failed = True
                                return v

                            eee = EarlyExitException(22, self.input)
                            raise eee

                        cnt22 += 1



                    self.match(self.input, UP, None)
                    if self.failed:
                        return v



            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return v

    # $ANTLR end cell




    FOLLOW_config_in_dataContainer56 = frozenset([1])
    FOLLOW_CONFIG_in_config85 = frozenset([2])
    FOLLOW_referenceSection_in_config87 = frozenset([6, 7])
    FOLLOW_commonSection_in_config91 = frozenset([6, 7])
    FOLLOW_datadefSection_in_config96 = frozenset([8])
    FOLLOW_dataSection_in_config98 = frozenset([3])
    FOLLOW_COMMON_SECTION_in_referenceSection129 = frozenset([2])
    FOLLOW_HEADER_in_referenceSection132 = frozenset([2])
    FOLLOW_ASTERISK_in_referenceSection134 = frozenset([64])
    FOLLOW_64_in_referenceSection136 = frozenset([3])
    FOLLOW_BODY_in_referenceSection150 = frozenset([2])
    FOLLOW_commonitem_in_referenceSection153 = frozenset([3, 10])
    FOLLOW_COMMON_SECTION_in_commonSection178 = frozenset([2])
    FOLLOW_HEADER_in_commonSection181 = frozenset([2])
    FOLLOW_headername_in_commonSection183 = frozenset([3])
    FOLLOW_BODY_in_commonSection197 = frozenset([2])
    FOLLOW_commonitem_in_commonSection200 = frozenset([3, 10])
    FOLLOW_ITEM_in_commonitem233 = frozenset([2])
    FOLLOW_KEY_in_commonitem236 = frozenset([2])
    FOLLOW_value_in_commonitem248 = frozenset([3])
    FOLLOW_NUMBER_in_value277 = frozenset([2])
    FOLLOW_number_in_value279 = frozenset([3])
    FOLLOW_VARIABLE_in_value291 = frozenset([2])
    FOLLOW_IDENTIFIER_in_value294 = frozenset([2])
    FOLLOW_identifier_in_value296 = frozenset([3])
    FOLLOW_quantity_in_value299 = frozenset([3])
    FOLLOW_datetime_in_value310 = frozenset([1])
    FOLLOW_STRING_in_value321 = frozenset([2])
    FOLLOW_catchall_in_value323 = frozenset([3])
    FOLLOW_set_in_catchall354 = frozenset([1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_DATETIME_in_datetime381 = frozenset([2])
    FOLLOW_DATE_in_datetime384 = frozenset([2])
    FOLLOW_date_in_datetime386 = frozenset([3])
    FOLLOW_TIME_in_datetime392 = frozenset([2])
    FOLLOW_time_in_datetime395 = frozenset([3])
    FOLLOW_GERMANDATE_in_date422 = frozenset([1])
    FOLLOW_ISODATE_in_date432 = frozenset([1])
    FOLLOW_INT_in_time457 = frozenset([33])
    FOLLOW_COLON_in_time459 = frozenset([58])
    FOLLOW_INT_in_time463 = frozenset([1, 33])
    FOLLOW_COLON_in_time466 = frozenset([57])
    FOLLOW_FLOAT_in_time470 = frozenset([1])
    FOLLOW_QUANTITY_in_quantity497 = frozenset([2])
    FOLLOW_NUMBER_in_quantity500 = frozenset([2])
    FOLLOW_number_in_quantity502 = frozenset([3])
    FOLLOW_UNIT_in_quantity508 = frozenset([2])
    FOLLOW_unit_in_quantity511 = frozenset([3])
    FOLLOW_set_in_number539 = frozenset([57, 58, 59])
    FOLLOW_absnumber_in_number546 = frozenset([1])
    FOLLOW_FLOAT_in_absnumber592 = frozenset([35, 38])
    FOLLOW_set_in_absnumber594 = frozenset([59])
    FOLLOW_IMAG_in_absnumber600 = frozenset([1])
    FOLLOW_INT_in_absnumber614 = frozenset([35, 38])
    FOLLOW_set_in_absnumber616 = frozenset([59])
    FOLLOW_IMAG_in_absnumber622 = frozenset([1])
    FOLLOW_FLOAT_in_absnumber636 = frozenset([1])
    FOLLOW_INT_in_absnumber650 = frozenset([1])
    FOLLOW_IMAG_in_absnumber664 = frozenset([1])
    FOLLOW_DATADEF_SECTION_in_datadefSection698 = frozenset([2])
    FOLLOW_HEADER_in_datadefSection701 = frozenset([2])
    FOLLOW_ASTERISK_in_datadefSection703 = frozenset([65])
    FOLLOW_65_in_datadefSection705 = frozenset([3])
    FOLLOW_BODY_in_datadefSection709 = frozenset([2])
    FOLLOW_colitem_in_datadefSection712 = frozenset([3, 22])
    FOLLOW_COLSPEC_in_colitem740 = frozenset([2])
    FOLLOW_LONGNAME_in_colitem743 = frozenset([2])
    FOLLOW_colspec_in_colitem761 = frozenset([3])
    FOLLOW_IDENTIFIER_in_colspec786 = frozenset([2])
    FOLLOW_identifier_in_colspec788 = frozenset([3])
    FOLLOW_DEPS_in_colspec792 = frozenset([2])
    FOLLOW_deps_in_colspec794 = frozenset([3])
    FOLLOW_UNIT_in_colspec799 = frozenset([2])
    FOLLOW_unit_in_colspec801 = frozenset([3])
    FOLLOW_WORD_in_unit828 = frozenset([1, 32, 44])
    FOLLOW_set_in_unit833 = frozenset([61])
    FOLLOW_WORD_in_unit841 = frozenset([1, 32, 44])
    FOLLOW_WORD_in_identifier858 = frozenset([1])
    FOLLOW_identifier_in_deps882 = frozenset([1, 61])
    FOLLOW_DATA_SECTION_in_dataSection919 = frozenset([2])
    FOLLOW_HEADER_in_dataSection922 = frozenset([2])
    FOLLOW_ASTERISK_in_dataSection924 = frozenset([66])
    FOLLOW_66_in_dataSection926 = frozenset([3])
    FOLLOW_BODY_in_dataSection930 = frozenset([2])
    FOLLOW_dataitem_in_dataSection932 = frozenset([3, 11])
    FOLLOW_DATASET_in_dataitem961 = frozenset([2])
    FOLLOW_cell_in_dataitem964 = frozenset([3, 16, 21])
    FOLLOW_NUMBER_in_cell1005 = frozenset([2])
    FOLLOW_number_in_cell1007 = frozenset([3])
    FOLLOW_STRING_in_cell1019 = frozenset([2])

