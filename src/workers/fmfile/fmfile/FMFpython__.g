lexer grammar FMFpython;
options {
  language=Python;

}

T64 : 'reference' ;
T65 : 'data definitions' ;
T66 : 'data' ;
T67 : ',' ;

// $ANTLR src "FMFpython.g" 32
NEWLINE :       ('\r'? '\n')+;
// $ANTLR src "FMFpython.g" 33
WS      :       (' ' | '\t')+ {$channel=HIDDEN;};
// $ANTLR src "FMFpython.g" 34
COMMENT :       (';' | '#') .* NEWLINE {$channel=HIDDEN;};

// $ANTLR src "FMFpython.g" 36
LBRACK  :       '[';
// $ANTLR src "FMFpython.g" 37
RBRACK  :       ']';
// $ANTLR src "FMFpython.g" 38
LPAREN  :       '(';
// $ANTLR src "FMFpython.g" 39
RPAREN  :       ')';
// $ANTLR src "FMFpython.g" 40
ASTERISK:       '*';
// $ANTLR src "FMFpython.g" 41
COLON   :       ':';
// $ANTLR src "FMFpython.g" 42
EQUALS  :       '=';
// $ANTLR src "FMFpython.g" 43
fragment
PLUS    :       '+';
// $ANTLR src "FMFpython.g" 45
NPLUS   :       (NPLUS DIGIT)=> PLUS;
// $ANTLR src "FMFpython.g" 46
fragment
MINUS   :       '-';
// $ANTLR src "FMFpython.g" 48
NMINUS  :       (NMINUS DIGIT)=> MINUS;

// $ANTLR src "FMFpython.g" 50
fragment
LCURLY  :       '{';
// $ANTLR src "FMFpython.g" 52
fragment
RCURLY  :       '}';
// $ANTLR src "FMFpython.g" 54
fragment
UNDERSCORE
        :       '_';
// $ANTLR src "FMFpython.g" 57
fragment
HAT     :       '^';
// $ANTLR src "FMFpython.g" 59
fragment
DIV     :       '/';
// $ANTLR src "FMFpython.g" 61
fragment
DOLLAR  :       '$';
// $ANTLR src "FMFpython.g" 63
fragment
PERCENTAGE
        :       '%';
// $ANTLR src "FMFpython.g" 66
fragment
LESSTHAN:       '<';
// $ANTLR src "FMFpython.g" 68
fragment
GREATERTHAN
        :       '>';
// $ANTLR src "FMFpython.g" 71
fragment
DIGIT   : ( '0' .. '9' ) ;
// $ANTLR src "FMFpython.g" 73
fragment
DIGITS  : DIGIT+;
// $ANTLR src "FMFpython.g" 75
fragment
LETTERS : 'a'..'z' | 'A'..'Z';
// $ANTLR src "FMFpython.g" 77
fragment
FFLOAT  :   '.' DIGITS EXPONENT?
        |   (DIGITS '.' ~DIGIT) =>DIGITS '.' EXPONENT?
        |   (DIGITS '.' DIGITS ~'.') => DIGITS '.' DIGITS EXPONENT?
        ;
// $ANTLR src "FMFpython.g" 82
fragment
EXPONENT
        :    ('e' | 'E') ( PLUS | MINUS )? DIGITS
        ;
// $ANTLR src "FMFpython.g" 86
fragment
IINT    : '0' ('x' | 'X') ( '0' .. '9' | 'a' .. 'f' | 'A' .. 'F' )+ //hex
        | '0' DIGITS* //octal
        | '1'..'9' DIGITS* //decimal
        ;
// $ANTLR src "FMFpython.g" 91
fragment        
ESC     : '\\' .;


// $ANTLR src "FMFpython.g" 95
GERMANDATE 
        : DIGIT? DIGIT '.' DIGIT? DIGIT '.' (DIGIT DIGIT)? DIGIT DIGIT;
// $ANTLR src "FMFpython.g" 97
ISODATE : DIGIT DIGIT DIGIT DIGIT MINUS DIGIT DIGIT MINUS DIGIT DIGIT;

// $ANTLR src "FMFpython.g" 99
FLOAT   : (FFLOAT ~('j'|'J'|'i'|'I')) => FFLOAT;

// $ANTLR src "FMFpython.g" 101
INT     : (IINT ~('j'|'J'|'i'|'I')) => IINT;

// $ANTLR src "FMFpython.g" 103
IMAG    :   IINT ('j'|'J'|'i'|'I')
        |   FFLOAT ('j'|'J'|'i'|'I')
        ;

// $ANTLR src "FMFpython.g" 107
fragment
RWORD   : ('\\' | LETTERS) ('\\' | LETTERS | DIGITS | UNDERSCORE | HAT | LCURLY | RCURLY | MINUS)*
        ;

// $ANTLR src "FMFpython.g" 111
WORD    : RWORD
        | LESSTHAN RWORD GREATERTHAN
        ;

// $ANTLR src "FMFpython.g" 115
PUNCTUATION 
        : '.' | ',' | ';';

// $ANTLR src "FMFpython.g" 118
LITERAL : '"' (ESC|~('\\'|'\n'|'"'))* '"'
        | '\'' (ESC|~('\\'|'\n'|'\''))* '\''
        ;

