DEVELOPERS
~~~~~~~~~~~~~~~~~~~~
* Vanessa Wei Feng
  Department of Computer Science
  University of Toronto
  Canada
  mailto:weifeng@cs.toronto.edu


REFERENCES
~~~~~~~~~~~~~~~~~~~~~~
* Vanessa Wei Feng and Graeme Hirst, 2012. Text-level discourse parsing with rich linguistic features. In Proceedings of the 50th Annual Meeting of the Association for Computational Linguistics: Human Language Technologies (ACL-2012), Jeju, Korea. http://aclweb.org/anthology-new/P/P12/P12-1007.pdf

* David A. duVerle and Helmut Prendinger. 2009. A novel discourse parser based on Support Vector Machine classification. In Proceedings of the Joint Conference of the 47th Annual Meeting of the ACL and the 4th International Joint Conference on Natural Language Processing of the AFNLP (ACL 2009), pages 665¨C673, Stroudsburg, PA, USA. http://www.aclweb.org/anthology/P/P09/P09-1075.pdf


GENERAL INFOMRATION
~~~~~~~~~~~~~~~~~~~~~~
* This RST-style discourse parser produces discourse tree structure on full-text level. The program runs on Linux systems. It was originally coded in Python, and packed using PyInstaller (Official website: http://www.pyinstaller.org).

* The overall software work flow is based on the third-party HILDA discourse parser (duVerle and Prendinger, 2009). The EDU segmentation component in our software was kept unchanged from their discourse parser. The developers of HILDA discourse parser receive full credit for the overall work flow and the EDU segmentation component.

* The major contribution of this software includes: Revising the tree-building component by incorporating rich-linguistic features in the binary classifier "struct" and the multi-class classifier "label". For full information, please refer to the papers listed in the REFERENCES section.

* Note that in this version, we have not implemented our contextual-features as described in Feng and Hirst (2012). We plan to explore incorporating them in some post-processing procedures in future versions.


INSTALLING
~~~~~~~~~~~~~~~~~~~~~~
You need to install the following third-party software first:

* Install Python 2.7+, available at http://www.python.org/download/.

* Install Java (for executing Penn2Malt.jar and stanford-parser.jar), available at http://www.java.com/en/download/index.jsp.

* Compile the SVM scaling utility and classification tools for liblinear and libsvm. In order to do that:
1) Go to ./svm_tools and do a "gcc -o svm-scale svm-scale.c" to compile the scaling utility.
2) Go to ./svm_tools/liblinear and do a "make clean" then "make" to compile liblinear. 
3) Go to ./svm_tools/libsvm and do a "make clean" then "make" to compile libsvm. 

* Compile the svm_perf and svm_multiclass classifiers. In order to do that:
1) Go to ./svm_tools/svm_perf_stdin/ and do a "make clean" then "make" to compile all files.
2) Copy the svm_perf_classify file to the parent folder: "cp svm_perf_classify ../"
1) Go to ./svm_tools/svm_multiclass_stdin/ and do a "make clean" then "make" to compile all files.
2) Copy the svm_multiclass_classify file to the parent folder: "cp svm_multiclass_classify ../"

* The Stanford syntax parser and Penn2Malt package are already included in this package. However, please do not try to replace the provided packages with newer versions of those two software, since compatibility is not guaranteed in this case.

TROUBLESHOOTING
~~~~~~~~~~~~~~~~~~~~~~
* The binary distribution of our software should already include necessary modules of NLTK (Natural Language Toolkit for Python), so you do not have to install NLTK first. However, in case that you see errors like "no module named nltk" or others when running our software, you can try either of the following two possible workaround:

1. Package the source code on your own, by following the instructions below:
1) Install NLTK after install Python. NLTK is available at http://www.nltk.org/.
2) Install PyInstaller-2.0, which is available at http://www.pyinstaller.org.
3) Package the source codes in "src" folder using the following command (fill in the root path where you have extracted discourse_parse-1.0.tar.gz as <discourse_parse_root_path>):
   python pyinstaller.py -F -o <discourse_parse_root_path> <discourse_parse_root_path>/src/parse.py
