grammar FMFpython;

options {
    language=Python;
    output=AST;
}

tokens {
    CONFIG;
    HEADER;
    COMMON_SECTION;
    DATADEF_SECTION;
    DATA_SECTION;
    BODY;
    ITEM;
    DATASET;
    KEY;
    DATETIME;
    DATE;
    TIME;
    NUMBER;
    VARIABLE;
    IDENTIFIER;
    QUANTITY;
    UNIT;
    STRING;
    COLSPEC;
    LONGNAME;
    DEPS;
}

NEWLINE :       ('\r'? '\n')+;
WS      :       (' ' | '\t')+ {$channel=HIDDEN;};
COMMENT :       (';' | '#') .* NEWLINE {$channel=HIDDEN;};

LBRACK  :       '[';
RBRACK  :       ']';
LPAREN  :       '(';
RPAREN  :       ')';
ASTERISK:       '*';
COLON   :       ':';
EQUALS  :       '=';
fragment
PLUS    :       '+';
NPLUS   :       (NPLUS DIGIT)=> PLUS;
fragment
MINUS   :       '-';
NMINUS  :       (NMINUS DIGIT)=> MINUS;

fragment
LCURLY  :       '{';
fragment
RCURLY  :       '}';
fragment
UNDERSCORE
        :       '_';
fragment
HAT     :       '^';
fragment
DIV     :       '/';
fragment
DOLLAR  :       '$';
fragment
PERCENTAGE
        :       '%';
fragment
LESSTHAN:       '<';
fragment
GREATERTHAN
        :       '>';
fragment
DIGIT   : ( '0' .. '9' ) ;
fragment
DIGITS  : DIGIT+;
fragment
LETTERS : 'a'..'z' | 'A'..'Z';
fragment
FFLOAT  :   '.' DIGITS EXPONENT?
        |   (DIGITS '.' ~DIGIT) =>DIGITS '.' EXPONENT?
        |   (DIGITS '.' DIGITS ~'.') => DIGITS '.' DIGITS EXPONENT?
        ;
fragment
EXPONENT
        :    ('e' | 'E') ( PLUS | MINUS )? DIGITS
        ;
fragment
IINT    : '0' ('x' | 'X') ( '0' .. '9' | 'a' .. 'f' | 'A' .. 'F' )+ //hex
        | '0' DIGITS* //octal
        | '1'..'9' DIGITS* //decimal
        ;
fragment
ESC     : '\\' .;


GERMANDATE
        : DIGIT? DIGIT '.' DIGIT? DIGIT '.' (DIGIT DIGIT)? DIGIT DIGIT;
ISODATE : DIGIT DIGIT DIGIT DIGIT MINUS DIGIT DIGIT MINUS DIGIT DIGIT;

FLOAT   : (FFLOAT ~('j'|'J'|'i'|'I')) => FFLOAT;

INT     : (IINT ~('j'|'J'|'i'|'I')) => IINT;

IMAG    :   IINT ('j'|'J'|'i'|'I')
        |   FFLOAT ('j'|'J'|'i'|'I')
        ;

fragment
RWORD   : ('\\' | LETTERS) ('\\' | LETTERS | DIGITS | UNDERSCORE | HAT | LCURLY | RCURLY | MINUS)*
        ;

WORD    : RWORD
        | LESSTHAN RWORD GREATERTHAN
        ;

PUNCTUATION
        : '.' | ',' | ';';

LITERAL : '"' (ESC|~('\\'|'\n'|'"'))* '"'
        | '\'' (ESC|~('\\'|'\n'|'\''))* '\''
        ;

config
        : referenceSection commonSection* datadefSection dataSection
        -> ^(CONFIG referenceSection commonSection* datadefSection dataSection)
        ;

referenceSection
        : LBRACK ASTERISK 'reference' RBRACK NEWLINE commonitem+
        -> ^(COMMON_SECTION ^(HEADER ASTERISK 'reference') ^(BODY commonitem+));

datadefSection
        : LBRACK ASTERISK 'data definitions' RBRACK NEWLINE colitem+
        -> ^(DATADEF_SECTION ^(HEADER ASTERISK 'data definitions') ^(BODY colitem+));

dataSection
        : LBRACK ASTERISK 'data' RBRACK NEWLINE dataitem*
        -> ^(DATA_SECTION ^(HEADER ASTERISK 'data') ^(BODY dataitem*));

commonSection
        : LBRACK headername RBRACK NEWLINE commonitem+
        -> ^(COMMON_SECTION ^(HEADER headername) ^(BODY commonitem+));

headername
        : ~ASTERISK .*;

colitem : key COLON colspec NEWLINE -> ^(COLSPEC ^(LONGNAME key) colspec);
dataitem
        : cell+ NEWLINE -> ^(DATASET cell+);
commonitem
        : key COLON value NEWLINE   -> ^(ITEM ^(KEY key) value);

cell    :       number  -> ^(NUMBER number)
        |       WORD    -> ^(STRING WORD)
        |       LITERAL -> ^(STRING LITERAL)
        ;

colspec : identifier deps? (LBRACK unit RBRACK)? -> ^(IDENTIFIER identifier) ^(DEPS deps?) ^(UNIT unit?);

deps    : LPAREN identifier ( ',' identifier)* RPAREN -> identifier+;

key     : ~LBRACK .*;

value
options {
    backtrack=true;
    memoize=true;
}
        :       number                     -> ^(NUMBER number)
        |       identifier EQUALS quantity -> ^(VARIABLE ^(IDENTIFIER identifier) quantity)
        |       datetime                   -> datetime
        |       catchall                   -> ^(STRING catchall)
        ;

identifier: WORD;
/*
identifier
        : WORD ( UNDERSCORE ((LCURLY WORD RCURLY) | WORD | INT)
               | HAT ((LCURLY WORD RCURLY) | WORD | INT))?
        ;
*/

catchall
        : ~NEWLINE*;

datetime
        : date time? -> ^(DATETIME ^(DATE date) ^(TIME time?));

date    : GERMANDATE | ISODATE;

time    : INT COLON INT (COLON FLOAT)?;

number  : (NPLUS|NMINUS)? absnumber;

fragment
absnumber
options {
    backtrack=true;
}
        : FLOAT (NPLUS|NMINUS) IMAG
        | INT (NPLUS|NMINUS) IMAG
        | FLOAT
        | INT
        | IMAG
        ;

quantity
        : number unit? -> ^(QUANTITY ^(NUMBER number) ^(UNIT unit?));

unit    : WORD ((ASTERISK|DIV) WORD)*;
