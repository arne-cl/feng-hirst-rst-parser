'''
Created on Feb 19, 2013

@author: Vanessa Wei Feng
'''
from nltk.tree import *

from string import *
import re
from yappsrt import *

class TreebankScanner(Scanner):
    patterns = [
        ('r"\\)"', re.compile('\\)')),
        ('r"\\("', re.compile('\\(')),
        ('"_!"', re.compile('_!')),
        ('\\s+', re.compile('\\s+')),
        ('//TT_ERR', re.compile('//TT_ERR')),
        ('NUM', re.compile('[0-9]+')),
        ('ID', re.compile('[-+*/!@$%^&=.a-zA-Z0-9]+')),
        ('STR', re.compile('(.)+_!')),
    ]
    def __init__(self, str):
        Scanner.__init__(self,None,['\\s+', '//TT_ERR'],str)

class Treebank(Parser):
    def expr(self):
        _token_ = self._peek('"_!"', 'ID', 'NUM', 'r"\\("')
        if _token_ == '"_!"':
            self._scan('"_!"')
            STR = self._scan('STR')
            return STR[0:-2]
        elif _token_ == 'ID':
            ID = self._scan('ID')
            return ID
        elif _token_ == 'NUM':
            NUM = self._scan('NUM')
            return atoi(NUM)
        else:# == 'r"\\("'
            self._scan('r"\\("')
            ID = self._scan('ID')
            e = []
            while self._peek('r"\\)"', '"_!"', 'ID', 'NUM', 'r"\\("') != 'r"\\)"':
                expr = self.expr()
                e.append(expr)
            self._scan('r"\\)"')
            return ParentedTree(ID, e)


def parse(rule, text):
    P = Treebank(TreebankScanner(text))
    return wrap_error_reporter(P, rule)


def parse(text):
    P = Treebank(TreebankScanner(text))
    return wrap_error_reporter(P, 'expr')

if __name__=='__main__':
    print 'Testing'
    f = open('./texts/wsj_0613.out.dis')
    str = f.read()
    P = parse(str)
    for subtree in P.subtrees():
        print subtree
        print
    print 'Bye.'

