// step 9,10
grammar MiniDecaf;

import CommonLex;

prog
    : externalDecl+ EOF
    ;

externalDecl
    : func # funcExternalDecl
    | decl ';' # declExternalDecl
    ;

func
    : ty Ident '(' paramList ')' block # funcDef
    | ty Ident '(' paramList ')' ';' # funcDecl
    ;

ty
    : 'int' # intType
    | ty '*' # ptrType
    ;

stmt
    : 'return' expr ';' # returnStmt
    | expr ';' # exprStmt
    | ';' # nullStmt
    | 'if' '(' expr ')' th=stmt ('else' el=stmt)? # IfStmt
    | block # blockStmt
    | 'for' '(' init=decl ';' ctrl=expr? ';' post=expr? ')' stmt # forDeclStmt
    | 'for' '(' init=expr? ';' ctrl=expr? ';' post=expr? ')' stmt # forStmt
    | 'while' '(' expr ')' stmt # whileStmt
    | 'do' stmt 'while' '(' expr ')' ';' # doWhileStmt
    | 'break' ';' # breakStmt
    | 'continue' ';' # continueStmt
    ;

expr
    : asgn
    ;

decl
    : ty Ident ('[' Integer ']')* ('=' expr)?
    ;

blockItem
    : stmt # blockItemStmt
    | decl ';' # blockItemDecl
    ;

block
    : '{' blockItem* '}'
    ;

paramList
    : (decl (',' decl)*)?
    ;

asgn
    : cond # tAsgn
    | unary asgnOp asgn # cAsgn
    ;

cond
    : lor # tCond
    | lor '?' expr ':' cond # cCond
    ;

lor
    : land # tLor
    | lor '||' land # cLor
    ;

land
    : eq # tLand
    | land '&&' eq # cLand
    ;

eq
    : rel # tEq
    | eq eqOp rel # cEq
    ;

rel
    : add # tRel
    | rel relOp add # cRel
    ;

add
    : mul # tAdd
    | add addOp mul # cAdd
    ;

mul
    : cast # tMul
    | mul mulOp cast # cMul
    ;

cast
    : unary # tCast
    | '(' ty ')' cast # cCast
    ;

unary
    : postfix # tUnary
    | unaryOp cast # cUnary
    ;

postfix
    : atom # tPostfix
    | postfix '[' expr ']' # postfixArray
    | Ident '(' argList ')' # postfixCall
    ;

atom
    : Integer # atomInteger
    | Ident # atomIdent
    | '(' expr ')' # atomParen
    ;

argList
    : (expr (',' expr)*)?
    ;


unaryOp
    : '-' | '!' | '~' | '*' | '&'
    ;

addOp
    : '+' | '-'
    ;

mulOp
    : '*' | '/' | '%'
    ;

relOp
    : '<' | '>' | '<=' | '>='
    ;

eqOp
    : '==' | '!='
    ;

asgnOp
    : '='
    ;

