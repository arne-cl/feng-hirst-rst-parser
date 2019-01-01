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


EXPECTED_PARSETREE_SHORT = """ParseTree(\'Contrast[S][N]\', ["_!Although they did n\'t like it ,!_", \'_!they accepted the offer . <P>!_\'])\n"""
EXPECTED_PARSETREE_LONG = """ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [ParseTree(\'same-unit[N][N]\', [ParseTree(\'Elaboration[N][S]\', [\'_!Henryk Szeryng!_\', \'_!( 22 September 1918 - 8 March 1988 )!_\']), \'_!was a violin virtuoso of Polish and Jewish heritage . <P>!_\']), ParseTree(\'Elaboration[N][S]\', [\'_!He was born in Zelazowa Wola , Poland . <s>!_\', ParseTree(\'Background[N][S]\', [ParseTree(\'Joint[N][N]\', [ParseTree(\'Background[N][S]\', [\'_!Henryk started piano and harmony training with his mother!_\', \'_!when he was 5 ,!_\']), ParseTree(\'Elaboration[N][S]\', [\'_!and at age 7 turned to the violin ,!_\', \'_!receiving instruction from Maurice Frenkel . <s>!_\'])]), ParseTree(\'same-unit[N][N]\', [ParseTree(\'Elaboration[N][S]\', [\'_!After studies with Carl Flesch in Berlin!_\', \'_!( 1929-32 ) ,!_\']), ParseTree(\'Evaluation[N][S]\', [ParseTree(\'Enablement[N][S]\', [\'_!he went to Paris!_\', \'_!to continue his training with Jacques Thibaud at the Conservatory ,!_\']), \'_!graduating with a premier prix in 1937 . <P>!_\'])])])])]), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [\'_!He made his solo debut in 1933!_\', \'_!playing the Brahms Violin Concerto . <s>!_\']), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Joint[N][N]\', [\'_!From 1933 to 1939 he studied composition in Paris with Nadia Boulanger ,!_\', ParseTree(\'same-unit[N][N]\', [ParseTree(\'Elaboration[N][S]\', [\'_!and during World War II he worked as an interpreter for the Polish government in exile!_\', \'_!( Szeryng was fluent in seven languages )!_\']), \'_!and gave concerts for Allied troops all over the world . <s>!_\'])]), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Enablement[N][S]\', [\'_!During one of these concerts in Mexico City he received an offer!_\', \'_!to take over the string department of the university there . <P>!_\']), ParseTree(\'Joint[N][N]\', [\'_!In 1946 , he became a naturalized citizen of Mexico . <P>!_\', ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Temporal[N][S]\', [\'_!Szeryng subsequently focused on teaching!_\', \'_!before resuming his concert career in 1954 . <s>!_\']), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Joint[N][N]\', [\'_!His debut in New York City brought him great acclaim ,!_\', \'_!and he toured widely for the rest of his life . <s>!_\']), \'_!He died in Kassel . <P>!_\'])])])])])]), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [\'_!Szeryng made a number of recordings ,!_\', \'_!including two of the complete sonatas and partitas for violin by Johann Sebastian Bach , and several of sonatas of Beethoven and Brahms with the pianist Arthur Rubinstein . <s>!_\']), ParseTree(\'Attribution[S][N]\', [\'_!He also composed ;!_\', \'_!his works include a number of violin concertos and pieces of chamber music . <P>!_\'])]), ParseTree(\'Elaboration[N][S]\', [ParseTree(\'Elaboration[N][S]\', [\'_!He owned the Del Gesu " Le Duc " , the Stradivarius " King David " as well as the Messiah Strad copy by Jean-Baptiste Vuillaume!_\', \'_!which he gave to Prince Rainier III of Monaco . <s>!_\']), ParseTree(\'Elaboration[N][S]\', [\'_!The " Le Duc " was the instrument!_\', ParseTree(\'Temporal[N][N]\', [\'_!on which he performed and recorded mostly ,!_\', ParseTree(\'same-unit[N][N]\', [ParseTree(\'same-unit[N][N]\', [ParseTree(\'Elaboration[N][S]\', [\'_!while the latter!_\', \'_!( " King David "!_\']), \'_!Strad )!_\']), \'_!was donated to the State of Israel . <P>!_\'])])])])])])])\n"""


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
