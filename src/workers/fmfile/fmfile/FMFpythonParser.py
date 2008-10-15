# $ANTLR 3.0.1 FMFpython.g 2008-10-15 18:08:06

from antlr3 import *
from antlr3.compat import set, frozenset

from antlr3.tree import *



# for convenience in actions
HIDDEN = BaseRecognizer.HIDDEN

# token types
LESSTHAN=47
MINUS=38
DATASET=11
IINT=53
NUMBER=16
FLOAT=57
GERMANDATE=55
COLSPEC=22
PUNCTUATION=62
LETTERS=50
NEWLINE=25
GREATERTHAN=48
RCURLY=41
LCURLY=40
LITERAL=63
DATADEF_SECTION=7
INT=58
DATETIME=13
DATE=14
DATA_SECTION=8
RPAREN=31
COMMON_SECTION=6
LPAREN=30
QUANTITY=19
PLUS=35
DIGIT=37
BODY=9
RWORD=60
DEPS=24
DIGITS=49
NMINUS=39
WS=26
NPLUS=36
STRING=21
CONFIG=4
DOLLAR=45
COMMENT=27
ISODATE=56
ESC=54
ITEM=10
UNIT=20
LBRACK=28
LONGNAME=23
IMAG=59
EQUALS=34
TIME=15
WORD=61
HAT=43
EXPONENT=51
VARIABLE=17
KEY=12
EOF=-1
FFLOAT=52
ASTERISK=32
RBRACK=29
COLON=33
DIV=44
IDENTIFIER=18
PERCENTAGE=46
HEADER=5
UNDERSCORE=42

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



