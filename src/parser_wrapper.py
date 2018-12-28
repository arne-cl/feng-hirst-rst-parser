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
from parse import parse_args, main


class ParserException(Exception):
    pass


if __name__ == "__main__":
    parser_stdout_filepath = 'parser.stdout'

    options, args = parse_args()
    if len(args) != 1:
        sys.stderr.write("Please provide (only) one file to parse.")
        sys.exit(1)

    # re-route the print/stdout output of the parser to a file
    old_stdout = sys.stdout
    sys.stdout = open(parser_stdout_filepath, "w")
    try:
        main(options, args)
    finally:
        sys.stdout.close()
        sys.stdout = old_stdout

    input_filepath = args[0]
    input_filename = os.path.basename(input_filepath)
    output_filepath = os.path.join("../texts/results", "{}.tree".format(input_filename))

    if not os.path.isfile(output_filepath):
        with open(parser_stdout_filepath) as parser_stdout:
            raise ParserException, parser_stdout.read()

    with open(output_filepath) as outfile:
        output_str = outfile.read() + "\n"
        sys.stdout.write(output_str)
        os.remove(output_filepath)