4) Now you should have two folders, "build" and "dist", under discourse_parse_root_path, and the parser is ready for use.

2. Use the source codes directly:
1) Install NLTK after install Python. NLTK is available at http://www.nltk.org/.
2) Go to src/ folder and use the parser from there. By using this approach, you need to use the following command when running the parser:
   
   python parser.py [options] input_file/dir1 [input_file/dir2] ...

   Meanings of options and arguments are described in the section "USEING THE DISCOURSE PARSER" below.

* It seems that newer version of NLTK has a different interface for its tree objects. Our implementation was based on NLTK 2.0b9. So if you're experiencing with errors reported such as "'function' object has no attribute 'parent'", please either replace your NLTK version with 2.0b9, or go through the source codes under src/ folder, adding brackets to all *.parent, *.left_sibling, *.right_sibling, *.root, *.treepos, *.treepositions. (e.g., *.parent becomes *.parent())

USEING THE DISCOURSE PARSER
~~~~~~~~~~~~~~~~~~~~~~
Go to dist/ and execute the binary file "parse" with the following command format:

Usage: parse [options] input_file/dir1 [input_file/dir2] ...

Options:
  --version        show program's version number and exit
  -h, --help       show this help message and exit
  -o, --output     write the results to input_file.edus, input_file.tree (or
                   input_file.dis if use "-S" option)
  -s, --seg-only   perform segmentation only
  -v, --verbose    verbose mode
  -D, --directory  parse all .txt files in the given directory
  -S, --SGML       print discourse tree in SGML format
  -E, --Edus       use the edus given by the users (do not perform
                   segmentation). Given edus need to be stored in a file
                   called input_file.edus, with an EDU surrounded by
                   "<edu>" and "</edu>" tags per line.

Same as the HILDA discourse parser, our program takes as input a text file, one or several optional arguments, and optional options (note that the options are case-sensitive).

The following formatting must be used in the input text file: Each sentence ending must be marked with a "<s>" tag, and each paragraph ending by a "<p>" tag.

You could indicate the program to skip some processing components, e.g.,
(1) "-s": skip parsing component, and output segmented EDUs only.
(2) "-S": skip segmentation component, by using the EDUs provided in <input_file>.edus.

The output of the program contains:
(1) EDUs of the text, segmented using HILDA's segmentation component. These are output if and only if "-S" option is disabled and the <intput_file>.edus file is found.
(2) If not using "-s" option, then the parsed discourse tree is produced as well. The discourse tree is available in two formats: 
    (a) HILDA's format (default). The parse tree is stored in <input_file>.tree, if "-o" option os enabled.
    (b) SGML format, i.e., the one used in the RST discourse treebank (Carlson et al., 2001), by using "-S" option. The parse tree is stored in <input_file>.dis, if "-o" option os enabled.

Several examples of correctly-formatted texts can be found in the "examples" directory.

Some examples of program usage:

(1) "parse -o examples/wsj_0602.txt" (Parses the text, writes the EDUs and HILDA-style tree to examples/wsj_0602.txt.edus, examples/wsj_0602.txt.tree)
(2) "parse -o -S examples/wsj_0602.txt" (Parses the text, writes the EDUs and RST-DT-style tree to examples/wsj_0602.txt.edus, examples/wsj_0602.txt.dis)
(3) "parse -o -E examples/AFP_ENG_20030304.0250.txt" (Parses the text, using the EDUs specified in examples/AFP_ENG_20030304.0250.txt.user_edus, writes the HILDA-style tree to examples/AFP_ENG_20030304.0250.txt.tree)


BUGS AND COMMENTS
~~~~~~~~~~~~~~~~~~~~~~

If you encounter and bugs using the program, please report the exception thrown by the program and the specific text file(s) you used for parsing, to weifeng@cs.toronto.edu. General comments about the program and the results are also welcome!