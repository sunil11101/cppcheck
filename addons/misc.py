#!/usr/bin/env python
#
# Misc: Uncategorized checks that might be moved to some better addon later
#
# Example usage of this addon (scan a sourcefile main.cpp)
# cppcheck --dump main.cpp
# python misc.py main.cpp.dump

import cppcheckdata
import sys
import re

VERIFY = ('-verify' in sys.argv)
VERIFY_EXPECTED = []
VERIFY_ACTUAL = []

def reportError(token, severity, msg, id):
    if VERIFY:
        VERIFY_ACTUAL.append(str(token.linenr) + ':' + id)
    else:
        sys.stderr.write(
            '[' + token.file + ':' + str(token.linenr) + '] (' + severity + '): ' + msg + ' [' + id + ']\n')

def simpleMatch(token, pattern):
    for p in pattern.split(' '):
        if not token or token.str != p:
            return False
        token = token.next
    return True

def isStringLiteral(tokenString):
    return tokenString.startswith('"')

# check data
def check(data):
    arrayInit = False
    rawTokens = data.rawTokens
    for i in range(len(rawTokens)):
        if i < 2:
            continue
        tok1 = rawTokens[i-2].str
        tok2 = rawTokens[i-1].str
        tok3 = rawTokens[i-0].str
        if tok3 == '}':
            arrayInit = False
        elif tok1 == ']' and tok2 == '=' and tok3 == '{':
            arrayInit = True
        elif arrayInit and (tok1 in [',', '{']) and isStringLiteral(tok2) and isStringLiteral(tok3):
            if tok1 == '{':
                i2 = i + 1
                while i2 < len(rawTokens) and rawTokens[i2].str not in [',', '}']:
                    i2 = i2 + 1
                if i2 >= len(rawTokens) or rawTokens[i2].str != ',':
                    continue
            if i + 2 < len(rawTokens) and isStringLiteral(rawTokens[i+1].str) and isStringLiteral(rawTokens[i+2].str):
                continue
            reportError(rawTokens[i], 'style', 'string concatenation', 'stringConcatInArrayInit')

for arg in sys.argv[1:]:
    if arg == '-verify':
        continue
    print('Checking ' + arg + '...')
    data = cppcheckdata.parsedump(arg)

    if VERIFY:
        VERIFY_ACTUAL = []
        VERIFY_EXPECTED = []
        for tok in data.rawTokens:
            if tok.str.startswith('//'):
                for word in tok.str[2:].split(' '):
                    if word == 'stringConcatInArrayInit':
                        VERIFY_EXPECTED.append(str(tok.linenr) + ':' + word)

    check(data)

    if VERIFY:
        for expected in VERIFY_EXPECTED:
            if expected not in VERIFY_ACTUAL:
                print('Expected but not seen: ' + expected)
                sys.exit(1)
        for actual in VERIFY_ACTUAL:
            if actual not in VERIFY_EXPECTED:
                print('Not expected: ' + actual)
                sys.exit(1)
