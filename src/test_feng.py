#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Author: Arne Neumann <nlpbox.programming@arne.cl>

"""
Tests for the Feng/Hirst RST parser and our preprocessor/wrapper
parser_wrapper.py.
"""

import sys
import pytest
from parser_wrapper import main as wrapper_main


EXPECTED_PARSETREE_SHORT = """ParseTree(\'Contrast[S][N]\', ["Although they did n\'t like it ,", \'they accepted the offer .\'])\n"""
EXPECTED_PARSETREE_LONG = """ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [ParseTree(\'same-unit[N][N]\', [ParseTree(\'Elaboration[N][S]\', [\'Henryk Szeryng\', \'( 22 September 1918 - 8 March 1988 )\']), \'was a violin virtuoso of Polish and Jewish heritage .\']), ParseTree(\'Elaboration[N][S]\', [\'He was born in Zelazowa Wola , Poland .\', ParseTree(\'Background[N][S]\', [ParseTree(\'Joint[N][N]\', [ParseTree(\'Background[N][S]\', [\'Henryk started piano and harmony training with his mother\', \'when he was 5 ,\']), ParseTree(\'Elaboration[N][S]\', [\'and at age 7 turned to the violin ,\', \'receiving instruction from Maurice Frenkel .\'])]), ParseTree(\'same-unit[N][N]\', [ParseTree(\'Elaboration[N][S]\', [\'After studies with Carl Flesch in Berlin\', \'( 1929-32 ) ,\']), ParseTree(\'Evaluation[N][S]\', [ParseTree(\'Enablement[N][S]\', [\'he went to Paris\', \'to continue his training with Jacques Thibaud at the Conservatory ,\']), \'graduating with a premier prix in 1937 .\'])])])])]), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [\'He made his solo debut in 1933\', \'playing the Brahms Violin Concerto .\']), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Joint[N][N]\', [\'From 1933 to 1939 he studied composition in Paris with Nadia Boulanger ,\', ParseTree(\'same-unit[N][N]\', [ParseTree(\'Elaboration[N][S]\', [\'and during World War II he worked as an interpreter for the Polish government in exile\', \'( Szeryng was fluent in seven languages )\']), \'and gave concerts for Allied troops all over the world .\'])]), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Enablement[N][S]\', [\'During one of these concerts in Mexico City he received an offer\', \'to take over the string department of the university there .\']), ParseTree(\'Joint[N][N]\', [\'In 1946 , he became a naturalized citizen of Mexico .\', ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Temporal[N][S]\', [\'Szeryng subsequently focused on teaching\', \'before resuming his concert career in 1954 .\']), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Joint[N][N]\', [\'His debut in New York City brought him great acclaim ,\', \'and he toured widely for the rest of his life .\']), \'He died in Kassel .\'])])])])])]), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [\'Szeryng made a number of recordings ,\', \'including two of the complete sonatas and partitas for violin by Johann Sebastian Bach , and several of sonatas of Beethoven and Brahms with the pianist Arthur Rubinstein .\']), ParseTree(\'Attribution[S][N]\', [\'He also composed ;\', \'his works include a number of violin concertos and pieces of chamber music .\'])]), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [\'He owned the Del Gesu " Le Duc " , the Stradivarius " King David " as well as the Messiah Strad copy by Jean-Baptiste Vuillaume\', \'which he gave to Prince Rainier III of Monaco .\']), ParseTree(\'Elaboration[N][S]\', [\'The " Le Duc " was the instrument\', ParseTree(\'Temporal[N][N]\', [\'on which he performed and recorded mostly ,\', ParseTree(\'same-unit[N][N]\', [ParseTree(\'same-unit[N][N]\', [ParseTree(\'Elaboration[N][S]\', [\'while the latter\', \'( " King David "\']), \'Strad )\']), \'was donated to the State of Israel .\'])])])])])])])\n"""


def parse_file(filepath):
    sys.argv = ['parser_wrapper.py', filepath]
    return wrapper_main()


def test_feng_short():
    """The Feng/Hirst parser produces the expected output."""
    result = parse_file('../texts/input_short.txt')
    assert result == EXPECTED_PARSETREE_SHORT

def test_feng_long():
    """The Feng/Hirst parser produces the expected output."""
    result = parse_file('../texts/input_long.txt')
    assert result == EXPECTED_PARSETREE_LONG

def test_feng_fail():
    """The Feng/Hirst parser fails on non-existing input file."""
    with pytest.raises(Exception) as excinfo:
        result = parse_file('does_not_exist.txt')
    assert "Expected one parse tree as a result, but got: []" in excinfo.value.args[0]
