#!/usr/bin/env python2.7

"""
Simple wrapper around the Feng-Hirst parser, used as an entry point for
a Docker container.

In contrast to parse.py, this script only accepts one input file.
Since parse.py is quite chatty, it's stdout will be suppressed and stored
in a file. If the parser doesn't produce a parse, this file will
be printed to stderr.
"""

import os
import sys

from nltk.tree import ParentedTree
from parse import parse_args
from parse import main as feng_main


class ParserException(Exception):
    pass

def get_parser_stdout(parser_stdout_filepath):
    """Returns the re-routed STDOUT of the Feng/Hirst parser."""
    sys.stdout.close()
    stdout_file = open(parser_stdout_filepath)
    stdout_str = stdout_file.read()
    stdout_file.close()
    sys.stdout = open(parser_stdout_filepath, "w")
    return stdout_str

def get_output_filepath(args):
    """Returns the path to the output file of the parser."""
    input_filepath = args[0]
    input_filename = os.path.basename(input_filepath)
    return os.path.join("../texts/results", "{}.tree".format(input_filename))

def main():
    parser_stdout_filepath = 'parser.stdout'

    options, args = parse_args()
    if len(args) != 1:
        sys.stderr.write("Please provide (only) one file to parse.")
        sys.exit(1)

    output_filepath = get_output_filepath(args)
    if os.path.isfile(output_filepath):
        # You can't parse a file with the same name twice, unless you
        # remove the parser output file first.
        os.remove(output_filepath)

    # re-route the print/stdout output of the parser to a file
    old_stdout = sys.stdout
    sys.stdout = open(parser_stdout_filepath, "w")
    try:
        results = feng_main(options, args)
        assert len(results) == 1 and isinstance(results[0], ParentedTree), \
            ("Expected one parse tree as a result, but got: {0}.\n"
             "Parser STDOUT was:\n{1}").format(
                results, get_parser_stdout(parser_stdout_filepath))
    finally:
        sys.stdout.close()
        sys.stdout = old_stdout

    parse_tree = results[0].__repr__() + "\n"
    sys.stdout.write(parse_tree)
    return parse_tree


if __name__ == "__main__":
    main()
