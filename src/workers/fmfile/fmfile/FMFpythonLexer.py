# $ANTLR 3.0.1 FMFpython.g 2008-04-03 08:14:07

from antlr3 import *
from antlr3.compat import set, frozenset


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
T64=64
RPAREN=31
T65=65
T66=66
T67=67
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
Tokens=68
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

class FMFpythonLexer(Lexer):

    grammarFileName = "FMFpython.g"

    def __init__(self, input=None):
        Lexer.__init__(self, input)
        self.ruleMemo = {}
        self.dfa9 = self.DFA9(
            self, 9,
            eot = self.DFA9_eot,
            eof = self.DFA9_eof,
            min = self.DFA9_min,
            max = self.DFA9_max,
            accept = self.DFA9_accept,
            special = self.DFA9_special,
            transition = self.DFA9_transition
            )
        self.dfa18 = self.DFA18(
            self, 18,
            eot = self.DFA18_eot,
            eof = self.DFA18_eof,
            min = self.DFA18_min,
            max = self.DFA18_max,
            accept = self.DFA18_accept,
            special = self.DFA18_special,
            transition = self.DFA18_transition
            )
        self.dfa24 = self.DFA24(
            self, 24,
            eot = self.DFA24_eot,
            eof = self.DFA24_eof,
            min = self.DFA24_min,
            max = self.DFA24_max,
            accept = self.DFA24_accept,
            special = self.DFA24_special,
            transition = self.DFA24_transition
            )






    # $ANTLR start T64
    def mT64(self, ):

        try:
            self.type = T64

            # FMFpython.g:7:5: ( 'reference' )
            # FMFpython.g:7:7: 'reference'
            self.match("reference")
            if self.failed:
                return 





        finally:

            pass

    # $ANTLR end T64



    # $ANTLR start T65
    def mT65(self, ):

        try:
            self.type = T65

            # FMFpython.g:8:5: ( 'data definitions' )
            # FMFpython.g:8:7: 'data definitions'
            self.match("data definitions")
            if self.failed:
                return 





        finally:

            pass

    # $ANTLR end T65



    # $ANTLR start T66
    def mT66(self, ):

        try:
            self.type = T66

            # FMFpython.g:9:5: ( 'data' )
            # FMFpython.g:9:7: 'data'
            self.match("data")
            if self.failed:
                return 





        finally:

            pass

    # $ANTLR end T66



    # $ANTLR start T67
    def mT67(self, ):

        try:
            self.type = T67

            # FMFpython.g:10:5: ( ',' )
            # FMFpython.g:10:7: ','
            self.match(u',')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end T67



    # $ANTLR start NEWLINE
    def mNEWLINE(self, ):

        try:
            self.type = NEWLINE

            # FMFpython.g:32:9: ( ( ( '\\r' )? '\\n' )+ )
            # FMFpython.g:32:17: ( ( '\\r' )? '\\n' )+
            # FMFpython.g:32:17: ( ( '\\r' )? '\\n' )+
            cnt2 = 0
            while True: #loop2
                alt2 = 2
                LA2_0 = self.input.LA(1)

                if (LA2_0 == u'\n' or LA2_0 == u'\r') :
                    alt2 = 1


                if alt2 == 1:
                    # FMFpython.g:32:18: ( '\\r' )? '\\n'
                    # FMFpython.g:32:18: ( '\\r' )?
                    alt1 = 2
                    LA1_0 = self.input.LA(1)

                    if (LA1_0 == u'\r') :
                        alt1 = 1
                    if alt1 == 1:
                        # FMFpython.g:32:18: '\\r'
                        self.match(u'\r')
                        if self.failed:
                            return 



                    self.match(u'\n')
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






        finally:

            pass

    # $ANTLR end NEWLINE



    # $ANTLR start WS
    def mWS(self, ):

        try:
            self.type = WS

            # FMFpython.g:33:9: ( ( ' ' | '\\t' )+ )
            # FMFpython.g:33:17: ( ' ' | '\\t' )+
            # FMFpython.g:33:17: ( ' ' | '\\t' )+
            cnt3 = 0
            while True: #loop3
                alt3 = 2
                LA3_0 = self.input.LA(1)

                if (LA3_0 == u'\t' or LA3_0 == u' ') :
                    alt3 = 1


                if alt3 == 1:
                    # FMFpython.g:
                    if self.input.LA(1) == u'\t' or self.input.LA(1) == u' ':
                        self.input.consume();
                        self.failed = False

                    else:
                        if self.backtracking > 0:
                            self.failed = True
                            return 

                        mse = MismatchedSetException(None, self.input)
                        self.recover(mse)
                        raise mse




                else:
                    if cnt3 >= 1:
                        break #loop3

                    if self.backtracking > 0:
                        self.failed = True
                        return 

                    eee = EarlyExitException(3, self.input)
                    raise eee

                cnt3 += 1


            if self.backtracking == 0:
                self.channel=HIDDEN;





        finally:

            pass

    # $ANTLR end WS



    # $ANTLR start COMMENT
    def mCOMMENT(self, ):

        try:
            self.type = COMMENT

            # FMFpython.g:34:9: ( ( ';' | '#' ) ( . )* NEWLINE )
            # FMFpython.g:34:17: ( ';' | '#' ) ( . )* NEWLINE
            if self.input.LA(1) == u'#' or self.input.LA(1) == u';':
                self.input.consume();
                self.failed = False

            else:
                if self.backtracking > 0:
                    self.failed = True
                    return 

                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse


            # FMFpython.g:34:29: ( . )*
            while True: #loop4
                alt4 = 2
                LA4_0 = self.input.LA(1)

                if (LA4_0 == u'\r') :
                    alt4 = 2
                elif (LA4_0 == u'\n') :
                    alt4 = 2
                elif ((u'\u0000' <= LA4_0 <= u'\t') or (u'\u000B' <= LA4_0 <= u'\f') or (u'\u000E' <= LA4_0 <= u'\uFFFE')) :
                    alt4 = 1


                if alt4 == 1:
                    # FMFpython.g:34:29: .
                    self.matchAny()
                    if self.failed:
                        return 


                else:
                    break #loop4


            self.mNEWLINE()
            if self.failed:
                return 
            if self.backtracking == 0:
                self.channel=HIDDEN;





        finally:

            pass

    # $ANTLR end COMMENT



    # $ANTLR start LBRACK
    def mLBRACK(self, ):

        try:
            self.type = LBRACK

            # FMFpython.g:36:9: ( '[' )
            # FMFpython.g:36:17: '['
            self.match(u'[')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end LBRACK



    # $ANTLR start RBRACK
    def mRBRACK(self, ):

        try:
            self.type = RBRACK

            # FMFpython.g:37:9: ( ']' )
            # FMFpython.g:37:17: ']'
            self.match(u']')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end RBRACK



    # $ANTLR start LPAREN
    def mLPAREN(self, ):

        try:
            self.type = LPAREN

            # FMFpython.g:38:9: ( '(' )
            # FMFpython.g:38:17: '('
            self.match(u'(')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end LPAREN



    # $ANTLR start RPAREN
    def mRPAREN(self, ):

        try:
            self.type = RPAREN

            # FMFpython.g:39:9: ( ')' )
            # FMFpython.g:39:17: ')'
            self.match(u')')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end RPAREN



    # $ANTLR start ASTERISK
    def mASTERISK(self, ):

        try:
            self.type = ASTERISK

            # FMFpython.g:40:9: ( '*' )
            # FMFpython.g:40:17: '*'
            self.match(u'*')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end ASTERISK



    # $ANTLR start COLON
    def mCOLON(self, ):

        try:
            self.type = COLON

            # FMFpython.g:41:9: ( ':' )
            # FMFpython.g:41:17: ':'
            self.match(u':')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end COLON



    # $ANTLR start EQUALS
    def mEQUALS(self, ):

        try:
            self.type = EQUALS

            # FMFpython.g:42:9: ( '=' )
            # FMFpython.g:42:17: '='
            self.match(u'=')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end EQUALS



    # $ANTLR start PLUS
    def mPLUS(self, ):

        try:
            # FMFpython.g:44:9: ( '+' )
            # FMFpython.g:44:17: '+'
            self.match(u'+')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end PLUS



    # $ANTLR start NPLUS
    def mNPLUS(self, ):

        try:
            self.type = NPLUS

            # FMFpython.g:45:9: ( ( NPLUS DIGIT )=> PLUS )
            # FMFpython.g:45:17: ( NPLUS DIGIT )=> PLUS
            self.mPLUS()
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end NPLUS



    # $ANTLR start MINUS
    def mMINUS(self, ):

        try:
            # FMFpython.g:47:9: ( '-' )
            # FMFpython.g:47:17: '-'
            self.match(u'-')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end MINUS



    # $ANTLR start NMINUS
    def mNMINUS(self, ):

        try:
            self.type = NMINUS

            # FMFpython.g:48:9: ( ( NMINUS DIGIT )=> MINUS )
            # FMFpython.g:48:17: ( NMINUS DIGIT )=> MINUS
            self.mMINUS()
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end NMINUS



    # $ANTLR start LCURLY
    def mLCURLY(self, ):

        try:
            # FMFpython.g:51:9: ( '{' )
            # FMFpython.g:51:17: '{'
            self.match(u'{')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end LCURLY



    # $ANTLR start RCURLY
    def mRCURLY(self, ):

        try:
            # FMFpython.g:53:9: ( '}' )
            # FMFpython.g:53:17: '}'
            self.match(u'}')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end RCURLY



    # $ANTLR start UNDERSCORE
    def mUNDERSCORE(self, ):

        try:
            # FMFpython.g:56:9: ( '_' )
            # FMFpython.g:56:17: '_'
            self.match(u'_')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end UNDERSCORE



    # $ANTLR start HAT
    def mHAT(self, ):

        try:
            # FMFpython.g:58:9: ( '^' )
            # FMFpython.g:58:17: '^'
            self.match(u'^')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end HAT



    # $ANTLR start DIV
    def mDIV(self, ):

        try:
            # FMFpython.g:60:9: ( '/' )
            # FMFpython.g:60:17: '/'
            self.match(u'/')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end DIV



    # $ANTLR start DOLLAR
    def mDOLLAR(self, ):

        try:
            # FMFpython.g:62:9: ( '$' )
            # FMFpython.g:62:17: '$'
            self.match(u'$')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end DOLLAR



    # $ANTLR start PERCENTAGE
    def mPERCENTAGE(self, ):

        try:
            # FMFpython.g:65:9: ( '%' )
            # FMFpython.g:65:17: '%'
            self.match(u'%')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end PERCENTAGE



    # $ANTLR start LESSTHAN
    def mLESSTHAN(self, ):

        try:
            # FMFpython.g:67:9: ( '<' )
            # FMFpython.g:67:17: '<'
            self.match(u'<')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end LESSTHAN



    # $ANTLR start GREATERTHAN
    def mGREATERTHAN(self, ):

        try:
            # FMFpython.g:70:9: ( '>' )
            # FMFpython.g:70:17: '>'
            self.match(u'>')
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end GREATERTHAN



    # $ANTLR start DIGIT
    def mDIGIT(self, ):

        try:
            # FMFpython.g:72:9: ( ( '0' .. '9' ) )
            # FMFpython.g:72:11: ( '0' .. '9' )
            if (u'0' <= self.input.LA(1) <= u'9'):
                self.input.consume();
                self.failed = False

            else:
                if self.backtracking > 0:
                    self.failed = True
                    return 

                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse






        finally:

            pass

    # $ANTLR end DIGIT



    # $ANTLR start DIGITS
    def mDIGITS(self, ):

        try:
            # FMFpython.g:74:9: ( ( DIGIT )+ )
            # FMFpython.g:74:11: ( DIGIT )+
            # FMFpython.g:74:11: ( DIGIT )+
            cnt5 = 0
            while True: #loop5
                alt5 = 2
                LA5_0 = self.input.LA(1)

                if ((u'0' <= LA5_0 <= u'9')) :
                    alt5 = 1


                if alt5 == 1:
                    # FMFpython.g:74:11: DIGIT
                    self.mDIGIT()
                    if self.failed:
                        return 


                else:
                    if cnt5 >= 1:
                        break #loop5

                    if self.backtracking > 0:
                        self.failed = True
                        return 

                    eee = EarlyExitException(5, self.input)
                    raise eee

                cnt5 += 1






        finally:

            pass

    # $ANTLR end DIGITS



    # $ANTLR start LETTERS
    def mLETTERS(self, ):

        try:
            # FMFpython.g:76:9: ( 'a' .. 'z' | 'A' .. 'Z' )
            # FMFpython.g:
            if (u'A' <= self.input.LA(1) <= u'Z') or (u'a' <= self.input.LA(1) <= u'z'):
                self.input.consume();
                self.failed = False

            else:
                if self.backtracking > 0:
                    self.failed = True
                    return 

                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse






        finally:

            pass

    # $ANTLR end LETTERS



    # $ANTLR start FFLOAT
    def mFFLOAT(self, ):

        try:
            # FMFpython.g:78:9: ( '.' DIGITS ( EXPONENT )? | ( DIGITS '.' ~ DIGIT )=> DIGITS '.' ( EXPONENT )? | ( DIGITS '.' DIGITS ~ '.' )=> DIGITS '.' DIGITS ( EXPONENT )? )
            alt9 = 3
            alt9 = self.dfa9.predict(self.input)
            if alt9 == 1:
                # FMFpython.g:78:13: '.' DIGITS ( EXPONENT )?
                self.match(u'.')
                if self.failed:
                    return 
                self.mDIGITS()
                if self.failed:
                    return 
                # FMFpython.g:78:24: ( EXPONENT )?
                alt6 = 2
                LA6_0 = self.input.LA(1)

                if (LA6_0 == u'E' or LA6_0 == u'e') :
                    alt6 = 1
                if alt6 == 1:
                    # FMFpython.g:78:24: EXPONENT
                    self.mEXPONENT()
                    if self.failed:
                        return 





            elif alt9 == 2:
                # FMFpython.g:79:13: ( DIGITS '.' ~ DIGIT )=> DIGITS '.' ( EXPONENT )?
                self.mDIGITS()
                if self.failed:
                    return 
                self.match(u'.')
                if self.failed:
                    return 
                # FMFpython.g:79:46: ( EXPONENT )?
                alt7 = 2
                LA7_0 = self.input.LA(1)

                if (LA7_0 == u'E' or LA7_0 == u'e') :
                    alt7 = 1
                if alt7 == 1:
                    # FMFpython.g:79:46: EXPONENT
                    self.mEXPONENT()
                    if self.failed:
                        return 





            elif alt9 == 3:
                # FMFpython.g:80:13: ( DIGITS '.' DIGITS ~ '.' )=> DIGITS '.' DIGITS ( EXPONENT )?
                self.mDIGITS()
                if self.failed:
                    return 
                self.match(u'.')
                if self.failed:
                    return 
                self.mDIGITS()
                if self.failed:
                    return 
                # FMFpython.g:80:59: ( EXPONENT )?
                alt8 = 2
                LA8_0 = self.input.LA(1)

                if (LA8_0 == u'E' or LA8_0 == u'e') :
                    alt8 = 1
                if alt8 == 1:
                    # FMFpython.g:80:59: EXPONENT
                    self.mEXPONENT()
                    if self.failed:
                        return 






        finally:

            pass

    # $ANTLR end FFLOAT



    # $ANTLR start EXPONENT
    def mEXPONENT(self, ):

        try:
            # FMFpython.g:84:9: ( ( 'e' | 'E' ) ( PLUS | MINUS )? DIGITS )
            # FMFpython.g:84:14: ( 'e' | 'E' ) ( PLUS | MINUS )? DIGITS
            if self.input.LA(1) == u'E' or self.input.LA(1) == u'e':
                self.input.consume();
                self.failed = False

            else:
                if self.backtracking > 0:
                    self.failed = True
                    return 

                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse


            # FMFpython.g:84:26: ( PLUS | MINUS )?
            alt10 = 2
            LA10_0 = self.input.LA(1)

            if (LA10_0 == u'+' or LA10_0 == u'-') :
                alt10 = 1
            if alt10 == 1:
                # FMFpython.g:
                if self.input.LA(1) == u'+' or self.input.LA(1) == u'-':
                    self.input.consume();
                    self.failed = False

                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return 

                    mse = MismatchedSetException(None, self.input)
                    self.recover(mse)
                    raise mse





            self.mDIGITS()
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end EXPONENT



    # $ANTLR start IINT
    def mIINT(self, ):

        try:
            # FMFpython.g:87:9: ( '0' ( 'x' | 'X' ) ( '0' .. '9' | 'a' .. 'f' | 'A' .. 'F' )+ | '0' ( DIGITS )* | '1' .. '9' ( DIGITS )* )
            alt14 = 3
            LA14_0 = self.input.LA(1)

            if (LA14_0 == u'0') :
                LA14_1 = self.input.LA(2)

                if (LA14_1 == u'X' or LA14_1 == u'x') :
                    alt14 = 1
                else:
                    alt14 = 2
            elif ((u'1' <= LA14_0 <= u'9')) :
                alt14 = 3
            else:
                if self.backtracking > 0:
                    self.failed = True
                    return 

                nvae = NoViableAltException("86:1: fragment IINT : ( '0' ( 'x' | 'X' ) ( '0' .. '9' | 'a' .. 'f' | 'A' .. 'F' )+ | '0' ( DIGITS )* | '1' .. '9' ( DIGITS )* );", 14, 0, self.input)

                raise nvae

            if alt14 == 1:
                # FMFpython.g:87:11: '0' ( 'x' | 'X' ) ( '0' .. '9' | 'a' .. 'f' | 'A' .. 'F' )+
                self.match(u'0')
                if self.failed:
                    return 
                if self.input.LA(1) == u'X' or self.input.LA(1) == u'x':
                    self.input.consume();
                    self.failed = False

                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return 

                    mse = MismatchedSetException(None, self.input)
                    self.recover(mse)
                    raise mse


                # FMFpython.g:87:27: ( '0' .. '9' | 'a' .. 'f' | 'A' .. 'F' )+
                cnt11 = 0
                while True: #loop11
                    alt11 = 2
                    LA11_0 = self.input.LA(1)

                    if ((u'0' <= LA11_0 <= u'9') or (u'A' <= LA11_0 <= u'F') or (u'a' <= LA11_0 <= u'f')) :
                        alt11 = 1


                    if alt11 == 1:
                        # FMFpython.g:
                        if (u'0' <= self.input.LA(1) <= u'9') or (u'A' <= self.input.LA(1) <= u'F') or (u'a' <= self.input.LA(1) <= u'f'):
                            self.input.consume();
                            self.failed = False

                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return 

                            mse = MismatchedSetException(None, self.input)
                            self.recover(mse)
                            raise mse




                    else:
                        if cnt11 >= 1:
                            break #loop11

                        if self.backtracking > 0:
                            self.failed = True
                            return 

                        eee = EarlyExitException(11, self.input)
                        raise eee

                    cnt11 += 1




            elif alt14 == 2:
                # FMFpython.g:88:11: '0' ( DIGITS )*
                self.match(u'0')
                if self.failed:
                    return 
                # FMFpython.g:88:15: ( DIGITS )*
                while True: #loop12
                    alt12 = 2
                    LA12_0 = self.input.LA(1)

                    if ((u'0' <= LA12_0 <= u'9')) :
                        alt12 = 1


                    if alt12 == 1:
                        # FMFpython.g:88:15: DIGITS
                        self.mDIGITS()
                        if self.failed:
                            return 


                    else:
                        break #loop12




            elif alt14 == 3:
                # FMFpython.g:89:11: '1' .. '9' ( DIGITS )*
                self.matchRange(u'1', u'9')
                if self.failed:
                    return 
                # FMFpython.g:89:20: ( DIGITS )*
                while True: #loop13
                    alt13 = 2
                    LA13_0 = self.input.LA(1)

                    if ((u'0' <= LA13_0 <= u'9')) :
                        alt13 = 1


                    if alt13 == 1:
                        # FMFpython.g:89:20: DIGITS
                        self.mDIGITS()
                        if self.failed:
                            return 


                    else:
                        break #loop13





        finally:

            pass

    # $ANTLR end IINT



    # $ANTLR start ESC
    def mESC(self, ):

        try:
            # FMFpython.g:92:9: ( '\\\\' . )
            # FMFpython.g:92:11: '\\\\' .
            self.match(u'\\')
            if self.failed:
                return 
            self.matchAny()
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end ESC



    # $ANTLR start GERMANDATE
    def mGERMANDATE(self, ):

        try:
            self.type = GERMANDATE

            # FMFpython.g:96:9: ( ( DIGIT )? DIGIT '.' ( DIGIT )? DIGIT '.' ( DIGIT DIGIT )? DIGIT DIGIT )
            # FMFpython.g:96:11: ( DIGIT )? DIGIT '.' ( DIGIT )? DIGIT '.' ( DIGIT DIGIT )? DIGIT DIGIT
            # FMFpython.g:96:11: ( DIGIT )?
            alt15 = 2
            LA15_0 = self.input.LA(1)

            if ((u'0' <= LA15_0 <= u'9')) :
                LA15_1 = self.input.LA(2)

                if ((u'0' <= LA15_1 <= u'9')) :
                    alt15 = 1
            if alt15 == 1:
                # FMFpython.g:96:11: DIGIT
                self.mDIGIT()
                if self.failed:
                    return 



            self.mDIGIT()
            if self.failed:
                return 
            self.match(u'.')
            if self.failed:
                return 
            # FMFpython.g:96:28: ( DIGIT )?
            alt16 = 2
            LA16_0 = self.input.LA(1)

            if ((u'0' <= LA16_0 <= u'9')) :
                LA16_1 = self.input.LA(2)

                if ((u'0' <= LA16_1 <= u'9')) :
                    alt16 = 1
            if alt16 == 1:
                # FMFpython.g:96:28: DIGIT
                self.mDIGIT()
                if self.failed:
                    return 



            self.mDIGIT()
            if self.failed:
                return 
            self.match(u'.')
            if self.failed:
                return 
            # FMFpython.g:96:45: ( DIGIT DIGIT )?
            alt17 = 2
            LA17_0 = self.input.LA(1)

            if ((u'0' <= LA17_0 <= u'9')) :
                LA17_1 = self.input.LA(2)

                if ((u'0' <= LA17_1 <= u'9')) :
                    LA17_2 = self.input.LA(3)

                    if ((u'0' <= LA17_2 <= u'9')) :
                        alt17 = 1
            if alt17 == 1:
                # FMFpython.g:96:46: DIGIT DIGIT
                self.mDIGIT()
                if self.failed:
                    return 
                self.mDIGIT()
                if self.failed:
                    return 



            self.mDIGIT()
            if self.failed:
                return 
            self.mDIGIT()
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end GERMANDATE



    # $ANTLR start ISODATE
    def mISODATE(self, ):

        try:
            self.type = ISODATE

            # FMFpython.g:97:9: ( DIGIT DIGIT DIGIT DIGIT MINUS DIGIT DIGIT MINUS DIGIT DIGIT )
            # FMFpython.g:97:11: DIGIT DIGIT DIGIT DIGIT MINUS DIGIT DIGIT MINUS DIGIT DIGIT
            self.mDIGIT()
            if self.failed:
                return 
            self.mDIGIT()
            if self.failed:
                return 
            self.mDIGIT()
            if self.failed:
                return 
            self.mDIGIT()
            if self.failed:
                return 
            self.mMINUS()
            if self.failed:
                return 
            self.mDIGIT()
            if self.failed:
                return 
            self.mDIGIT()
            if self.failed:
                return 
            self.mMINUS()
            if self.failed:
                return 
            self.mDIGIT()
            if self.failed:
                return 
            self.mDIGIT()
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end ISODATE



    # $ANTLR start FLOAT
    def mFLOAT(self, ):

        try:
            self.type = FLOAT

            # FMFpython.g:99:9: ( ( FFLOAT ~ ( 'j' | 'J' | 'i' | 'I' ) )=> FFLOAT )
            # FMFpython.g:99:11: ( FFLOAT ~ ( 'j' | 'J' | 'i' | 'I' ) )=> FFLOAT
            self.mFFLOAT()
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end FLOAT



    # $ANTLR start INT
    def mINT(self, ):

        try:
            self.type = INT

            # FMFpython.g:101:9: ( ( IINT ~ ( 'j' | 'J' | 'i' | 'I' ) )=> IINT )
            # FMFpython.g:101:11: ( IINT ~ ( 'j' | 'J' | 'i' | 'I' ) )=> IINT
            self.mIINT()
            if self.failed:
                return 




        finally:

            pass

    # $ANTLR end INT



    # $ANTLR start IMAG
    def mIMAG(self, ):

        try:
            self.type = IMAG

            # FMFpython.g:103:9: ( IINT ( 'j' | 'J' | 'i' | 'I' ) | FFLOAT ( 'j' | 'J' | 'i' | 'I' ) )
            alt18 = 2
            alt18 = self.dfa18.predict(self.input)
            if alt18 == 1:
                # FMFpython.g:103:13: IINT ( 'j' | 'J' | 'i' | 'I' )
                self.mIINT()
                if self.failed:
                    return 
                if (u'I' <= self.input.LA(1) <= u'J') or (u'i' <= self.input.LA(1) <= u'j'):
                    self.input.consume();
                    self.failed = False

                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return 

                    mse = MismatchedSetException(None, self.input)
                    self.recover(mse)
                    raise mse




            elif alt18 == 2:
                # FMFpython.g:104:13: FFLOAT ( 'j' | 'J' | 'i' | 'I' )
                self.mFFLOAT()
                if self.failed:
                    return 
                if (u'I' <= self.input.LA(1) <= u'J') or (u'i' <= self.input.LA(1) <= u'j'):
                    self.input.consume();
                    self.failed = False

                else:
                    if self.backtracking > 0:
                        self.failed = True
                        return 

                    mse = MismatchedSetException(None, self.input)
                    self.recover(mse)
                    raise mse





        finally:

            pass

    # $ANTLR end IMAG



    # $ANTLR start RWORD
    def mRWORD(self, ):

        try:
            # FMFpython.g:108:9: ( ( '\\\\' | LETTERS ) ( '\\\\' | LETTERS | DIGITS | UNDERSCORE | HAT | LCURLY | RCURLY | MINUS )* )
            # FMFpython.g:108:11: ( '\\\\' | LETTERS ) ( '\\\\' | LETTERS | DIGITS | UNDERSCORE | HAT | LCURLY | RCURLY | MINUS )*
            if (u'A' <= self.input.LA(1) <= u'Z') or self.input.LA(1) == u'\\' or (u'a' <= self.input.LA(1) <= u'z'):
                self.input.consume();
                self.failed = False

            else:
                if self.backtracking > 0:
                    self.failed = True
                    return 

                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse


            # FMFpython.g:108:28: ( '\\\\' | LETTERS | DIGITS | UNDERSCORE | HAT | LCURLY | RCURLY | MINUS )*
            while True: #loop19
                alt19 = 9
                LA19 = self.input.LA(1)
                if LA19 == u'\\':
                    alt19 = 1
                elif LA19 == u'A' or LA19 == u'B' or LA19 == u'C' or LA19 == u'D' or LA19 == u'E' or LA19 == u'F' or LA19 == u'G' or LA19 == u'H' or LA19 == u'I' or LA19 == u'J' or LA19 == u'K' or LA19 == u'L' or LA19 == u'M' or LA19 == u'N' or LA19 == u'O' or LA19 == u'P' or LA19 == u'Q' or LA19 == u'R' or LA19 == u'S' or LA19 == u'T' or LA19 == u'U' or LA19 == u'V' or LA19 == u'W' or LA19 == u'X' or LA19 == u'Y' or LA19 == u'Z' or LA19 == u'a' or LA19 == u'b' or LA19 == u'c' or LA19 == u'd' or LA19 == u'e' or LA19 == u'f' or LA19 == u'g' or LA19 == u'h' or LA19 == u'i' or LA19 == u'j' or LA19 == u'k' or LA19 == u'l' or LA19 == u'm' or LA19 == u'n' or LA19 == u'o' or LA19 == u'p' or LA19 == u'q' or LA19 == u'r' or LA19 == u's' or LA19 == u't' or LA19 == u'u' or LA19 == u'v' or LA19 == u'w' or LA19 == u'x' or LA19 == u'y' or LA19 == u'z':
                    alt19 = 2
                elif LA19 == u'0' or LA19 == u'1' or LA19 == u'2' or LA19 == u'3' or LA19 == u'4' or LA19 == u'5' or LA19 == u'6' or LA19 == u'7' or LA19 == u'8' or LA19 == u'9':
                    alt19 = 3
                elif LA19 == u'_':
                    alt19 = 4
                elif LA19 == u'^':
                    alt19 = 5
                elif LA19 == u'{':
                    alt19 = 6
                elif LA19 == u'}':
                    alt19 = 7
                elif LA19 == u'-':
                    alt19 = 8

                if alt19 == 1:
                    # FMFpython.g:108:29: '\\\\'
                    self.match(u'\\')
                    if self.failed:
                        return 


                elif alt19 == 2:
                    # FMFpython.g:108:36: LETTERS
                    self.mLETTERS()
                    if self.failed:
                        return 


                elif alt19 == 3:
                    # FMFpython.g:108:46: DIGITS
                    self.mDIGITS()
                    if self.failed:
                        return 


                elif alt19 == 4:
                    # FMFpython.g:108:55: UNDERSCORE
                    self.mUNDERSCORE()
                    if self.failed:
                        return 


                elif alt19 == 5:
                    # FMFpython.g:108:68: HAT
                    self.mHAT()
                    if self.failed:
                        return 


                elif alt19 == 6:
                    # FMFpython.g:108:74: LCURLY
                    self.mLCURLY()
                    if self.failed:
                        return 


                elif alt19 == 7:
                    # FMFpython.g:108:83: RCURLY
                    self.mRCURLY()
                    if self.failed:
                        return 


                elif alt19 == 8:
                    # FMFpython.g:108:92: MINUS
                    self.mMINUS()
                    if self.failed:
                        return 


                else:
                    break #loop19






        finally:

            pass

    # $ANTLR end RWORD



    # $ANTLR start WORD
    def mWORD(self, ):

        try:
            self.type = WORD

            # FMFpython.g:111:9: ( RWORD | LESSTHAN RWORD GREATERTHAN )
            alt20 = 2
            LA20_0 = self.input.LA(1)

            if ((u'A' <= LA20_0 <= u'Z') or LA20_0 == u'\\' or (u'a' <= LA20_0 <= u'z')) :
                alt20 = 1
            elif (LA20_0 == u'<') :
                alt20 = 2
            else:
                if self.backtracking > 0:
                    self.failed = True
                    return 

                nvae = NoViableAltException("111:1: WORD : ( RWORD | LESSTHAN RWORD GREATERTHAN );", 20, 0, self.input)

                raise nvae

            if alt20 == 1:
                # FMFpython.g:111:11: RWORD
                self.mRWORD()
                if self.failed:
                    return 


            elif alt20 == 2:
                # FMFpython.g:112:11: LESSTHAN RWORD GREATERTHAN
                self.mLESSTHAN()
                if self.failed:
                    return 
                self.mRWORD()
                if self.failed:
                    return 
                self.mGREATERTHAN()
                if self.failed:
                    return 



        finally:

            pass

    # $ANTLR end WORD



    # $ANTLR start PUNCTUATION
    def mPUNCTUATION(self, ):

        try:
            self.type = PUNCTUATION

            # FMFpython.g:116:9: ( '.' | ',' | ';' )
            # FMFpython.g:
            if self.input.LA(1) == u',' or self.input.LA(1) == u'.' or self.input.LA(1) == u';':
                self.input.consume();
                self.failed = False

            else:
                if self.backtracking > 0:
                    self.failed = True
                    return 

                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse






        finally:

            pass

    # $ANTLR end PUNCTUATION



    # $ANTLR start LITERAL
    def mLITERAL(self, ):

        try:
            self.type = LITERAL

            # FMFpython.g:118:9: ( '\"' ( ESC | ~ ( '\\\\' | '\\n' | '\"' ) )* '\"' | '\\'' ( ESC | ~ ( '\\\\' | '\\n' | '\\'' ) )* '\\'' )
            alt23 = 2
            LA23_0 = self.input.LA(1)

            if (LA23_0 == u'"') :
                alt23 = 1
            elif (LA23_0 == u'\'') :
                alt23 = 2
            else:
                if self.backtracking > 0:
                    self.failed = True
                    return 

                nvae = NoViableAltException("118:1: LITERAL : ( '\"' ( ESC | ~ ( '\\\\' | '\\n' | '\"' ) )* '\"' | '\\'' ( ESC | ~ ( '\\\\' | '\\n' | '\\'' ) )* '\\'' );", 23, 0, self.input)

                raise nvae

            if alt23 == 1:
                # FMFpython.g:118:11: '\"' ( ESC | ~ ( '\\\\' | '\\n' | '\"' ) )* '\"'
                self.match(u'"')
                if self.failed:
                    return 
                # FMFpython.g:118:15: ( ESC | ~ ( '\\\\' | '\\n' | '\"' ) )*
                while True: #loop21
                    alt21 = 3
                    LA21_0 = self.input.LA(1)

                    if (LA21_0 == u'\\') :
                        alt21 = 1
                    elif ((u'\u0000' <= LA21_0 <= u'\t') or (u'\u000B' <= LA21_0 <= u'!') or (u'#' <= LA21_0 <= u'[') or (u']' <= LA21_0 <= u'\uFFFE')) :
                        alt21 = 2


                    if alt21 == 1:
                        # FMFpython.g:118:16: ESC
                        self.mESC()
                        if self.failed:
                            return 


                    elif alt21 == 2:
                        # FMFpython.g:118:20: ~ ( '\\\\' | '\\n' | '\"' )
                        if (u'\u0000' <= self.input.LA(1) <= u'\t') or (u'\u000B' <= self.input.LA(1) <= u'!') or (u'#' <= self.input.LA(1) <= u'[') or (u']' <= self.input.LA(1) <= u'\uFFFE'):
                            self.input.consume();
                            self.failed = False

                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return 

                            mse = MismatchedSetException(None, self.input)
                            self.recover(mse)
                            raise mse




                    else:
                        break #loop21


                self.match(u'"')
                if self.failed:
                    return 


            elif alt23 == 2:
                # FMFpython.g:119:11: '\\'' ( ESC | ~ ( '\\\\' | '\\n' | '\\'' ) )* '\\''
                self.match(u'\'')
                if self.failed:
                    return 
                # FMFpython.g:119:16: ( ESC | ~ ( '\\\\' | '\\n' | '\\'' ) )*
                while True: #loop22
                    alt22 = 3
                    LA22_0 = self.input.LA(1)

                    if (LA22_0 == u'\\') :
                        alt22 = 1
                    elif ((u'\u0000' <= LA22_0 <= u'\t') or (u'\u000B' <= LA22_0 <= u'&') or (u'(' <= LA22_0 <= u'[') or (u']' <= LA22_0 <= u'\uFFFE')) :
                        alt22 = 2


                    if alt22 == 1:
                        # FMFpython.g:119:17: ESC
                        self.mESC()
                        if self.failed:
                            return 


                    elif alt22 == 2:
                        # FMFpython.g:119:21: ~ ( '\\\\' | '\\n' | '\\'' )
                        if (u'\u0000' <= self.input.LA(1) <= u'\t') or (u'\u000B' <= self.input.LA(1) <= u'&') or (u'(' <= self.input.LA(1) <= u'[') or (u']' <= self.input.LA(1) <= u'\uFFFE'):
                            self.input.consume();
                            self.failed = False

                        else:
                            if self.backtracking > 0:
                                self.failed = True
                                return 

                            mse = MismatchedSetException(None, self.input)
                            self.recover(mse)
                            raise mse




                    else:
                        break #loop22


                self.match(u'\'')
                if self.failed:
                    return 



        finally:

            pass

    # $ANTLR end LITERAL



    def mTokens(self):
        # FMFpython.g:1:8: ( T64 | T65 | T66 | T67 | NEWLINE | WS | COMMENT | LBRACK | RBRACK | LPAREN | RPAREN | ASTERISK | COLON | EQUALS | NPLUS | NMINUS | GERMANDATE | ISODATE | FLOAT | INT | IMAG | WORD | PUNCTUATION | LITERAL )
        alt24 = 24
        alt24 = self.dfa24.predict(self.input)
        if alt24 == 1:
            # FMFpython.g:1:10: T64
            self.mT64()
            if self.failed:
                return 


        elif alt24 == 2:
            # FMFpython.g:1:14: T65
            self.mT65()
            if self.failed:
                return 


        elif alt24 == 3:
            # FMFpython.g:1:18: T66
            self.mT66()
            if self.failed:
                return 


        elif alt24 == 4:
            # FMFpython.g:1:22: T67
            self.mT67()
            if self.failed:
                return 


        elif alt24 == 5:
            # FMFpython.g:1:26: NEWLINE
            self.mNEWLINE()
            if self.failed:
                return 


        elif alt24 == 6:
            # FMFpython.g:1:34: WS
            self.mWS()
            if self.failed:
                return 


        elif alt24 == 7:
            # FMFpython.g:1:37: COMMENT
            self.mCOMMENT()
            if self.failed:
                return 


        elif alt24 == 8:
            # FMFpython.g:1:45: LBRACK
            self.mLBRACK()
            if self.failed:
                return 


        elif alt24 == 9:
            # FMFpython.g:1:52: RBRACK
            self.mRBRACK()
            if self.failed:
                return 


        elif alt24 == 10:
            # FMFpython.g:1:59: LPAREN
            self.mLPAREN()
            if self.failed:
                return 


        elif alt24 == 11:
            # FMFpython.g:1:66: RPAREN
            self.mRPAREN()
            if self.failed:
                return 


        elif alt24 == 12:
            # FMFpython.g:1:73: ASTERISK
            self.mASTERISK()
            if self.failed:
                return 


        elif alt24 == 13:
            # FMFpython.g:1:82: COLON
            self.mCOLON()
            if self.failed:
                return 


        elif alt24 == 14:
            # FMFpython.g:1:88: EQUALS
            self.mEQUALS()
            if self.failed:
                return 


        elif alt24 == 15:
            # FMFpython.g:1:95: NPLUS
            self.mNPLUS()
            if self.failed:
                return 


        elif alt24 == 16:
            # FMFpython.g:1:101: NMINUS
            self.mNMINUS()
            if self.failed:
                return 


        elif alt24 == 17:
            # FMFpython.g:1:108: GERMANDATE
            self.mGERMANDATE()
            if self.failed:
                return 


        elif alt24 == 18:
            # FMFpython.g:1:119: ISODATE
            self.mISODATE()
            if self.failed:
                return 


        elif alt24 == 19:
            # FMFpython.g:1:127: FLOAT
            self.mFLOAT()
            if self.failed:
                return 


        elif alt24 == 20:
            # FMFpython.g:1:133: INT
            self.mINT()
            if self.failed:
                return 


        elif alt24 == 21:
            # FMFpython.g:1:137: IMAG
            self.mIMAG()
            if self.failed:
                return 


        elif alt24 == 22:
            # FMFpython.g:1:142: WORD
            self.mWORD()
            if self.failed:
                return 


        elif alt24 == 23:
            # FMFpython.g:1:147: PUNCTUATION
            self.mPUNCTUATION()
            if self.failed:
                return 


        elif alt24 == 24:
            # FMFpython.g:1:159: LITERAL
            self.mLITERAL()
            if self.failed:
                return 






    # $ANTLR start synpred3
    def synpred3_fragment(self, ):
        # FMFpython.g:79:13: ( DIGITS '.' ~ DIGIT )
        # FMFpython.g:79:14: DIGITS '.' ~ DIGIT
        self.mDIGITS()
        if self.failed:
            return 
        self.match(u'.')
        if self.failed:
            return 
        if (u'\u0000' <= self.input.LA(1) <= u'$') or (u'&' <= self.input.LA(1) <= u'\uFFFE'):
            self.input.consume();
            self.failed = False

        else:
            if self.backtracking > 0:
                self.failed = True
                return 

            mse = MismatchedSetException(None, self.input)
            self.recover(mse)
            raise mse




    # $ANTLR end synpred3



    # $ANTLR start synpred4
    def synpred4_fragment(self, ):
        # FMFpython.g:80:13: ( DIGITS '.' DIGITS ~ '.' )
        # FMFpython.g:80:14: DIGITS '.' DIGITS ~ '.'
        self.mDIGITS()
        if self.failed:
            return 
        self.match(u'.')
        if self.failed:
            return 
        self.mDIGITS()
        if self.failed:
            return 
        if (u'\u0000' <= self.input.LA(1) <= u'-') or (u'/' <= self.input.LA(1) <= u'\uFFFE'):
            self.input.consume();
            self.failed = False

        else:
            if self.backtracking > 0:
                self.failed = True
                return 

            mse = MismatchedSetException(None, self.input)
            self.recover(mse)
            raise mse




    # $ANTLR end synpred4



    def synpred3(self):
        self.backtracking += 1
        start = self.input.mark()
        self.synpred3_fragment()
        success = not self.failed
        self.input.rewind(start)
        self.backtracking -= 1
        self.failed = False
        return success

    def synpred4(self):
        self.backtracking += 1
        start = self.input.mark()
        self.synpred4_fragment()
        success = not self.failed
        self.input.rewind(start)
        self.backtracking -= 1
        self.failed = False
        return success



    # lookup tables for DFA #9

    DFA9_eot = DFA.unpack(
        u"\3\uffff\1\5\3\uffff"
        )

    DFA9_eof = DFA.unpack(
        u"\7\uffff"
        )

    DFA9_min = DFA.unpack(
        u"\1\56\1\uffff\1\56\1\60\3\uffff"
        )

    DFA9_max = DFA.unpack(
        u"\1\71\1\uffff\1\71\1\145\3\uffff"
        )

    DFA9_accept = DFA.unpack(
        u"\1\uffff\1\1\2\uffff\2\2\1\3"
        )

    DFA9_special = DFA.unpack(
        u"\3\uffff\1\0\3\uffff"
        )

            
    DFA9_transition = [
        DFA.unpack(u"\1\1\1\uffff\12\2"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\3\1\uffff\12\2"),
        DFA.unpack(u"\12\6\13\uffff\1\4\37\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"")
    ]

    # class definition for DFA #9

    class DFA9(DFA):
        def specialStateTransition(self_, s, input):
            # convince pylint that my self_ magic is ok ;)
            # pylint: disable-msg=E0213

            # pretend we are a member of the recognizer
            # thus semantic predicates can be evaluated
            self = self_.recognizer

            _s = s

            if s == 0: 
                LA9_3 = input.LA(1)

                 
                index9_3 = input.index()
                input.rewind()
                s = -1
                if (LA9_3 == u'E' or LA9_3 == u'e') and (self.synpred3()):
                    s = 4

                elif ((u'0' <= LA9_3 <= u'9')) and (self.synpred4()):
                    s = 6

                else:
                    s = 5

                 
                input.seek(index9_3)
                if s >= 0:
                    return s

            if self.backtracking >0:
                self.failed = True
                return -1
            nvae = NoViableAltException(self_.getDescription(), 9, _s, input)
            self_.error(nvae)
            raise nvae
    # lookup tables for DFA #18

    DFA18_eot = DFA.unpack(
        u"\7\uffff"
        )

    DFA18_eof = DFA.unpack(
        u"\7\uffff"
        )

    DFA18_min = DFA.unpack(
        u"\3\56\2\uffff\2\56"
        )

    DFA18_max = DFA.unpack(
        u"\1\71\1\170\1\152\2\uffff\2\152"
        )

    DFA18_accept = DFA.unpack(
        u"\3\uffff\1\2\1\1\2\uffff"
        )

    DFA18_special = DFA.unpack(
        u"\7\uffff"
        )

            
    DFA18_transition = [
        DFA.unpack(u"\1\3\1\uffff\1\1\11\2"),
        DFA.unpack(u"\1\3\1\uffff\12\5\17\uffff\2\4\15\uffff\1\4\20\uffff"
        u"\2\4\15\uffff\1\4"),
        DFA.unpack(u"\1\3\1\uffff\12\6\17\uffff\2\4\36\uffff\2\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\3\1\uffff\12\5\17\uffff\2\4\36\uffff\2\4"),
        DFA.unpack(u"\1\3\1\uffff\12\6\17\uffff\2\4\36\uffff\2\4")
    ]

    # class definition for DFA #18

    DFA18 = DFA
    # lookup tables for DFA #24

    DFA24_eot = DFA.unpack(
        u"\1\uffff\2\23\3\uffff\1\31\11\uffff\1\33\1\31\1\33\3\uffff\2\23"
        u"\4\uffff\1\46\1\33\1\uffff\1\46\1\33\2\23\1\33\1\46\2\uffff\1\33"
        u"\1\uffff\1\33\1\23\1\70\1\uffff\1\46\2\uffff\2\46\1\33\1\uffff"
        u"\1\46\1\33\1\23\3\uffff\2\46\1\33\1\uffff\1\33\3\23\1\103\1\uffff"
        )

    DFA24_eof = DFA.unpack(
        u"\104\uffff"
        )

    DFA24_min = DFA.unpack(
        u"\1\11\1\145\1\141\3\uffff\1\0\11\uffff\1\56\1\60\1\56\3\uffff\1"
        u"\146\1\164\2\uffff\1\60\1\uffff\1\60\1\56\1\uffff\1\60\1\56\1\145"
        u"\1\141\1\60\1\56\1\53\1\uffff\1\56\1\53\1\56\1\162\1\40\1\53\1"
        u"\56\1\uffff\3\60\1\55\2\60\1\55\1\145\2\uffff\3\60\1\56\1\uffff"
        u"\1\56\1\156\1\143\1\145\1\55\1\uffff"
        )

    DFA24_max = DFA.unpack(
        u"\1\172\1\145\1\141\3\uffff\1\ufffe\11\uffff\1\170\1\71\1\152\3"
        u"\uffff\1\146\1\164\2\uffff\1\146\1\uffff\2\152\1\uffff\2\152\1"
        u"\145\1\141\2\152\1\71\1\uffff\1\152\1\71\1\152\1\162\1\175\1\71"
        u"\1\152\1\uffff\1\71\3\152\1\71\2\152\1\145\2\uffff\1\71\3\152\1"
        u"\uffff\1\152\1\156\1\143\1\145\1\175\1\uffff"
        )

    DFA24_accept = DFA.unpack(
        u"\3\uffff\1\4\1\5\1\6\1\uffff\1\10\1\11\1\12\1\13\1\14\1\15\1\16"
        u"\1\17\1\20\3\uffff\1\26\1\7\1\30\2\uffff\1\4\1\27\1\uffff\1\24"
        u"\2\uffff\1\25\7\uffff\1\23\7\uffff\1\21\10\uffff\1\2\1\3\4\uffff"
        u"\1\22\5\uffff\1\1"
        )

    DFA24_special = DFA.unpack(
        u"\104\uffff"
        )

            
    DFA24_transition = [
        DFA.unpack(u"\1\5\1\4\2\uffff\1\4\22\uffff\1\5\1\uffff\1\25\1\24"
        u"\3\uffff\1\25\1\11\1\12\1\13\1\16\1\3\1\17\1\21\1\uffff\1\20\11"
        u"\22\1\14\1\6\1\23\1\15\3\uffff\32\23\1\7\1\23\1\10\3\uffff\3\23"
        u"\1\2\15\23\1\1\10\23"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\uffff\24"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\34\1\uffff\12\35\17\uffff\2\36\15\uffff\1\32\20\uffff"
        u"\2\36\15\uffff\1\32"),
        DFA.unpack(u"\12\37"),
        DFA.unpack(u"\1\34\1\uffff\12\40\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\41"),
        DFA.unpack(u"\1\42"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\12\43\7\uffff\6\43\32\uffff\6\43"),
        DFA.unpack(u""),
        DFA.unpack(u"\12\44\13\uffff\1\45\3\uffff\2\36\32\uffff\1\45\3\uffff"
        u"\2\36"),
        DFA.unpack(u"\1\34\1\uffff\12\47\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u""),
        DFA.unpack(u"\12\37\13\uffff\1\50\3\uffff\2\36\32\uffff\1\50\3\uffff"
        u"\2\36"),
        DFA.unpack(u"\1\34\1\uffff\12\51\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u"\1\52"),
        DFA.unpack(u"\1\53"),
        DFA.unpack(u"\12\43\7\uffff\6\43\2\uffff\2\36\26\uffff\6\43\2\uffff"
        u"\2\36"),
        DFA.unpack(u"\1\56\1\uffff\12\55\13\uffff\1\54\3\uffff\2\36\32\uffff"
        u"\1\54\3\uffff\2\36"),
        DFA.unpack(u"\1\57\1\uffff\1\57\2\uffff\12\60"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\61\1\uffff\12\62\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u"\1\63\1\uffff\1\63\2\uffff\12\64"),
        DFA.unpack(u"\1\61\1\uffff\12\65\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u"\1\66"),
        DFA.unpack(u"\1\67\14\uffff\1\23\2\uffff\12\23\7\uffff\32\23\1\uffff"
        u"\1\23\1\uffff\2\23\1\uffff\33\23\1\uffff\1\23"),
        DFA.unpack(u"\1\71\1\uffff\1\71\2\uffff\12\72"),
        DFA.unpack(u"\1\56\1\uffff\12\73\13\uffff\1\54\3\uffff\2\36\32\uffff"
        u"\1\54\3\uffff\2\36"),
        DFA.unpack(u""),
        DFA.unpack(u"\12\60"),
        DFA.unpack(u"\12\60\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u"\12\73\13\uffff\1\45\3\uffff\2\36\32\uffff\1\45\3\uffff"
        u"\2\36"),
        DFA.unpack(u"\1\75\1\61\1\uffff\12\74\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u"\12\64"),
        DFA.unpack(u"\12\64\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u"\1\75\1\61\1\uffff\12\76\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u"\1\77"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\12\72"),
        DFA.unpack(u"\12\72\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u"\12\73\13\uffff\1\54\3\uffff\2\36\32\uffff\1\54\3\uffff"
        u"\2\36"),
        DFA.unpack(u"\1\61\1\uffff\12\74\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\61\1\uffff\12\76\17\uffff\2\36\36\uffff\2\36"),
        DFA.unpack(u"\1\100"),
        DFA.unpack(u"\1\101"),
        DFA.unpack(u"\1\102"),
        DFA.unpack(u"\1\23\2\uffff\12\23\7\uffff\32\23\1\uffff\1\23\1\uffff"
        u"\2\23\1\uffff\33\23\1\uffff\1\23"),
        DFA.unpack(u"")
    ]

    # class definition for DFA #24

    DFA24 = DFA
 