class FMFpythonParser(Parser):
    grammarFileName = "FMFpython.g"
    tokenNames = tokenNames

    def __init__(self, input):
        Parser.__init__(self, input)
        self.ruleMemo = {}



                
        self.adaptor = CommonTreeAdaptor()




    class config_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start config
    # FMFpython.g:122:1: config : referenceSection ( commonSection )* datadefSection dataSection -> ^( CONFIG referenceSection ( commonSection )* datadefSection dataSection ) ;
    def config(self, ):

        retval = self.config_return()
        retval.start = self.input.LT(1)

        root_0 = None

        referenceSection1 = None

        commonSection2 = None

        datadefSection3 = None

        dataSection4 = None


        stream_datadefSection = RewriteRuleSubtreeStream(self.adaptor, "rule datadefSection")
        stream_commonSection = RewriteRuleSubtreeStream(self.adaptor, "rule commonSection")
        stream_referenceSection = RewriteRuleSubtreeStream(self.adaptor, "rule referenceSection")
        stream_dataSection = RewriteRuleSubtreeStream(self.adaptor, "rule dataSection")
        try:
            try:
                # FMFpython.g:123:9: ( referenceSection ( commonSection )* datadefSection dataSection -> ^( CONFIG referenceSection ( commonSection )* datadefSection dataSection ) )
                # FMFpython.g:123:11: referenceSection ( commonSection )* datadefSection dataSection
                self.following.append(self.FOLLOW_referenceSection_in_config1261)
                referenceSection1 = self.referenceSection()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_referenceSection.add(referenceSection1.tree)
                # FMFpython.g:123:28: ( commonSection )*
                while True: #loop1
                    alt1 = 2
                    LA1_0 = self.input.LA(1)

                    if (LA1_0 == LBRACK) :
                        LA1_1 = self.input.LA(2)

                        if ((CONFIG <= LA1_1 <= RPAREN) or (COLON <= LA1_1 <= 67)) :
                            alt1 = 1




                    if alt1 == 1:
                        # FMFpython.g:123:28: commonSection
                        self.following.append(self.FOLLOW_commonSection_in_config1263)
                        commonSection2 = self.commonSection()
                        self.following.pop()
                        if self.failed:
                            return retval
                        if self.backtracking == 0:
                            stream_commonSection.add(commonSection2.tree)


                    else:
                        break #loop1


                self.following.append(self.FOLLOW_datadefSection_in_config1266)
                datadefSection3 = self.datadefSection()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_datadefSection.add(datadefSection3.tree)
                self.following.append(self.FOLLOW_dataSection_in_config1268)
                dataSection4 = self.dataSection()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_dataSection.add(dataSection4.tree)
                # AST Rewrite
                # elements: datadefSection, commonSection, dataSection, referenceSection
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 124:9: -> ^( CONFIG referenceSection ( commonSection )* datadefSection dataSection )
                    # FMFpython.g:124:12: ^( CONFIG referenceSection ( commonSection )* datadefSection dataSection )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(CONFIG, "CONFIG"), root_1)

                    self.adaptor.addChild(root_1, stream_referenceSection.next())
                    # FMFpython.g:124:38: ( commonSection )*
                    while stream_commonSection.hasNext():
                        self.adaptor.addChild(root_1, stream_commonSection.next())


                    stream_commonSection.reset();
                    self.adaptor.addChild(root_1, stream_datadefSection.next())
                    self.adaptor.addChild(root_1, stream_dataSection.next())

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end config

    class referenceSection_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start referenceSection
    # FMFpython.g:127:1: referenceSection : LBRACK ASTERISK 'reference' RBRACK NEWLINE ( commonitem )+ -> ^( COMMON_SECTION ^( HEADER ASTERISK 'reference' ) ^( BODY ( commonitem )+ ) ) ;
    def referenceSection(self, ):

        retval = self.referenceSection_return()
        retval.start = self.input.LT(1)

        root_0 = None

        LBRACK5 = None
        ASTERISK6 = None
        string_literal7 = None
        RBRACK8 = None
        NEWLINE9 = None
        commonitem10 = None


        LBRACK5_tree = None
        ASTERISK6_tree = None
        string_literal7_tree = None
        RBRACK8_tree = None
        NEWLINE9_tree = None
        stream_ASTERISK = RewriteRuleTokenStream(self.adaptor, "token ASTERISK")
        stream_RBRACK = RewriteRuleTokenStream(self.adaptor, "token RBRACK")
        stream_64 = RewriteRuleTokenStream(self.adaptor, "token 64")
        stream_LBRACK = RewriteRuleTokenStream(self.adaptor, "token LBRACK")
        stream_NEWLINE = RewriteRuleTokenStream(self.adaptor, "token NEWLINE")
        stream_commonitem = RewriteRuleSubtreeStream(self.adaptor, "rule commonitem")
        try:
            try:
                # FMFpython.g:128:9: ( LBRACK ASTERISK 'reference' RBRACK NEWLINE ( commonitem )+ -> ^( COMMON_SECTION ^( HEADER ASTERISK 'reference' ) ^( BODY ( commonitem )+ ) ) )
                # FMFpython.g:128:11: LBRACK ASTERISK 'reference' RBRACK NEWLINE ( commonitem )+
                LBRACK5 = self.input.LT(1)
                self.match(self.input, LBRACK, self.FOLLOW_LBRACK_in_referenceSection1316)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_LBRACK.add(LBRACK5)
                ASTERISK6 = self.input.LT(1)
                self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_referenceSection1318)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_ASTERISK.add(ASTERISK6)
                string_literal7 = self.input.LT(1)
                self.match(self.input, 64, self.FOLLOW_64_in_referenceSection1320)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_64.add(string_literal7)
                RBRACK8 = self.input.LT(1)
                self.match(self.input, RBRACK, self.FOLLOW_RBRACK_in_referenceSection1322)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_RBRACK.add(RBRACK8)
                NEWLINE9 = self.input.LT(1)
                self.match(self.input, NEWLINE, self.FOLLOW_NEWLINE_in_referenceSection1324)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_NEWLINE.add(NEWLINE9)
                # FMFpython.g:128:54: ( commonitem )+
                cnt2 = 0
                while True: #loop2
                    alt2 = 2
                    LA2_0 = self.input.LA(1)

                    if ((CONFIG <= LA2_0 <= COMMENT) or (RBRACK <= LA2_0 <= 67)) :
                        alt2 = 1


                    if alt2 == 1:
                        # FMFpython.g:128:54: commonitem
                        self.following.append(self.FOLLOW_commonitem_in_referenceSection1326)
                        commonitem10 = self.commonitem()
                        self.following.pop()
                        if self.failed:
                            return retval
                        if self.backtracking == 0:
                            stream_commonitem.add(commonitem10.tree)


                    else:
                        if cnt2 >= 1:
                            break #loop2

                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        eee = EarlyExitException(2, self.input)
                        raise eee

                    cnt2 += 1


                # AST Rewrite
                # elements: commonitem, ASTERISK, 64
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 129:9: -> ^( COMMON_SECTION ^( HEADER ASTERISK 'reference' ) ^( BODY ( commonitem )+ ) )
                    # FMFpython.g:129:12: ^( COMMON_SECTION ^( HEADER ASTERISK 'reference' ) ^( BODY ( commonitem )+ ) )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(COMMON_SECTION, "COMMON_SECTION"), root_1)

                    # FMFpython.g:129:29: ^( HEADER ASTERISK 'reference' )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(HEADER, "HEADER"), root_2)

                    self.adaptor.addChild(root_2, stream_ASTERISK.next())
                    self.adaptor.addChild(root_2, stream_64.next())

                    self.adaptor.addChild(root_1, root_2)
                    # FMFpython.g:129:60: ^( BODY ( commonitem )+ )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(BODY, "BODY"), root_2)

                    # FMFpython.g:129:67: ( commonitem )+
                    if not (stream_commonitem.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_commonitem.hasNext():
                        self.adaptor.addChild(root_2, stream_commonitem.next())


                    stream_commonitem.reset()

                    self.adaptor.addChild(root_1, root_2)

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end referenceSection

    class datadefSection_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start datadefSection
    # FMFpython.g:131:1: datadefSection : LBRACK ASTERISK 'data definitions' RBRACK NEWLINE ( colitem )+ -> ^( DATADEF_SECTION ^( HEADER ASTERISK 'data definitions' ) ^( BODY ( colitem )+ ) ) ;
    def datadefSection(self, ):

        retval = self.datadefSection_return()
        retval.start = self.input.LT(1)

        root_0 = None

        LBRACK11 = None
        ASTERISK12 = None
        string_literal13 = None
        RBRACK14 = None
        NEWLINE15 = None
        colitem16 = None


        LBRACK11_tree = None
        ASTERISK12_tree = None
        string_literal13_tree = None
        RBRACK14_tree = None
        NEWLINE15_tree = None
        stream_65 = RewriteRuleTokenStream(self.adaptor, "token 65")
        stream_ASTERISK = RewriteRuleTokenStream(self.adaptor, "token ASTERISK")
        stream_RBRACK = RewriteRuleTokenStream(self.adaptor, "token RBRACK")
        stream_LBRACK = RewriteRuleTokenStream(self.adaptor, "token LBRACK")
        stream_NEWLINE = RewriteRuleTokenStream(self.adaptor, "token NEWLINE")
        stream_colitem = RewriteRuleSubtreeStream(self.adaptor, "rule colitem")
        try:
            try:
                # FMFpython.g:132:9: ( LBRACK ASTERISK 'data definitions' RBRACK NEWLINE ( colitem )+ -> ^( DATADEF_SECTION ^( HEADER ASTERISK 'data definitions' ) ^( BODY ( colitem )+ ) ) )
                # FMFpython.g:132:11: LBRACK ASTERISK 'data definitions' RBRACK NEWLINE ( colitem )+
                LBRACK11 = self.input.LT(1)
                self.match(self.input, LBRACK, self.FOLLOW_LBRACK_in_datadefSection1372)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_LBRACK.add(LBRACK11)
                ASTERISK12 = self.input.LT(1)
                self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_datadefSection1374)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_ASTERISK.add(ASTERISK12)
                string_literal13 = self.input.LT(1)
                self.match(self.input, 65, self.FOLLOW_65_in_datadefSection1376)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_65.add(string_literal13)
                RBRACK14 = self.input.LT(1)
                self.match(self.input, RBRACK, self.FOLLOW_RBRACK_in_datadefSection1378)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_RBRACK.add(RBRACK14)
                NEWLINE15 = self.input.LT(1)
                self.match(self.input, NEWLINE, self.FOLLOW_NEWLINE_in_datadefSection1380)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_NEWLINE.add(NEWLINE15)
                # FMFpython.g:132:61: ( colitem )+
                cnt3 = 0
                while True: #loop3
                    alt3 = 2
                    LA3_0 = self.input.LA(1)

                    if ((CONFIG <= LA3_0 <= COMMENT) or (RBRACK <= LA3_0 <= 67)) :
                        alt3 = 1


                    if alt3 == 1:
                        # FMFpython.g:132:61: colitem
                        self.following.append(self.FOLLOW_colitem_in_datadefSection1382)
                        colitem16 = self.colitem()
                        self.following.pop()
                        if self.failed:
                            return retval
                        if self.backtracking == 0:
                            stream_colitem.add(colitem16.tree)


                    else:
                        if cnt3 >= 1:
                            break #loop3

                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        eee = EarlyExitException(3, self.input)
                        raise eee

                    cnt3 += 1


                # AST Rewrite
                # elements: ASTERISK, 65, colitem
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 133:9: -> ^( DATADEF_SECTION ^( HEADER ASTERISK 'data definitions' ) ^( BODY ( colitem )+ ) )
                    # FMFpython.g:133:12: ^( DATADEF_SECTION ^( HEADER ASTERISK 'data definitions' ) ^( BODY ( colitem )+ ) )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(DATADEF_SECTION, "DATADEF_SECTION"), root_1)

                    # FMFpython.g:133:30: ^( HEADER ASTERISK 'data definitions' )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(HEADER, "HEADER"), root_2)

                    self.adaptor.addChild(root_2, stream_ASTERISK.next())
                    self.adaptor.addChild(root_2, stream_65.next())

                    self.adaptor.addChild(root_1, root_2)
                    # FMFpython.g:133:68: ^( BODY ( colitem )+ )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(BODY, "BODY"), root_2)

                    # FMFpython.g:133:75: ( colitem )+
                    if not (stream_colitem.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_colitem.hasNext():
                        self.adaptor.addChild(root_2, stream_colitem.next())


                    stream_colitem.reset()

                    self.adaptor.addChild(root_1, root_2)

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end datadefSection

    class dataSection_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start dataSection
    # FMFpython.g:135:1: dataSection : LBRACK ASTERISK 'data' RBRACK NEWLINE ( dataitem )* -> ^( DATA_SECTION ^( HEADER ASTERISK 'data' ) ^( BODY ( dataitem )* ) ) ;
    def dataSection(self, ):

        retval = self.dataSection_return()
        retval.start = self.input.LT(1)

        root_0 = None

        LBRACK17 = None
        ASTERISK18 = None
        string_literal19 = None
        RBRACK20 = None
        NEWLINE21 = None
        dataitem22 = None


        LBRACK17_tree = None
        ASTERISK18_tree = None
        string_literal19_tree = None
        RBRACK20_tree = None
        NEWLINE21_tree = None
        stream_ASTERISK = RewriteRuleTokenStream(self.adaptor, "token ASTERISK")
        stream_RBRACK = RewriteRuleTokenStream(self.adaptor, "token RBRACK")
        stream_66 = RewriteRuleTokenStream(self.adaptor, "token 66")
        stream_LBRACK = RewriteRuleTokenStream(self.adaptor, "token LBRACK")
        stream_NEWLINE = RewriteRuleTokenStream(self.adaptor, "token NEWLINE")
        stream_dataitem = RewriteRuleSubtreeStream(self.adaptor, "rule dataitem")
        try:
            try:
                # FMFpython.g:136:9: ( LBRACK ASTERISK 'data' RBRACK NEWLINE ( dataitem )* -> ^( DATA_SECTION ^( HEADER ASTERISK 'data' ) ^( BODY ( dataitem )* ) ) )
                # FMFpython.g:136:11: LBRACK ASTERISK 'data' RBRACK NEWLINE ( dataitem )*
                LBRACK17 = self.input.LT(1)
                self.match(self.input, LBRACK, self.FOLLOW_LBRACK_in_dataSection1428)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_LBRACK.add(LBRACK17)
                ASTERISK18 = self.input.LT(1)
                self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_dataSection1430)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_ASTERISK.add(ASTERISK18)
                string_literal19 = self.input.LT(1)
                self.match(self.input, 66, self.FOLLOW_66_in_dataSection1432)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_66.add(string_literal19)
                RBRACK20 = self.input.LT(1)
                self.match(self.input, RBRACK, self.FOLLOW_RBRACK_in_dataSection1434)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_RBRACK.add(RBRACK20)
                NEWLINE21 = self.input.LT(1)
                self.match(self.input, NEWLINE, self.FOLLOW_NEWLINE_in_dataSection1436)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_NEWLINE.add(NEWLINE21)
                # FMFpython.g:136:49: ( dataitem )*
                while True: #loop4
                    alt4 = 2
                    LA4_0 = self.input.LA(1)

                    if (LA4_0 == NPLUS or LA4_0 == NMINUS or (FLOAT <= LA4_0 <= IMAG) or LA4_0 == WORD or LA4_0 == LITERAL) :
                        alt4 = 1


                    if alt4 == 1:
                        # FMFpython.g:136:49: dataitem
                        self.following.append(self.FOLLOW_dataitem_in_dataSection1438)
                        dataitem22 = self.dataitem()
                        self.following.pop()
                        if self.failed:
                            return retval
                        if self.backtracking == 0:
                            stream_dataitem.add(dataitem22.tree)


                    else:
                        break #loop4


                # AST Rewrite
                # elements: 66, dataitem, ASTERISK
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 137:9: -> ^( DATA_SECTION ^( HEADER ASTERISK 'data' ) ^( BODY ( dataitem )* ) )
                    # FMFpython.g:137:12: ^( DATA_SECTION ^( HEADER ASTERISK 'data' ) ^( BODY ( dataitem )* ) )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(DATA_SECTION, "DATA_SECTION"), root_1)

                    # FMFpython.g:137:27: ^( HEADER ASTERISK 'data' )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(HEADER, "HEADER"), root_2)

                    self.adaptor.addChild(root_2, stream_ASTERISK.next())
                    self.adaptor.addChild(root_2, stream_66.next())

                    self.adaptor.addChild(root_1, root_2)
                    # FMFpython.g:137:53: ^( BODY ( dataitem )* )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(BODY, "BODY"), root_2)

                    # FMFpython.g:137:60: ( dataitem )*
                    while stream_dataitem.hasNext():
                        self.adaptor.addChild(root_2, stream_dataitem.next())


                    stream_dataitem.reset();

                    self.adaptor.addChild(root_1, root_2)

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end dataSection

    class commonSection_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start commonSection
    # FMFpython.g:139:1: commonSection : LBRACK headername RBRACK NEWLINE ( commonitem )+ -> ^( COMMON_SECTION ^( HEADER headername ) ^( BODY ( commonitem )+ ) ) ;
    def commonSection(self, ):

        retval = self.commonSection_return()
        retval.start = self.input.LT(1)

        root_0 = None

        LBRACK23 = None
        RBRACK25 = None
        NEWLINE26 = None
        headername24 = None

        commonitem27 = None


        LBRACK23_tree = None
        RBRACK25_tree = None
        NEWLINE26_tree = None
        stream_RBRACK = RewriteRuleTokenStream(self.adaptor, "token RBRACK")
        stream_LBRACK = RewriteRuleTokenStream(self.adaptor, "token LBRACK")
        stream_NEWLINE = RewriteRuleTokenStream(self.adaptor, "token NEWLINE")
        stream_commonitem = RewriteRuleSubtreeStream(self.adaptor, "rule commonitem")
        stream_headername = RewriteRuleSubtreeStream(self.adaptor, "rule headername")
        try:
            try:
                # FMFpython.g:140:9: ( LBRACK headername RBRACK NEWLINE ( commonitem )+ -> ^( COMMON_SECTION ^( HEADER headername ) ^( BODY ( commonitem )+ ) ) )
                # FMFpython.g:140:11: LBRACK headername RBRACK NEWLINE ( commonitem )+
                LBRACK23 = self.input.LT(1)
                self.match(self.input, LBRACK, self.FOLLOW_LBRACK_in_commonSection1484)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_LBRACK.add(LBRACK23)
                self.following.append(self.FOLLOW_headername_in_commonSection1486)
                headername24 = self.headername()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_headername.add(headername24.tree)
                RBRACK25 = self.input.LT(1)
                self.match(self.input, RBRACK, self.FOLLOW_RBRACK_in_commonSection1488)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_RBRACK.add(RBRACK25)
                NEWLINE26 = self.input.LT(1)
                self.match(self.input, NEWLINE, self.FOLLOW_NEWLINE_in_commonSection1490)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_NEWLINE.add(NEWLINE26)
                # FMFpython.g:140:44: ( commonitem )+
                cnt5 = 0
                while True: #loop5
                    alt5 = 2
                    LA5_0 = self.input.LA(1)

                    if ((CONFIG <= LA5_0 <= COMMENT) or (RBRACK <= LA5_0 <= 67)) :
                        alt5 = 1


                    if alt5 == 1:
                        # FMFpython.g:140:44: commonitem
                        self.following.append(self.FOLLOW_commonitem_in_commonSection1492)
                        commonitem27 = self.commonitem()
                        self.following.pop()
                        if self.failed:
                            return retval
                        if self.backtracking == 0:
                            stream_commonitem.add(commonitem27.tree)


                    else:
                        if cnt5 >= 1:
                            break #loop5

                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        eee = EarlyExitException(5, self.input)
                        raise eee

                    cnt5 += 1


                # AST Rewrite
                # elements: headername, commonitem
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 141:9: -> ^( COMMON_SECTION ^( HEADER headername ) ^( BODY ( commonitem )+ ) )
                    # FMFpython.g:141:12: ^( COMMON_SECTION ^( HEADER headername ) ^( BODY ( commonitem )+ ) )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(COMMON_SECTION, "COMMON_SECTION"), root_1)

                    # FMFpython.g:141:29: ^( HEADER headername )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(HEADER, "HEADER"), root_2)

                    self.adaptor.addChild(root_2, stream_headername.next())

                    self.adaptor.addChild(root_1, root_2)
                    # FMFpython.g:141:50: ^( BODY ( commonitem )+ )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(BODY, "BODY"), root_2)

                    # FMFpython.g:141:57: ( commonitem )+
                    if not (stream_commonitem.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_commonitem.hasNext():
                        self.adaptor.addChild(root_2, stream_commonitem.next())


                    stream_commonitem.reset()

                    self.adaptor.addChild(root_1, root_2)

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end commonSection

    class headername_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start headername
    # FMFpython.g:143:1: headername : ~ ASTERISK ( . )* ;
    def headername(self, ):

        retval = self.headername_return()
        retval.start = self.input.LT(1)

        root_0 = None

        set28 = None
        wildcard29 = None

        set28_tree = None
        wildcard29_tree = None

        try:
            try:
                # FMFpython.g:144:9: (~ ASTERISK ( . )* )
                # FMFpython.g:144:11: ~ ASTERISK ( . )*
                root_0 = self.adaptor.nil()

                set28 = self.input.LT(1)
                if (CONFIG <= self.input.LA(1) <= RPAREN) or (COLON <= self.input.LA(1) <= 67):
                    self.input.consume();
                    if self.backtracking == 0:
                        self.adaptor.addChild(root_0, self.adaptor.createWithPayload(set28))
                    self.errorRecovery = False
                    self.failed = False

                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return retval

                    mse = MismatchedSetException(None, self.input)
                    self.recoverFromMismatchedSet(
                        self.input, mse, self.FOLLOW_set_in_headername1536
                        )
                    raise mse


                # FMFpython.g:144:21: ( . )*
                while True: #loop6
                    alt6 = 2
                    LA6_0 = self.input.LA(1)

                    if (LA6_0 == RBRACK) :
                        alt6 = 2
                    elif ((CONFIG <= LA6_0 <= LBRACK) or (LPAREN <= LA6_0 <= 67)) :
                        alt6 = 1


                    if alt6 == 1:
                        # FMFpython.g:144:21: .
                        wildcard29 = self.input.LT(1)
                        self.matchAny(self.input)
                        if self.failed:
                            return retval
                        if self.backtracking == 0:

                            wildcard29_tree = self.adaptor.createWithPayload(wildcard29)
                            self.adaptor.addChild(root_0, wildcard29_tree)


                    else:
                        break #loop6





                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end headername

    class colitem_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start colitem
    # FMFpython.g:146:1: colitem : key COLON colspec NEWLINE -> ^( COLSPEC ^( LONGNAME key ) colspec ) ;
    def colitem(self, ):

        retval = self.colitem_return()
        retval.start = self.input.LT(1)

        root_0 = None

        COLON31 = None
        NEWLINE33 = None
        key30 = None

        colspec32 = None


        COLON31_tree = None
        NEWLINE33_tree = None
        stream_COLON = RewriteRuleTokenStream(self.adaptor, "token COLON")
        stream_NEWLINE = RewriteRuleTokenStream(self.adaptor, "token NEWLINE")
        stream_key = RewriteRuleSubtreeStream(self.adaptor, "rule key")
        stream_colspec = RewriteRuleSubtreeStream(self.adaptor, "rule colspec")
        try:
            try:
                # FMFpython.g:146:9: ( key COLON colspec NEWLINE -> ^( COLSPEC ^( LONGNAME key ) colspec ) )
                # FMFpython.g:146:11: key COLON colspec NEWLINE
                self.following.append(self.FOLLOW_key_in_colitem1548)
                key30 = self.key()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_key.add(key30.tree)
                COLON31 = self.input.LT(1)
                self.match(self.input, COLON, self.FOLLOW_COLON_in_colitem1550)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_COLON.add(COLON31)
                self.following.append(self.FOLLOW_colspec_in_colitem1552)
                colspec32 = self.colspec()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_colspec.add(colspec32.tree)
                NEWLINE33 = self.input.LT(1)
                self.match(self.input, NEWLINE, self.FOLLOW_NEWLINE_in_colitem1554)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_NEWLINE.add(NEWLINE33)
                # AST Rewrite
                # elements: colspec, key
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 146:37: -> ^( COLSPEC ^( LONGNAME key ) colspec )
                    # FMFpython.g:146:40: ^( COLSPEC ^( LONGNAME key ) colspec )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(COLSPEC, "COLSPEC"), root_1)

                    # FMFpython.g:146:50: ^( LONGNAME key )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(LONGNAME, "LONGNAME"), root_2)

                    self.adaptor.addChild(root_2, stream_key.next())

                    self.adaptor.addChild(root_1, root_2)
                    self.adaptor.addChild(root_1, stream_colspec.next())

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end colitem

    class dataitem_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start dataitem
    # FMFpython.g:147:1: dataitem : ( cell )+ NEWLINE -> ^( DATASET ( cell )+ ) ;
    def dataitem(self, ):

        retval = self.dataitem_return()
        retval.start = self.input.LT(1)

        root_0 = None

        NEWLINE35 = None
        cell34 = None


        NEWLINE35_tree = None
        stream_NEWLINE = RewriteRuleTokenStream(self.adaptor, "token NEWLINE")
        stream_cell = RewriteRuleSubtreeStream(self.adaptor, "rule cell")
        try:
            try:
                # FMFpython.g:148:9: ( ( cell )+ NEWLINE -> ^( DATASET ( cell )+ ) )
                # FMFpython.g:148:11: ( cell )+ NEWLINE
                # FMFpython.g:148:11: ( cell )+
                cnt7 = 0
                while True: #loop7
                    alt7 = 2
                    LA7_0 = self.input.LA(1)

                    if (LA7_0 == NPLUS or LA7_0 == NMINUS or (FLOAT <= LA7_0 <= IMAG) or LA7_0 == WORD or LA7_0 == LITERAL) :
                        alt7 = 1


                    if alt7 == 1:
                        # FMFpython.g:148:11: cell
                        self.following.append(self.FOLLOW_cell_in_dataitem1583)
                        cell34 = self.cell()
                        self.following.pop()
                        if self.failed:
                            return retval
                        if self.backtracking == 0:
                            stream_cell.add(cell34.tree)


                    else:
                        if cnt7 >= 1:
                            break #loop7

                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        eee = EarlyExitException(7, self.input)
                        raise eee

                    cnt7 += 1


                NEWLINE35 = self.input.LT(1)
                self.match(self.input, NEWLINE, self.FOLLOW_NEWLINE_in_dataitem1586)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_NEWLINE.add(NEWLINE35)
                # AST Rewrite
                # elements: cell
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 148:25: -> ^( DATASET ( cell )+ )
                    # FMFpython.g:148:28: ^( DATASET ( cell )+ )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(DATASET, "DATASET"), root_1)

                    # FMFpython.g:148:38: ( cell )+
                    if not (stream_cell.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_cell.hasNext():
                        self.adaptor.addChild(root_1, stream_cell.next())


                    stream_cell.reset()

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end dataitem

    class commonitem_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start commonitem
    # FMFpython.g:149:1: commonitem : key COLON value NEWLINE -> ^( ITEM ^( KEY key ) value ) ;
    def commonitem(self, ):

        retval = self.commonitem_return()
        retval.start = self.input.LT(1)

        root_0 = None

        COLON37 = None
        NEWLINE39 = None
        key36 = None

        value38 = None


        COLON37_tree = None
        NEWLINE39_tree = None
        stream_COLON = RewriteRuleTokenStream(self.adaptor, "token COLON")
        stream_NEWLINE = RewriteRuleTokenStream(self.adaptor, "token NEWLINE")
        stream_key = RewriteRuleSubtreeStream(self.adaptor, "rule key")
        stream_value = RewriteRuleSubtreeStream(self.adaptor, "rule value")
        try:
            try:
                # FMFpython.g:150:9: ( key COLON value NEWLINE -> ^( ITEM ^( KEY key ) value ) )
                # FMFpython.g:150:11: key COLON value NEWLINE
                self.following.append(self.FOLLOW_key_in_commonitem1610)
                key36 = self.key()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_key.add(key36.tree)
                COLON37 = self.input.LT(1)
                self.match(self.input, COLON, self.FOLLOW_COLON_in_commonitem1612)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_COLON.add(COLON37)
                self.following.append(self.FOLLOW_value_in_commonitem1614)
                value38 = self.value()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_value.add(value38.tree)
                NEWLINE39 = self.input.LT(1)
                self.match(self.input, NEWLINE, self.FOLLOW_NEWLINE_in_commonitem1616)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_NEWLINE.add(NEWLINE39)
                # AST Rewrite
                # elements: value, key
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 150:37: -> ^( ITEM ^( KEY key ) value )
                    # FMFpython.g:150:40: ^( ITEM ^( KEY key ) value )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(ITEM, "ITEM"), root_1)

                    # FMFpython.g:150:47: ^( KEY key )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(KEY, "KEY"), root_2)

                    self.adaptor.addChild(root_2, stream_key.next())

                    self.adaptor.addChild(root_1, root_2)
                    self.adaptor.addChild(root_1, stream_value.next())

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end commonitem

    class cell_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start cell
    # FMFpython.g:152:1: cell : ( number -> ^( NUMBER number ) | WORD -> ^( STRING WORD ) | LITERAL -> ^( STRING LITERAL ) );
    def cell(self, ):

        retval = self.cell_return()
        retval.start = self.input.LT(1)

        root_0 = None

        WORD41 = None
        LITERAL42 = None
        number40 = None


        WORD41_tree = None
        LITERAL42_tree = None
        stream_LITERAL = RewriteRuleTokenStream(self.adaptor, "token LITERAL")
        stream_WORD = RewriteRuleTokenStream(self.adaptor, "token WORD")
        stream_number = RewriteRuleSubtreeStream(self.adaptor, "rule number")
        try:
            try:
                # FMFpython.g:152:9: ( number -> ^( NUMBER number ) | WORD -> ^( STRING WORD ) | LITERAL -> ^( STRING LITERAL ) )
                alt8 = 3
                LA8 = self.input.LA(1)
                if LA8 == NPLUS or LA8 == NMINUS or LA8 == FLOAT or LA8 == INT or LA8 == IMAG:
                    alt8 = 1
                elif LA8 == WORD:
                    alt8 = 2
                elif LA8 == LITERAL:
                    alt8 = 3
                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return retval

                    nvae = NoViableAltException("152:1: cell : ( number -> ^( NUMBER number ) | WORD -> ^( STRING WORD ) | LITERAL -> ^( STRING LITERAL ) );", 8, 0, self.input)

                    raise nvae

                if alt8 == 1:
                    # FMFpython.g:152:17: number
                    self.following.append(self.FOLLOW_number_in_cell1649)
                    number40 = self.number()
                    self.following.pop()
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_number.add(number40.tree)
                    # AST Rewrite
                    # elements: number
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    if self.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                        root_0 = self.adaptor.nil()
                        # 152:25: -> ^( NUMBER number )
                        # FMFpython.g:152:28: ^( NUMBER number )
                        root_1 = self.adaptor.nil()
                        root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(NUMBER, "NUMBER"), root_1)

                        self.adaptor.addChild(root_1, stream_number.next())

                        self.adaptor.addChild(root_0, root_1)





                elif alt8 == 2:
                    # FMFpython.g:153:17: WORD
                    WORD41 = self.input.LT(1)
                    self.match(self.input, WORD, self.FOLLOW_WORD_in_cell1676)
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_WORD.add(WORD41)
                    # AST Rewrite
                    # elements: WORD
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    if self.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                        root_0 = self.adaptor.nil()
                        # 153:25: -> ^( STRING WORD )
                        # FMFpython.g:153:28: ^( STRING WORD )
                        root_1 = self.adaptor.nil()
                        root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(STRING, "STRING"), root_1)

                        self.adaptor.addChild(root_1, stream_WORD.next())

                        self.adaptor.addChild(root_0, root_1)





                elif alt8 == 3:
                    # FMFpython.g:154:17: LITERAL
                    LITERAL42 = self.input.LT(1)
                    self.match(self.input, LITERAL, self.FOLLOW_LITERAL_in_cell1705)
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_LITERAL.add(LITERAL42)
                    # AST Rewrite
                    # elements: LITERAL
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    if self.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                        root_0 = self.adaptor.nil()
                        # 154:25: -> ^( STRING LITERAL )
                        # FMFpython.g:154:28: ^( STRING LITERAL )
                        root_1 = self.adaptor.nil()
                        root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(STRING, "STRING"), root_1)

                        self.adaptor.addChild(root_1, stream_LITERAL.next())

                        self.adaptor.addChild(root_0, root_1)





                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end cell

    class colspec_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start colspec
    # FMFpython.g:157:1: colspec : identifier ( deps )? ( LBRACK unit RBRACK )? -> ^( IDENTIFIER identifier ) ^( DEPS ( deps )? ) ^( UNIT ( unit )? ) ;
    def colspec(self, ):

        retval = self.colspec_return()
        retval.start = self.input.LT(1)

        root_0 = None

        LBRACK45 = None
        RBRACK47 = None
        identifier43 = None

        deps44 = None

        unit46 = None


        LBRACK45_tree = None
        RBRACK47_tree = None
        stream_RBRACK = RewriteRuleTokenStream(self.adaptor, "token RBRACK")
        stream_LBRACK = RewriteRuleTokenStream(self.adaptor, "token LBRACK")
        stream_unit = RewriteRuleSubtreeStream(self.adaptor, "rule unit")
        stream_identifier = RewriteRuleSubtreeStream(self.adaptor, "rule identifier")
        stream_deps = RewriteRuleSubtreeStream(self.adaptor, "rule deps")
        try:
            try:
                # FMFpython.g:157:9: ( identifier ( deps )? ( LBRACK unit RBRACK )? -> ^( IDENTIFIER identifier ) ^( DEPS ( deps )? ) ^( UNIT ( unit )? ) )
                # FMFpython.g:157:11: identifier ( deps )? ( LBRACK unit RBRACK )?
                self.following.append(self.FOLLOW_identifier_in_colspec1730)
                identifier43 = self.identifier()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_identifier.add(identifier43.tree)
                # FMFpython.g:157:22: ( deps )?
                alt9 = 2
                LA9_0 = self.input.LA(1)

                if (LA9_0 == LPAREN) :
                    alt9 = 1
                if alt9 == 1:
                    # FMFpython.g:157:22: deps
                    self.following.append(self.FOLLOW_deps_in_colspec1732)
                    deps44 = self.deps()
                    self.following.pop()
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_deps.add(deps44.tree)



                # FMFpython.g:157:28: ( LBRACK unit RBRACK )?
                alt10 = 2
                LA10_0 = self.input.LA(1)

                if (LA10_0 == LBRACK) :
                    alt10 = 1
                if alt10 == 1:
                    # FMFpython.g:157:29: LBRACK unit RBRACK
                    LBRACK45 = self.input.LT(1)
                    self.match(self.input, LBRACK, self.FOLLOW_LBRACK_in_colspec1736)
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_LBRACK.add(LBRACK45)
                    self.following.append(self.FOLLOW_unit_in_colspec1738)
                    unit46 = self.unit()
                    self.following.pop()
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_unit.add(unit46.tree)
                    RBRACK47 = self.input.LT(1)
                    self.match(self.input, RBRACK, self.FOLLOW_RBRACK_in_colspec1740)
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_RBRACK.add(RBRACK47)



                # AST Rewrite
                # elements: identifier, deps, unit
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 157:50: -> ^( IDENTIFIER identifier ) ^( DEPS ( deps )? ) ^( UNIT ( unit )? )
                    # FMFpython.g:157:53: ^( IDENTIFIER identifier )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(IDENTIFIER, "IDENTIFIER"), root_1)

                    self.adaptor.addChild(root_1, stream_identifier.next())

                    self.adaptor.addChild(root_0, root_1)
                    # FMFpython.g:157:78: ^( DEPS ( deps )? )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(DEPS, "DEPS"), root_1)

                    # FMFpython.g:157:85: ( deps )?
                    if stream_deps.hasNext():
                        self.adaptor.addChild(root_1, stream_deps.next())


                    stream_deps.reset();

                    self.adaptor.addChild(root_0, root_1)
                    # FMFpython.g:157:92: ^( UNIT ( unit )? )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(UNIT, "UNIT"), root_1)

                    # FMFpython.g:157:99: ( unit )?
                    if stream_unit.hasNext():
                        self.adaptor.addChild(root_1, stream_unit.next())


                    stream_unit.reset();

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end colspec

    class deps_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start deps
    # FMFpython.g:159:1: deps : LPAREN identifier ( ',' identifier )* RPAREN -> ( identifier )+ ;
    def deps(self, ):

        retval = self.deps_return()
        retval.start = self.input.LT(1)

        root_0 = None

        LPAREN48 = None
        char_literal50 = None
        RPAREN52 = None
        identifier49 = None

        identifier51 = None


        LPAREN48_tree = None
        char_literal50_tree = None
        RPAREN52_tree = None
        stream_RPAREN = RewriteRuleTokenStream(self.adaptor, "token RPAREN")
        stream_LPAREN = RewriteRuleTokenStream(self.adaptor, "token LPAREN")
        stream_67 = RewriteRuleTokenStream(self.adaptor, "token 67")
        stream_identifier = RewriteRuleSubtreeStream(self.adaptor, "rule identifier")
        try:
            try:
                # FMFpython.g:159:9: ( LPAREN identifier ( ',' identifier )* RPAREN -> ( identifier )+ )
                # FMFpython.g:159:11: LPAREN identifier ( ',' identifier )* RPAREN
                LPAREN48 = self.input.LT(1)
                self.match(self.input, LPAREN, self.FOLLOW_LPAREN_in_deps1775)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_LPAREN.add(LPAREN48)
                self.following.append(self.FOLLOW_identifier_in_deps1777)
                identifier49 = self.identifier()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_identifier.add(identifier49.tree)
                # FMFpython.g:159:29: ( ',' identifier )*
                while True: #loop11
                    alt11 = 2
                    LA11_0 = self.input.LA(1)

                    if (LA11_0 == 67) :
                        alt11 = 1


                    if alt11 == 1:
                        # FMFpython.g:159:31: ',' identifier
                        char_literal50 = self.input.LT(1)
                        self.match(self.input, 67, self.FOLLOW_67_in_deps1781)
                        if self.failed:
                            return retval
                        if self.backtracking == 0:
                            stream_67.add(char_literal50)
                        self.following.append(self.FOLLOW_identifier_in_deps1783)
                        identifier51 = self.identifier()
                        self.following.pop()
                        if self.failed:
                            return retval
                        if self.backtracking == 0:
                            stream_identifier.add(identifier51.tree)


                    else:
                        break #loop11


                RPAREN52 = self.input.LT(1)
                self.match(self.input, RPAREN, self.FOLLOW_RPAREN_in_deps1787)
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_RPAREN.add(RPAREN52)
                # AST Rewrite
                # elements: identifier
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 159:55: -> ( identifier )+
                    # FMFpython.g:159:58: ( identifier )+
                    if not (stream_identifier.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_identifier.hasNext():
                        self.adaptor.addChild(root_0, stream_identifier.next())


                    stream_identifier.reset()






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end deps

    class key_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start key
    # FMFpython.g:161:1: key : ~ LBRACK ( . )* ;
    def key(self, ):

        retval = self.key_return()
        retval.start = self.input.LT(1)

        root_0 = None

        set53 = None
        wildcard54 = None

        set53_tree = None
        wildcard54_tree = None

        try:
            try:
                # FMFpython.g:161:9: (~ LBRACK ( . )* )
                # FMFpython.g:161:11: ~ LBRACK ( . )*
                root_0 = self.adaptor.nil()

                set53 = self.input.LT(1)
                if (CONFIG <= self.input.LA(1) <= COMMENT) or (RBRACK <= self.input.LA(1) <= 67):
                    self.input.consume();
                    if self.backtracking == 0:
                        self.adaptor.addChild(root_0, self.adaptor.createWithPayload(set53))
                    self.errorRecovery = False
                    self.failed = False

                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return retval

                    mse = MismatchedSetException(None, self.input)
                    self.recoverFromMismatchedSet(
                        self.input, mse, self.FOLLOW_set_in_key1804
                        )
                    raise mse


                # FMFpython.g:161:19: ( . )*
                while True: #loop12
                    alt12 = 2
                    LA12_0 = self.input.LA(1)

                    if (LA12_0 == COLON) :
                        alt12 = 2
                    elif ((CONFIG <= LA12_0 <= ASTERISK) or (EQUALS <= LA12_0 <= 67)) :
                        alt12 = 1


                    if alt12 == 1:
                        # FMFpython.g:161:19: .
                        wildcard54 = self.input.LT(1)
                        self.matchAny(self.input)
                        if self.failed:
                            return retval
                        if self.backtracking == 0:

                            wildcard54_tree = self.adaptor.createWithPayload(wildcard54)
                            self.adaptor.addChild(root_0, wildcard54_tree)


                    else:
                        break #loop12





                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end key

    class value_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start value
    # FMFpython.g:163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );
    def value(self, ):

        retval = self.value_return()
        retval.start = self.input.LT(1)
        value_StartIndex = self.input.index()
        root_0 = None

        EQUALS57 = None
        number55 = None

        identifier56 = None

        quantity58 = None

        datetime59 = None

        catchall60 = None


        EQUALS57_tree = None
        stream_EQUALS = RewriteRuleTokenStream(self.adaptor, "token EQUALS")
        stream_datetime = RewriteRuleSubtreeStream(self.adaptor, "rule datetime")
        stream_identifier = RewriteRuleSubtreeStream(self.adaptor, "rule identifier")
        stream_catchall = RewriteRuleSubtreeStream(self.adaptor, "rule catchall")
        stream_quantity = RewriteRuleSubtreeStream(self.adaptor, "rule quantity")
        stream_number = RewriteRuleSubtreeStream(self.adaptor, "rule number")
        try:
            try:
                if self.backtracking > 0 and self.alreadyParsedRule(self.input, 14):
                    return retval

                # FMFpython.g:168:9: ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) )
                alt13 = 4
                LA13 = self.input.LA(1)
                if LA13 == NPLUS or LA13 == NMINUS:
                    LA13 = self.input.LA(2)
                    if LA13 == CONFIG or LA13 == HEADER or LA13 == COMMON_SECTION or LA13 == DATADEF_SECTION or LA13 == DATA_SECTION or LA13 == BODY or LA13 == ITEM or LA13 == DATASET or LA13 == KEY or LA13 == DATETIME or LA13 == DATE or LA13 == TIME or LA13 == NUMBER or LA13 == VARIABLE or LA13 == IDENTIFIER or LA13 == QUANTITY or LA13 == UNIT or LA13 == STRING or LA13 == COLSPEC or LA13 == LONGNAME or LA13 == DEPS or LA13 == NEWLINE or LA13 == WS or LA13 == COMMENT or LA13 == LBRACK or LA13 == RBRACK or LA13 == LPAREN or LA13 == RPAREN or LA13 == ASTERISK or LA13 == COLON or LA13 == EQUALS or LA13 == PLUS or LA13 == NPLUS or LA13 == DIGIT or LA13 == MINUS or LA13 == NMINUS or LA13 == LCURLY or LA13 == RCURLY or LA13 == UNDERSCORE or LA13 == HAT or LA13 == DIV or LA13 == DOLLAR or LA13 == PERCENTAGE or LA13 == LESSTHAN or LA13 == GREATERTHAN or LA13 == DIGITS or LA13 == LETTERS or LA13 == EXPONENT or LA13 == FFLOAT or LA13 == IINT or LA13 == ESC or LA13 == GERMANDATE or LA13 == ISODATE or LA13 == RWORD or LA13 == WORD or LA13 == PUNCTUATION or LA13 == LITERAL or LA13 == 64 or LA13 == 65 or LA13 == 66 or LA13 == 67:
                        alt13 = 4
                    elif LA13 == FLOAT:
                        LA13_2 = self.input.LA(3)

                        if (self.synpred1()) :
                            alt13 = 1
                        elif (True) :
                            alt13 = 4
                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return retval

                            nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 2, self.input)

                            raise nvae

                    elif LA13 == INT:
                        LA13_3 = self.input.LA(3)

                        if (self.synpred1()) :
                            alt13 = 1
                        elif (True) :
                            alt13 = 4
                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return retval

                            nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 3, self.input)

                            raise nvae

                    elif LA13 == IMAG:
                        LA13_4 = self.input.LA(3)

                        if (self.synpred1()) :
                            alt13 = 1
                        elif (True) :
                            alt13 = 4
                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return retval

                            nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 4, self.input)

                            raise nvae

                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 1, self.input)

                        raise nvae

                elif LA13 == FLOAT:
                    LA13_2 = self.input.LA(2)

                    if (self.synpred1()) :
                        alt13 = 1
                    elif (True) :
                        alt13 = 4
                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 2, self.input)

                        raise nvae

                elif LA13 == INT:
                    LA13_3 = self.input.LA(2)

                    if (self.synpred1()) :
                        alt13 = 1
                    elif (True) :
                        alt13 = 4
                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 3, self.input)

                        raise nvae

                elif LA13 == IMAG:
                    LA13_4 = self.input.LA(2)

                    if (self.synpred1()) :
                        alt13 = 1
                    elif (True) :
                        alt13 = 4
                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 4, self.input)

                        raise nvae

                elif LA13 == WORD:
                    LA13_5 = self.input.LA(2)

                    if (LA13_5 == EQUALS) :
                        LA13 = self.input.LA(3)
                        if LA13 == CONFIG or LA13 == HEADER or LA13 == COMMON_SECTION or LA13 == DATADEF_SECTION or LA13 == DATA_SECTION or LA13 == BODY or LA13 == ITEM or LA13 == DATASET or LA13 == KEY or LA13 == DATETIME or LA13 == DATE or LA13 == TIME or LA13 == NUMBER or LA13 == VARIABLE or LA13 == IDENTIFIER or LA13 == QUANTITY or LA13 == UNIT or LA13 == STRING or LA13 == COLSPEC or LA13 == LONGNAME or LA13 == DEPS or LA13 == NEWLINE or LA13 == WS or LA13 == COMMENT or LA13 == LBRACK or LA13 == RBRACK or LA13 == LPAREN or LA13 == RPAREN or LA13 == ASTERISK or LA13 == COLON or LA13 == EQUALS or LA13 == PLUS or LA13 == DIGIT or LA13 == MINUS or LA13 == LCURLY or LA13 == RCURLY or LA13 == UNDERSCORE or LA13 == HAT or LA13 == DIV or LA13 == DOLLAR or LA13 == PERCENTAGE or LA13 == LESSTHAN or LA13 == GREATERTHAN or LA13 == DIGITS or LA13 == LETTERS or LA13 == EXPONENT or LA13 == FFLOAT or LA13 == IINT or LA13 == ESC or LA13 == GERMANDATE or LA13 == ISODATE or LA13 == RWORD or LA13 == WORD or LA13 == PUNCTUATION or LA13 == LITERAL or LA13 == 64 or LA13 == 65 or LA13 == 66 or LA13 == 67:
                            alt13 = 4
                        elif LA13 == NPLUS or LA13 == NMINUS:
                            LA13 = self.input.LA(4)
                            if LA13 == CONFIG or LA13 == HEADER or LA13 == COMMON_SECTION or LA13 == DATADEF_SECTION or LA13 == DATA_SECTION or LA13 == BODY or LA13 == ITEM or LA13 == DATASET or LA13 == KEY or LA13 == DATETIME or LA13 == DATE or LA13 == TIME or LA13 == NUMBER or LA13 == VARIABLE or LA13 == IDENTIFIER or LA13 == QUANTITY or LA13 == UNIT or LA13 == STRING or LA13 == COLSPEC or LA13 == LONGNAME or LA13 == DEPS or LA13 == NEWLINE or LA13 == WS or LA13 == COMMENT or LA13 == LBRACK or LA13 == RBRACK or LA13 == LPAREN or LA13 == RPAREN or LA13 == ASTERISK or LA13 == COLON or LA13 == EQUALS or LA13 == PLUS or LA13 == NPLUS or LA13 == DIGIT or LA13 == MINUS or LA13 == NMINUS or LA13 == LCURLY or LA13 == RCURLY or LA13 == UNDERSCORE or LA13 == HAT or LA13 == DIV or LA13 == DOLLAR or LA13 == PERCENTAGE or LA13 == LESSTHAN or LA13 == GREATERTHAN or LA13 == DIGITS or LA13 == LETTERS or LA13 == EXPONENT or LA13 == FFLOAT or LA13 == IINT or LA13 == ESC or LA13 == GERMANDATE or LA13 == ISODATE or LA13 == RWORD or LA13 == WORD or LA13 == PUNCTUATION or LA13 == LITERAL or LA13 == 64 or LA13 == 65 or LA13 == 66 or LA13 == 67:
                                alt13 = 4
                            elif LA13 == FLOAT:
                                LA13_13 = self.input.LA(5)

                                if (self.synpred2()) :
                                    alt13 = 2
                                elif (True) :
                                    alt13 = 4
                                else:
                                    if self.backtracking > 0:
                                        self.failed = True
                                        return retval

                                    nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 13, self.input)

                                    raise nvae

                            elif LA13 == INT:
                                LA13_14 = self.input.LA(5)

                                if (self.synpred2()) :
                                    alt13 = 2
                                elif (True) :
                                    alt13 = 4
                                else:
                                    if self.backtracking > 0:
                                        self.failed = True
                                        return retval

                                    nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 14, self.input)

                                    raise nvae

                            elif LA13 == IMAG:
                                LA13_15 = self.input.LA(5)

                                if (self.synpred2()) :
                                    alt13 = 2
                                elif (True) :
                                    alt13 = 4
                                else:
                                    if self.backtracking > 0:
                                        self.failed = True
                                        return retval

                                    nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 15, self.input)

                                    raise nvae

                            else:
                                if self.backtracking > 0:
                                    self.failed = True
                                    return retval

                                nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 12, self.input)

                                raise nvae

                        elif LA13 == FLOAT:
                            LA13_13 = self.input.LA(4)

                            if (self.synpred2()) :
                                alt13 = 2
                            elif (True) :
                                alt13 = 4
                            else:
                                if self.backtracking > 0:
                                    self.failed = True
                                    return retval

                                nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 13, self.input)

                                raise nvae

                        elif LA13 == INT:
                            LA13_14 = self.input.LA(4)

                            if (self.synpred2()) :
                                alt13 = 2
                            elif (True) :
                                alt13 = 4
                            else:
                                if self.backtracking > 0:
                                    self.failed = True
                                    return retval

                                nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 14, self.input)

                                raise nvae

                        elif LA13 == IMAG:
                            LA13_15 = self.input.LA(4)

                            if (self.synpred2()) :
                                alt13 = 2
                            elif (True) :
                                alt13 = 4
                            else:
                                if self.backtracking > 0:
                                    self.failed = True
                                    return retval

                                nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 15, self.input)

                                raise nvae

                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return retval

                            nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 10, self.input)

                            raise nvae

                    elif ((CONFIG <= LA13_5 <= COLON) or (PLUS <= LA13_5 <= 67)) :
                        alt13 = 4
                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 5, self.input)

                        raise nvae

                elif LA13 == GERMANDATE or LA13 == ISODATE:
                    LA13_6 = self.input.LA(2)

                    if (self.synpred3()) :
                        alt13 = 3
                    elif (True) :
                        alt13 = 4
                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 6, self.input)

                        raise nvae

                elif LA13 == CONFIG or LA13 == HEADER or LA13 == COMMON_SECTION or LA13 == DATADEF_SECTION or LA13 == DATA_SECTION or LA13 == BODY or LA13 == ITEM or LA13 == DATASET or LA13 == KEY or LA13 == DATETIME or LA13 == DATE or LA13 == TIME or LA13 == NUMBER or LA13 == VARIABLE or LA13 == IDENTIFIER or LA13 == QUANTITY or LA13 == UNIT or LA13 == STRING or LA13 == COLSPEC or LA13 == LONGNAME or LA13 == DEPS or LA13 == NEWLINE or LA13 == WS or LA13 == COMMENT or LA13 == LBRACK or LA13 == RBRACK or LA13 == LPAREN or LA13 == RPAREN or LA13 == ASTERISK or LA13 == COLON or LA13 == EQUALS or LA13 == PLUS or LA13 == DIGIT or LA13 == MINUS or LA13 == LCURLY or LA13 == RCURLY or LA13 == UNDERSCORE or LA13 == HAT or LA13 == DIV or LA13 == DOLLAR or LA13 == PERCENTAGE or LA13 == LESSTHAN or LA13 == GREATERTHAN or LA13 == DIGITS or LA13 == LETTERS or LA13 == EXPONENT or LA13 == FFLOAT or LA13 == IINT or LA13 == ESC or LA13 == RWORD or LA13 == PUNCTUATION or LA13 == LITERAL or LA13 == 64 or LA13 == 65 or LA13 == 66 or LA13 == 67:
                    alt13 = 4
                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return retval

                    nvae = NoViableAltException("163:1: value options {backtrack=true; memoize=true; } : ( number -> ^( NUMBER number ) | identifier EQUALS quantity -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity ) | datetime -> datetime | catchall -> ^( STRING catchall ) );", 13, 0, self.input)

                    raise nvae

                if alt13 == 1:
                    # FMFpython.g:168:17: number
                    self.following.append(self.FOLLOW_number_in_value1852)
                    number55 = self.number()
                    self.following.pop()
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_number.add(number55.tree)
                    # AST Rewrite
                    # elements: number
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    if self.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                        root_0 = self.adaptor.nil()
                        # 168:44: -> ^( NUMBER number )
                        # FMFpython.g:168:47: ^( NUMBER number )
                        root_1 = self.adaptor.nil()
                        root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(NUMBER, "NUMBER"), root_1)

                        self.adaptor.addChild(root_1, stream_number.next())

                        self.adaptor.addChild(root_0, root_1)





                elif alt13 == 2:
                    # FMFpython.g:169:17: identifier EQUALS quantity
                    self.following.append(self.FOLLOW_identifier_in_value1898)
                    identifier56 = self.identifier()
                    self.following.pop()
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_identifier.add(identifier56.tree)
                    EQUALS57 = self.input.LT(1)
                    self.match(self.input, EQUALS, self.FOLLOW_EQUALS_in_value1900)
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_EQUALS.add(EQUALS57)
                    self.following.append(self.FOLLOW_quantity_in_value1902)
                    quantity58 = self.quantity()
                    self.following.pop()
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_quantity.add(quantity58.tree)
                    # AST Rewrite
                    # elements: quantity, identifier
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    if self.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                        root_0 = self.adaptor.nil()
                        # 169:44: -> ^( VARIABLE ^( IDENTIFIER identifier ) quantity )
                        # FMFpython.g:169:47: ^( VARIABLE ^( IDENTIFIER identifier ) quantity )
                        root_1 = self.adaptor.nil()
                        root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(VARIABLE, "VARIABLE"), root_1)

                        # FMFpython.g:169:58: ^( IDENTIFIER identifier )
                        root_2 = self.adaptor.nil()
                        root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(IDENTIFIER, "IDENTIFIER"), root_2)

                        self.adaptor.addChild(root_2, stream_identifier.next())

                        self.adaptor.addChild(root_1, root_2)
                        self.adaptor.addChild(root_1, stream_quantity.next())

                        self.adaptor.addChild(root_0, root_1)





                elif alt13 == 3:
                    # FMFpython.g:170:17: datetime
                    self.following.append(self.FOLLOW_datetime_in_value1934)
                    datetime59 = self.datetime()
                    self.following.pop()
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_datetime.add(datetime59.tree)
                    # AST Rewrite
                    # elements: datetime
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    if self.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                        root_0 = self.adaptor.nil()
                        # 170:44: -> datetime
                        self.adaptor.addChild(root_0, stream_datetime.next())





                elif alt13 == 4:
                    # FMFpython.g:171:17: catchall
                    self.following.append(self.FOLLOW_catchall_in_value1974)
                    catchall60 = self.catchall()
                    self.following.pop()
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_catchall.add(catchall60.tree)
                    # AST Rewrite
                    # elements: catchall
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    if self.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                        root_0 = self.adaptor.nil()
                        # 171:44: -> ^( STRING catchall )
                        # FMFpython.g:171:47: ^( STRING catchall )
                        root_1 = self.adaptor.nil()
                        root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(STRING, "STRING"), root_1)

                        self.adaptor.addChild(root_1, stream_catchall.next())

                        self.adaptor.addChild(root_0, root_1)





                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:
            if self.backtracking > 0:
                self.memoize(self.input, 14, value_StartIndex)

            pass

        return retval

    # $ANTLR end value

    class identifier_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start identifier
    # FMFpython.g:174:1: identifier : WORD ;
    def identifier(self, ):

        retval = self.identifier_return()
        retval.start = self.input.LT(1)

        root_0 = None

        WORD61 = None

        WORD61_tree = None

        try:
            try:
                # FMFpython.g:174:11: ( WORD )
                # FMFpython.g:174:13: WORD
                root_0 = self.adaptor.nil()

                WORD61 = self.input.LT(1)
                self.match(self.input, WORD, self.FOLLOW_WORD_in_identifier2016)
                if self.failed:
                    return retval

                WORD61_tree = self.adaptor.createWithPayload(WORD61)
                self.adaptor.addChild(root_0, WORD61_tree)




                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end identifier

    class catchall_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start catchall
    # FMFpython.g:182:1: catchall : (~ NEWLINE )* ;
    def catchall(self, ):

        retval = self.catchall_return()
        retval.start = self.input.LT(1)

        root_0 = None

        set62 = None

        set62_tree = None

        try:
            try:
                # FMFpython.g:183:9: ( (~ NEWLINE )* )
                # FMFpython.g:183:11: (~ NEWLINE )*
                root_0 = self.adaptor.nil()

                # FMFpython.g:183:11: (~ NEWLINE )*
                while True: #loop14
                    alt14 = 2
                    LA14_0 = self.input.LA(1)

                    if ((CONFIG <= LA14_0 <= DEPS) or (WS <= LA14_0 <= 67)) :
                        alt14 = 1


                    if alt14 == 1:
                        # FMFpython.g:183:11: ~ NEWLINE
                        set62 = self.input.LT(1)
                        if (CONFIG <= self.input.LA(1) <= DEPS) or (WS <= self.input.LA(1) <= 67):
                            self.input.consume();
                            if self.backtracking == 0:
                                self.adaptor.addChild(root_0, self.adaptor.createWithPayload(set62))
                            self.errorRecovery = False
                            self.failed = False

                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return retval

                            mse = MismatchedSetException(None, self.input)
                            self.recoverFromMismatchedSet(
                                self.input, mse, self.FOLLOW_set_in_catchall2034
                                )
                            raise mse




                    else:
                        break #loop14





                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end catchall

    class datetime_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start datetime
    # FMFpython.g:185:1: datetime : date ( time )? -> ^( DATETIME ^( DATE date ) ^( TIME ( time )? ) ) ;
    def datetime(self, ):

        retval = self.datetime_return()
        retval.start = self.input.LT(1)

        root_0 = None

        date63 = None

        time64 = None


        stream_time = RewriteRuleSubtreeStream(self.adaptor, "rule time")
        stream_date = RewriteRuleSubtreeStream(self.adaptor, "rule date")
        try:
            try:
                # FMFpython.g:186:9: ( date ( time )? -> ^( DATETIME ^( DATE date ) ^( TIME ( time )? ) ) )
                # FMFpython.g:186:11: date ( time )?
                self.following.append(self.FOLLOW_date_in_datetime2052)
                date63 = self.date()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_date.add(date63.tree)
                # FMFpython.g:186:16: ( time )?
                alt15 = 2
                LA15_0 = self.input.LA(1)

                if (LA15_0 == INT) :
                    alt15 = 1
                if alt15 == 1:
                    # FMFpython.g:186:16: time
                    self.following.append(self.FOLLOW_time_in_datetime2054)
                    time64 = self.time()
                    self.following.pop()
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_time.add(time64.tree)



                # AST Rewrite
                # elements: time, date
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 186:22: -> ^( DATETIME ^( DATE date ) ^( TIME ( time )? ) )
                    # FMFpython.g:186:25: ^( DATETIME ^( DATE date ) ^( TIME ( time )? ) )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(DATETIME, "DATETIME"), root_1)

                    # FMFpython.g:186:36: ^( DATE date )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(DATE, "DATE"), root_2)

                    self.adaptor.addChild(root_2, stream_date.next())

                    self.adaptor.addChild(root_1, root_2)
                    # FMFpython.g:186:49: ^( TIME ( time )? )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(TIME, "TIME"), root_2)

                    # FMFpython.g:186:56: ( time )?
                    if stream_time.hasNext():
                        self.adaptor.addChild(root_2, stream_time.next())


                    stream_time.reset();

                    self.adaptor.addChild(root_1, root_2)

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end datetime

    class date_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start date
    # FMFpython.g:188:1: date : ( GERMANDATE | ISODATE );
    def date(self, ):

        retval = self.date_return()
        retval.start = self.input.LT(1)

        root_0 = None

        set65 = None

        set65_tree = None

        try:
            try:
                # FMFpython.g:188:9: ( GERMANDATE | ISODATE )
                # FMFpython.g:
                root_0 = self.adaptor.nil()

                set65 = self.input.LT(1)
                if (GERMANDATE <= self.input.LA(1) <= ISODATE):
                    self.input.consume();
                    if self.backtracking == 0:
                        self.adaptor.addChild(root_0, self.adaptor.createWithPayload(set65))
                    self.errorRecovery = False
                    self.failed = False

                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return retval

                    mse = MismatchedSetException(None, self.input)
                    self.recoverFromMismatchedSet(
                        self.input, mse, self.FOLLOW_set_in_date0
                        )
                    raise mse





                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end date

    class time_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start time
    # FMFpython.g:190:1: time : INT COLON INT ( COLON FLOAT )? ;
    def time(self, ):

        retval = self.time_return()
        retval.start = self.input.LT(1)

        root_0 = None

        INT66 = None
        COLON67 = None
        INT68 = None
        COLON69 = None
        FLOAT70 = None

        INT66_tree = None
        COLON67_tree = None
        INT68_tree = None
        COLON69_tree = None
        FLOAT70_tree = None

        try:
            try:
                # FMFpython.g:190:9: ( INT COLON INT ( COLON FLOAT )? )
                # FMFpython.g:190:11: INT COLON INT ( COLON FLOAT )?
                root_0 = self.adaptor.nil()

                INT66 = self.input.LT(1)
                self.match(self.input, INT, self.FOLLOW_INT_in_time2100)
                if self.failed:
                    return retval

                INT66_tree = self.adaptor.createWithPayload(INT66)
                self.adaptor.addChild(root_0, INT66_tree)

                COLON67 = self.input.LT(1)
                self.match(self.input, COLON, self.FOLLOW_COLON_in_time2102)
                if self.failed:
                    return retval

                COLON67_tree = self.adaptor.createWithPayload(COLON67)
                self.adaptor.addChild(root_0, COLON67_tree)

                INT68 = self.input.LT(1)
                self.match(self.input, INT, self.FOLLOW_INT_in_time2104)
                if self.failed:
                    return retval

                INT68_tree = self.adaptor.createWithPayload(INT68)
                self.adaptor.addChild(root_0, INT68_tree)

                # FMFpython.g:190:25: ( COLON FLOAT )?
                alt16 = 2
                LA16_0 = self.input.LA(1)

                if (LA16_0 == COLON) :
                    alt16 = 1
                if alt16 == 1:
                    # FMFpython.g:190:26: COLON FLOAT
                    COLON69 = self.input.LT(1)
                    self.match(self.input, COLON, self.FOLLOW_COLON_in_time2107)
                    if self.failed:
                        return retval

                    COLON69_tree = self.adaptor.createWithPayload(COLON69)
                    self.adaptor.addChild(root_0, COLON69_tree)

                    FLOAT70 = self.input.LT(1)
                    self.match(self.input, FLOAT, self.FOLLOW_FLOAT_in_time2109)
                    if self.failed:
                        return retval

                    FLOAT70_tree = self.adaptor.createWithPayload(FLOAT70)
                    self.adaptor.addChild(root_0, FLOAT70_tree)







                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end time

    class number_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start number
    # FMFpython.g:192:1: number : ( NPLUS | NMINUS )? absnumber ;
    def number(self, ):

        retval = self.number_return()
        retval.start = self.input.LT(1)

        root_0 = None

        set71 = None
        absnumber72 = None


        set71_tree = None

        try:
            try:
                # FMFpython.g:192:9: ( ( NPLUS | NMINUS )? absnumber )
                # FMFpython.g:192:11: ( NPLUS | NMINUS )? absnumber
                root_0 = self.adaptor.nil()

                # FMFpython.g:192:11: ( NPLUS | NMINUS )?
                alt17 = 2
                LA17_0 = self.input.LA(1)

                if (LA17_0 == NPLUS or LA17_0 == NMINUS) :
                    alt17 = 1
                if alt17 == 1:
                    # FMFpython.g:
                    set71 = self.input.LT(1)
                    if self.input.LA(1) == NPLUS or self.input.LA(1) == NMINUS:
                        self.input.consume();
                        if self.backtracking == 0:
                            self.adaptor.addChild(root_0, self.adaptor.createWithPayload(set71))
                        self.errorRecovery = False
                        self.failed = False

                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        mse = MismatchedSetException(None, self.input)
                        self.recoverFromMismatchedSet(
                            self.input, mse, self.FOLLOW_set_in_number2120
                            )
                        raise mse





                self.following.append(self.FOLLOW_absnumber_in_number2127)
                absnumber72 = self.absnumber()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    self.adaptor.addChild(root_0, absnumber72.tree)



                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end number

    class absnumber_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start absnumber
    # FMFpython.g:194:1: fragment absnumber options {backtrack=true; } : ( FLOAT ( NPLUS | NMINUS ) IMAG | INT ( NPLUS | NMINUS ) IMAG | FLOAT | INT | IMAG );
    def absnumber(self, ):

        retval = self.absnumber_return()
        retval.start = self.input.LT(1)

        root_0 = None

        FLOAT73 = None
        set74 = None
        IMAG75 = None
        INT76 = None
        set77 = None
        IMAG78 = None
        FLOAT79 = None
        INT80 = None
        IMAG81 = None

        FLOAT73_tree = None
        set74_tree = None
        IMAG75_tree = None
        INT76_tree = None
        set77_tree = None
        IMAG78_tree = None
        FLOAT79_tree = None
        INT80_tree = None
        IMAG81_tree = None

        try:
            try:
                # FMFpython.g:199:9: ( FLOAT ( NPLUS | NMINUS ) IMAG | INT ( NPLUS | NMINUS ) IMAG | FLOAT | INT | IMAG )
                alt18 = 5
                LA18 = self.input.LA(1)
                if LA18 == FLOAT:
                    LA18_1 = self.input.LA(2)

                    if (LA18_1 == NPLUS or LA18_1 == NMINUS) :
                        LA18_4 = self.input.LA(3)

                        if (LA18_4 == IMAG) :
                            LA18_8 = self.input.LA(4)

                            if (self.synpred4()) :
                                alt18 = 1
                            elif (self.synpred6()) :
                                alt18 = 3
                            else:
                                if self.backtracking > 0:
                                    self.failed = True
                                    return retval

                                nvae = NoViableAltException("194:1: fragment absnumber options {backtrack=true; } : ( FLOAT ( NPLUS | NMINUS ) IMAG | INT ( NPLUS | NMINUS ) IMAG | FLOAT | INT | IMAG );", 18, 8, self.input)

                                raise nvae

                        elif ((FLOAT <= LA18_4 <= INT)) :
                            alt18 = 3
                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return retval

                            nvae = NoViableAltException("194:1: fragment absnumber options {backtrack=true; } : ( FLOAT ( NPLUS | NMINUS ) IMAG | INT ( NPLUS | NMINUS ) IMAG | FLOAT | INT | IMAG );", 18, 4, self.input)

                            raise nvae

                    elif (LA18_1 == EOF or LA18_1 == NEWLINE or (FLOAT <= LA18_1 <= IMAG) or LA18_1 == WORD or LA18_1 == LITERAL) :
                        alt18 = 3
                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        nvae = NoViableAltException("194:1: fragment absnumber options {backtrack=true; } : ( FLOAT ( NPLUS | NMINUS ) IMAG | INT ( NPLUS | NMINUS ) IMAG | FLOAT | INT | IMAG );", 18, 1, self.input)

                        raise nvae

                elif LA18 == INT:
                    LA18_2 = self.input.LA(2)

                    if (LA18_2 == NPLUS or LA18_2 == NMINUS) :
                        LA18_6 = self.input.LA(3)

                        if (LA18_6 == IMAG) :
                            LA18_9 = self.input.LA(4)

                            if (self.synpred5()) :
                                alt18 = 2
                            elif (self.synpred7()) :
                                alt18 = 4
                            else:
                                if self.backtracking > 0:
                                    self.failed = True
                                    return retval

                                nvae = NoViableAltException("194:1: fragment absnumber options {backtrack=true; } : ( FLOAT ( NPLUS | NMINUS ) IMAG | INT ( NPLUS | NMINUS ) IMAG | FLOAT | INT | IMAG );", 18, 9, self.input)

                                raise nvae

                        elif ((FLOAT <= LA18_6 <= INT)) :
                            alt18 = 4
                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return retval

                            nvae = NoViableAltException("194:1: fragment absnumber options {backtrack=true; } : ( FLOAT ( NPLUS | NMINUS ) IMAG | INT ( NPLUS | NMINUS ) IMAG | FLOAT | INT | IMAG );", 18, 6, self.input)

                            raise nvae

                    elif (LA18_2 == EOF or LA18_2 == NEWLINE or (FLOAT <= LA18_2 <= IMAG) or LA18_2 == WORD or LA18_2 == LITERAL) :
                        alt18 = 4
                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        nvae = NoViableAltException("194:1: fragment absnumber options {backtrack=true; } : ( FLOAT ( NPLUS | NMINUS ) IMAG | INT ( NPLUS | NMINUS ) IMAG | FLOAT | INT | IMAG );", 18, 2, self.input)

                        raise nvae

                elif LA18 == IMAG:
                    alt18 = 5
                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return retval

                    nvae = NoViableAltException("194:1: fragment absnumber options {backtrack=true; } : ( FLOAT ( NPLUS | NMINUS ) IMAG | INT ( NPLUS | NMINUS ) IMAG | FLOAT | INT | IMAG );", 18, 0, self.input)

                    raise nvae

                if alt18 == 1:
                    # FMFpython.g:199:11: FLOAT ( NPLUS | NMINUS ) IMAG
                    root_0 = self.adaptor.nil()

                    FLOAT73 = self.input.LT(1)
                    self.match(self.input, FLOAT, self.FOLLOW_FLOAT_in_absnumber2158)
                    if self.failed:
                        return retval

                    FLOAT73_tree = self.adaptor.createWithPayload(FLOAT73)
                    self.adaptor.addChild(root_0, FLOAT73_tree)

                    set74 = self.input.LT(1)
                    if self.input.LA(1) == NPLUS or self.input.LA(1) == NMINUS:
                        self.input.consume();
                        if self.backtracking == 0:
                            self.adaptor.addChild(root_0, self.adaptor.createWithPayload(set74))
                        self.errorRecovery = False
                        self.failed = False

                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        mse = MismatchedSetException(None, self.input)
                        self.recoverFromMismatchedSet(
                            self.input, mse, self.FOLLOW_set_in_absnumber2160
                            )
                        raise mse


                    IMAG75 = self.input.LT(1)
                    self.match(self.input, IMAG, self.FOLLOW_IMAG_in_absnumber2166)
                    if self.failed:
                        return retval

                    IMAG75_tree = self.adaptor.createWithPayload(IMAG75)
                    self.adaptor.addChild(root_0, IMAG75_tree)



                elif alt18 == 2:
                    # FMFpython.g:200:11: INT ( NPLUS | NMINUS ) IMAG
                    root_0 = self.adaptor.nil()

                    INT76 = self.input.LT(1)
                    self.match(self.input, INT, self.FOLLOW_INT_in_absnumber2178)
                    if self.failed:
                        return retval

                    INT76_tree = self.adaptor.createWithPayload(INT76)
                    self.adaptor.addChild(root_0, INT76_tree)

                    set77 = self.input.LT(1)
                    if self.input.LA(1) == NPLUS or self.input.LA(1) == NMINUS:
                        self.input.consume();
                        if self.backtracking == 0:
                            self.adaptor.addChild(root_0, self.adaptor.createWithPayload(set77))
                        self.errorRecovery = False
                        self.failed = False

                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return retval

                        mse = MismatchedSetException(None, self.input)
                        self.recoverFromMismatchedSet(
                            self.input, mse, self.FOLLOW_set_in_absnumber2180
                            )
                        raise mse


                    IMAG78 = self.input.LT(1)
                    self.match(self.input, IMAG, self.FOLLOW_IMAG_in_absnumber2186)
                    if self.failed:
                        return retval

                    IMAG78_tree = self.adaptor.createWithPayload(IMAG78)
                    self.adaptor.addChild(root_0, IMAG78_tree)



                elif alt18 == 3:
                    # FMFpython.g:201:11: FLOAT
                    root_0 = self.adaptor.nil()

                    FLOAT79 = self.input.LT(1)
                    self.match(self.input, FLOAT, self.FOLLOW_FLOAT_in_absnumber2198)
                    if self.failed:
                        return retval

                    FLOAT79_tree = self.adaptor.createWithPayload(FLOAT79)
                    self.adaptor.addChild(root_0, FLOAT79_tree)



                elif alt18 == 4:
                    # FMFpython.g:202:11: INT
                    root_0 = self.adaptor.nil()

                    INT80 = self.input.LT(1)
                    self.match(self.input, INT, self.FOLLOW_INT_in_absnumber2210)
                    if self.failed:
                        return retval

                    INT80_tree = self.adaptor.createWithPayload(INT80)
                    self.adaptor.addChild(root_0, INT80_tree)



                elif alt18 == 5:
                    # FMFpython.g:203:11: IMAG
                    root_0 = self.adaptor.nil()

                    IMAG81 = self.input.LT(1)
                    self.match(self.input, IMAG, self.FOLLOW_IMAG_in_absnumber2222)
                    if self.failed:
                        return retval

                    IMAG81_tree = self.adaptor.createWithPayload(IMAG81)
                    self.adaptor.addChild(root_0, IMAG81_tree)



                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end absnumber

    class quantity_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start quantity
    # FMFpython.g:206:1: quantity : number ( unit )? -> ^( QUANTITY ^( NUMBER number ) ^( UNIT ( unit )? ) ) ;
    def quantity(self, ):

        retval = self.quantity_return()
        retval.start = self.input.LT(1)

        root_0 = None

        number82 = None

        unit83 = None


        stream_unit = RewriteRuleSubtreeStream(self.adaptor, "rule unit")
        stream_number = RewriteRuleSubtreeStream(self.adaptor, "rule number")
        try:
            try:
                # FMFpython.g:207:9: ( number ( unit )? -> ^( QUANTITY ^( NUMBER number ) ^( UNIT ( unit )? ) ) )
                # FMFpython.g:207:11: number ( unit )?
                self.following.append(self.FOLLOW_number_in_quantity2247)
                number82 = self.number()
                self.following.pop()
                if self.failed:
                    return retval
                if self.backtracking == 0:
                    stream_number.add(number82.tree)
                # FMFpython.g:207:18: ( unit )?
                alt19 = 2
                LA19_0 = self.input.LA(1)

                if (LA19_0 == WORD) :
                    alt19 = 1
                if alt19 == 1:
                    # FMFpython.g:207:18: unit
                    self.following.append(self.FOLLOW_unit_in_quantity2249)
                    unit83 = self.unit()
                    self.following.pop()
                    if self.failed:
                        return retval
                    if self.backtracking == 0:
                        stream_unit.add(unit83.tree)



                # AST Rewrite
                # elements: number, unit
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                if self.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self.adaptor, "token retval", None)


                    root_0 = self.adaptor.nil()
                    # 207:24: -> ^( QUANTITY ^( NUMBER number ) ^( UNIT ( unit )? ) )
                    # FMFpython.g:207:27: ^( QUANTITY ^( NUMBER number ) ^( UNIT ( unit )? ) )
                    root_1 = self.adaptor.nil()
                    root_1 = self.adaptor.becomeRoot(self.adaptor.createFromType(QUANTITY, "QUANTITY"), root_1)

                    # FMFpython.g:207:38: ^( NUMBER number )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(NUMBER, "NUMBER"), root_2)

                    self.adaptor.addChild(root_2, stream_number.next())

                    self.adaptor.addChild(root_1, root_2)
                    # FMFpython.g:207:55: ^( UNIT ( unit )? )
                    root_2 = self.adaptor.nil()
                    root_2 = self.adaptor.becomeRoot(self.adaptor.createFromType(UNIT, "UNIT"), root_2)

                    # FMFpython.g:207:62: ( unit )?
                    if stream_unit.hasNext():
                        self.adaptor.addChild(root_2, stream_unit.next())


                    stream_unit.reset();

                    self.adaptor.addChild(root_1, root_2)

                    self.adaptor.addChild(root_0, root_1)






                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end quantity

    class unit_return(object):
        def __init__(self):
            self.start = None
            self.stop = None

            self.tree = None


    # $ANTLR start unit
    # FMFpython.g:209:1: unit : WORD ( ( ASTERISK | DIV ) WORD )* ;
    def unit(self, ):

        retval = self.unit_return()
        retval.start = self.input.LT(1)

        root_0 = None

        WORD84 = None
        set85 = None
        WORD86 = None

        WORD84_tree = None
        set85_tree = None
        WORD86_tree = None

        try:
            try:
                # FMFpython.g:209:9: ( WORD ( ( ASTERISK | DIV ) WORD )* )
                # FMFpython.g:209:11: WORD ( ( ASTERISK | DIV ) WORD )*
                root_0 = self.adaptor.nil()

                WORD84 = self.input.LT(1)
                self.match(self.input, WORD, self.FOLLOW_WORD_in_unit2280)
                if self.failed:
                    return retval

                WORD84_tree = self.adaptor.createWithPayload(WORD84)
                self.adaptor.addChild(root_0, WORD84_tree)

                # FMFpython.g:209:16: ( ( ASTERISK | DIV ) WORD )*
                while True: #loop20
                    alt20 = 2
                    LA20_0 = self.input.LA(1)

                    if (LA20_0 == ASTERISK or LA20_0 == DIV) :
                        alt20 = 1


                    if alt20 == 1:
                        # FMFpython.g:209:17: ( ASTERISK | DIV ) WORD
                        set85 = self.input.LT(1)
                        if self.input.LA(1) == ASTERISK or self.input.LA(1) == DIV:
                            self.input.consume();
                            if self.backtracking == 0:
                                self.adaptor.addChild(root_0, self.adaptor.createWithPayload(set85))
                            self.errorRecovery = False
                            self.failed = False

                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return retval

                            mse = MismatchedSetException(None, self.input)
                            self.recoverFromMismatchedSet(
                                self.input, mse, self.FOLLOW_set_in_unit2283
                                )
                            raise mse


                        WORD86 = self.input.LT(1)
                        self.match(self.input, WORD, self.FOLLOW_WORD_in_unit2289)
                        if self.failed:
                            return retval

                        WORD86_tree = self.adaptor.createWithPayload(WORD86)
                        self.adaptor.addChild(root_0, WORD86_tree)



                    else:
                        break #loop20





                retval.stop = self.input.LT(-1)

                if self.backtracking == 0:

                    retval.tree = self.adaptor.rulePostProcessing(root_0)
                    self.adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)

            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass

        return retval

    # $ANTLR end unit

    # $ANTLR start synpred1
    def synpred1_fragment(self, ):
        # FMFpython.g:168:17: ( number )
        # FMFpython.g:168:17: number
        self.following.append(self.FOLLOW_number_in_synpred11852)
        self.number()
        self.following.pop()
        if self.failed:
            return 


    # $ANTLR end synpred1



    # $ANTLR start synpred2
    def synpred2_fragment(self, ):
        # FMFpython.g:169:17: ( identifier EQUALS quantity )
        # FMFpython.g:169:17: identifier EQUALS quantity
        self.following.append(self.FOLLOW_identifier_in_synpred21898)
        self.identifier()
        self.following.pop()
        if self.failed:
            return 
        self.match(self.input, EQUALS, self.FOLLOW_EQUALS_in_synpred21900)
        if self.failed:
            return 
        self.following.append(self.FOLLOW_quantity_in_synpred21902)
        self.quantity()
        self.following.pop()
        if self.failed:
            return 


    # $ANTLR end synpred2



    # $ANTLR start synpred3
    def synpred3_fragment(self, ):
        # FMFpython.g:170:17: ( datetime )
        # FMFpython.g:170:17: datetime
        self.following.append(self.FOLLOW_datetime_in_synpred31934)
        self.datetime()
        self.following.pop()
        if self.failed:
            return 


    # $ANTLR end synpred3



    # $ANTLR start synpred4
    def synpred4_fragment(self, ):
        # FMFpython.g:199:11: ( FLOAT ( NPLUS | NMINUS ) IMAG )
        # FMFpython.g:199:11: FLOAT ( NPLUS | NMINUS ) IMAG
        self.match(self.input, FLOAT, self.FOLLOW_FLOAT_in_synpred42158)
        if self.failed:
            return 
        if self.input.LA(1) == NPLUS or self.input.LA(1) == NMINUS:
            self.input.consume();
            self.errorRecovery = False
            self.failed = False

        else:
            if self.backtracking > 0:
                self.failed = True
                return 

            mse = MismatchedSetException(None, self.input)
            self.recoverFromMismatchedSet(
                self.input, mse, self.FOLLOW_set_in_synpred42160
                )
            raise mse


        self.match(self.input, IMAG, self.FOLLOW_IMAG_in_synpred42166)
        if self.failed:
            return 


    # $ANTLR end synpred4



    # $ANTLR start synpred5
    def synpred5_fragment(self, ):
        # FMFpython.g:200:11: ( INT ( NPLUS | NMINUS ) IMAG )
        # FMFpython.g:200:11: INT ( NPLUS | NMINUS ) IMAG
        self.match(self.input, INT, self.FOLLOW_INT_in_synpred52178)
        if self.failed:
            return 
        if self.input.LA(1) == NPLUS or self.input.LA(1) == NMINUS:
            self.input.consume();
            self.errorRecovery = False
            self.failed = False

        else:
            if self.backtracking > 0:
                self.failed = True
                return 

            mse = MismatchedSetException(None, self.input)
            self.recoverFromMismatchedSet(
                self.input, mse, self.FOLLOW_set_in_synpred52180
                )
            raise mse


        self.match(self.input, IMAG, self.FOLLOW_IMAG_in_synpred52186)
        if self.failed:
            return 


    # $ANTLR end synpred5



    # $ANTLR start synpred6
    def synpred6_fragment(self, ):
        # FMFpython.g:201:11: ( FLOAT )
        # FMFpython.g:201:11: FLOAT
        self.match(self.input, FLOAT, self.FOLLOW_FLOAT_in_synpred62198)
        if self.failed:
            return 


    # $ANTLR end synpred6



    # $ANTLR start synpred7
    def synpred7_fragment(self, ):
        # FMFpython.g:202:11: ( INT )
        # FMFpython.g:202:11: INT
        self.match(self.input, INT, self.FOLLOW_INT_in_synpred72210)
        if self.failed:
            return 


    # $ANTLR end synpred7



    def synpred4(self):
        self.backtracking += 1
        start = self.input.mark()
        self.synpred4_fragment()
        success = not self.failed
        self.input.rewind(start)
        self.backtracking -= 1
        self.failed = False
        return success

    def synpred7(self):
        self.backtracking += 1
        start = self.input.mark()
        self.synpred7_fragment()
        success = not self.failed
        self.input.rewind(start)
        self.backtracking -= 1
        self.failed = False
        return success

    def synpred2(self):
        self.backtracking += 1
        start = self.input.mark()
        self.synpred2_fragment()
        success = not self.failed
        self.input.rewind(start)
        self.backtracking -= 1
        self.failed = False
        return success

    def synpred3(self):
        self.backtracking += 1
        start = self.input.mark()
        self.synpred3_fragment()
        success = not self.failed
        self.input.rewind(start)
        self.backtracking -= 1
        self.failed = False
        return success

    def synpred1(self):
        self.backtracking += 1
        start = self.input.mark()
        self.synpred1_fragment()
        success = not self.failed
        self.input.rewind(start)
        self.backtracking -= 1
        self.failed = False
        return success

    def synpred5(self):
        self.backtracking += 1
        start = self.input.mark()
        self.synpred5_fragment()
        success = not self.failed
        self.input.rewind(start)
        self.backtracking -= 1
        self.failed = False
        return success

    def synpred6(self):
        self.backtracking += 1
        start = self.input.mark()
        self.synpred6_fragment()
        success = not self.failed
        self.input.rewind(start)
        self.backtracking -= 1
        self.failed = False
        return success



 

    FOLLOW_referenceSection_in_config1261 = frozenset([28])
    FOLLOW_commonSection_in_config1263 = frozenset([28])
    FOLLOW_datadefSection_in_config1266 = frozenset([28])
    FOLLOW_dataSection_in_config1268 = frozenset([1])
    FOLLOW_LBRACK_in_referenceSection1316 = frozenset([32])
    FOLLOW_ASTERISK_in_referenceSection1318 = frozenset([64])
    FOLLOW_64_in_referenceSection1320 = frozenset([29])
    FOLLOW_RBRACK_in_referenceSection1322 = frozenset([25])
    FOLLOW_NEWLINE_in_referenceSection1324 = frozenset([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_commonitem_in_referenceSection1326 = frozenset([1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_LBRACK_in_datadefSection1372 = frozenset([32])
    FOLLOW_ASTERISK_in_datadefSection1374 = frozenset([65])
    FOLLOW_65_in_datadefSection1376 = frozenset([29])
    FOLLOW_RBRACK_in_datadefSection1378 = frozenset([25])
    FOLLOW_NEWLINE_in_datadefSection1380 = frozenset([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_colitem_in_datadefSection1382 = frozenset([1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_LBRACK_in_dataSection1428 = frozenset([32])
    FOLLOW_ASTERISK_in_dataSection1430 = frozenset([66])
    FOLLOW_66_in_dataSection1432 = frozenset([29])
    FOLLOW_RBRACK_in_dataSection1434 = frozenset([25])
    FOLLOW_NEWLINE_in_dataSection1436 = frozenset([1, 36, 39, 57, 58, 59, 61, 63])
    FOLLOW_dataitem_in_dataSection1438 = frozenset([1, 36, 39, 57, 58, 59, 61, 63])
    FOLLOW_LBRACK_in_commonSection1484 = frozenset([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_headername_in_commonSection1486 = frozenset([29])
    FOLLOW_RBRACK_in_commonSection1488 = frozenset([25])
    FOLLOW_NEWLINE_in_commonSection1490 = frozenset([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_commonitem_in_commonSection1492 = frozenset([1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_set_in_headername1536 = frozenset([1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_key_in_colitem1548 = frozenset([33])
    FOLLOW_COLON_in_colitem1550 = frozenset([61])
    FOLLOW_colspec_in_colitem1552 = frozenset([25])
    FOLLOW_NEWLINE_in_colitem1554 = frozenset([1])
    FOLLOW_cell_in_dataitem1583 = frozenset([25, 36, 39, 57, 58, 59, 61, 63])
    FOLLOW_NEWLINE_in_dataitem1586 = frozenset([1])
    FOLLOW_key_in_commonitem1610 = frozenset([33])
    FOLLOW_COLON_in_commonitem1612 = frozenset([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_value_in_commonitem1614 = frozenset([25])
    FOLLOW_NEWLINE_in_commonitem1616 = frozenset([1])
    FOLLOW_number_in_cell1649 = frozenset([1])
    FOLLOW_WORD_in_cell1676 = frozenset([1])
    FOLLOW_LITERAL_in_cell1705 = frozenset([1])
    FOLLOW_identifier_in_colspec1730 = frozenset([1, 28, 30])
    FOLLOW_deps_in_colspec1732 = frozenset([1, 28])
    FOLLOW_LBRACK_in_colspec1736 = frozenset([61])
    FOLLOW_unit_in_colspec1738 = frozenset([29])
    FOLLOW_RBRACK_in_colspec1740 = frozenset([1])
    FOLLOW_LPAREN_in_deps1775 = frozenset([61])
    FOLLOW_identifier_in_deps1777 = frozenset([31, 67])
    FOLLOW_67_in_deps1781 = frozenset([61])
    FOLLOW_identifier_in_deps1783 = frozenset([31, 67])
    FOLLOW_RPAREN_in_deps1787 = frozenset([1])
    FOLLOW_set_in_key1804 = frozenset([1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_number_in_value1852 = frozenset([1])
    FOLLOW_identifier_in_value1898 = frozenset([34])
    FOLLOW_EQUALS_in_value1900 = frozenset([36, 39, 57, 58, 59])
    FOLLOW_quantity_in_value1902 = frozenset([1])
    FOLLOW_datetime_in_value1934 = frozenset([1])
    FOLLOW_catchall_in_value1974 = frozenset([1])
    FOLLOW_WORD_in_identifier2016 = frozenset([1])
    FOLLOW_set_in_catchall2034 = frozenset([1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67])
    FOLLOW_date_in_datetime2052 = frozenset([1, 58])
    FOLLOW_time_in_datetime2054 = frozenset([1])
    FOLLOW_set_in_date0 = frozenset([1])
    FOLLOW_INT_in_time2100 = frozenset([33])
    FOLLOW_COLON_in_time2102 = frozenset([58])
    FOLLOW_INT_in_time2104 = frozenset([1, 33])
    FOLLOW_COLON_in_time2107 = frozenset([57])
    FOLLOW_FLOAT_in_time2109 = frozenset([1])
    FOLLOW_set_in_number2120 = frozenset([57, 58, 59])
    FOLLOW_absnumber_in_number2127 = frozenset([1])
    FOLLOW_FLOAT_in_absnumber2158 = frozenset([36, 39])
    FOLLOW_set_in_absnumber2160 = frozenset([59])
    FOLLOW_IMAG_in_absnumber2166 = frozenset([1])
    FOLLOW_INT_in_absnumber2178 = frozenset([36, 39])
    FOLLOW_set_in_absnumber2180 = frozenset([59])
    FOLLOW_IMAG_in_absnumber2186 = frozenset([1])
    FOLLOW_FLOAT_in_absnumber2198 = frozenset([1])
    FOLLOW_INT_in_absnumber2210 = frozenset([1])
    FOLLOW_IMAG_in_absnumber2222 = frozenset([1])
    FOLLOW_number_in_quantity2247 = frozenset([1, 61])
    FOLLOW_unit_in_quantity2249 = frozenset([1])
    FOLLOW_WORD_in_unit2280 = frozenset([1, 32, 44])
    FOLLOW_set_in_unit2283 = frozenset([61])
    FOLLOW_WORD_in_unit2289 = frozenset([1, 32, 44])
    FOLLOW_number_in_synpred11852 = frozenset([1])
    FOLLOW_identifier_in_synpred21898 = frozenset([34])
    FOLLOW_EQUALS_in_synpred21900 = frozenset([36, 39, 57, 58, 59])
    FOLLOW_quantity_in_synpred21902 = frozenset([1])
    FOLLOW_datetime_in_synpred31934 = frozenset([1])
    FOLLOW_FLOAT_in_synpred42158 = frozenset([36, 39])
    FOLLOW_set_in_synpred42160 = frozenset([59])
    FOLLOW_IMAG_in_synpred42166 = frozenset([1])
    FOLLOW_INT_in_synpred52178 = frozenset([36, 39])
    FOLLOW_set_in_synpred52180 = frozenset([59])
    FOLLOW_IMAG_in_synpred52186 = frozenset([1])
    FOLLOW_FLOAT_in_synpred62198 = frozenset([1])
    FOLLOW_INT_in_synpred72210 = frozenset([1])

