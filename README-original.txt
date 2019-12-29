DEVELOPERS
~~~~~~~~~~~~~~~~~~~~
* Vanessa Wei Feng
  Department of Computer Science
  University of Toronto
  Canada
  mailto:weifeng@cs.toronto.edu



REFERENCES
~~~~~~~~~~~~~~~~~~~~~~
* Vanessa Wei Feng and Graeme Hirst, 2014. Two-pass Discourse Segmentation with Pairing and Global Features. arXiv:1407.8215v1. http://arxiv.org/abs/1407.8215

* Vanessa Wei Feng and Graeme Hirst, 2014. A Linear-Time Bottom-Up Discourse Parser with Constraints and Post-Editing. In Proceedings of the 52th Annual Meeting of the Association for Computational Linguistics: Human Language Technologies (ACL-2014), Baltimore, USA. http://aclweb.org/anthology/P14-1048



GENERAL INFOMRATION
~~~~~~~~~~~~~~~~~~~~~~
* This RST-style discourse parser produces discourse tree structure on full-text level, given a raw text. No prior sentence splitting or any sort of preprocessing is expected. The program runs on Linux systems.

* The overall software work flow is similar to the one described in our paper (ACL 2014). However, to guarantee further efficiency, we remove the post-editing component from the workflow, and remove the set of entity-based transaction features from our feature set. Moreover, both structure and relation classification models are now implemented using CRFSuite.



DEPENDENCIES
~~~~~~~~~~~~~~~~~~~~~~
You need to install the following third-party software first:

In order to run the software, you need to have the following components:
1. Python 2.7.
2. NLTK 2.0b9 (newer versions will not work because of the different interfaces in the tree modules).
3. Java
4. gcc
5. Perl

* The Stanford syntax parser is already included in this package. However, please do not try to replace the provided package with newer versions, since compatibility is not guaranteed in this case.



SETUP CRFSUITE
~~~~~~~~~~~~~~~~~~~~~~
The $gCRF_ROOT$ symbol in the commands below stands for the root directory of gCRF.

1. Test if the binary file of CRFsuite-stdin is ready for use, by executing the following two commands:
cd $gCRF_ROOT$/tools/crfsuite/
crfsuite-stdin tag -pi -m ../../model/tree_build_set_CRF/label/intra.crfsuite test.txt

If the following lines are printed, then the binary is usable on your platform, and thus you can skip the next step and go to the USAGE section:
@probability    0.003834
LEAF:0.063409
Elaboration[N][S]:0.958434
LEAF:0.060318

2. If the test in the Step 1 fails, you need to build the binary from source codes. To do so, you need to do the following three things:
a. Build LibLBFGS
   cd $gCRF_ROOT$/tools/crfsuite/liblbfgs-1.10
   ./configure --prefix=$HOME/local
   make
   make install

b. Build CRFsuite-stdin
   cd $gCRF_ROOT$/tools/crfsuite/crfsuite-0.12
   ./configure --prefix=$HOME/local --with-liblbfgs=$HOME/local
   make
   make install

c. Copy the crfsuite binary under $HOME/local/bin to tools/crfsuite and rename it as crfsuite-stdin
   cp $HOME/local/bin/crfsuite $gCRF_ROOT$/tools/crfsuite/crfsuite-stdin
   chmod +x ../crfsuite-stdin

Now repeat the test in Step 1 and see if it works now.



SOFTWARE USAGE
~~~~~~~~~~~~~~~~~~~~~~
Usage: parse.py [options] input_file/filelist

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -v, --verbose         verbose mode
  -s, --skip_parsing    Skip parsing, i.e., conduct segmentation only.
  -D, --filelist        parse all files specified in the filelist file, one
                        file per line.
  -t, --output_dir      Specify a directory for output files.
  -g, --global_features
                        Perform a second pass of EDU segmentation using global
                        features.
  -l, --logging         Perform logging while parsing.
  -e, --save            Save preprocessed document into serialized file for
                        future use.

     1) To produce the discourse parse tree for a single file, do the following:
         python parse.py -t test ../texts/wsj_0607.out

         If you omit the -t option, the result will be written to "$gCRF_ROOT$/texts/results", otherwise, it will create a sub-folder under "$gCRF_ROOT$/texts/results". So for the command above, the result "wsj_0607.out.tree" will appear in "$gCRF_ROOT$/texts/results/test/".

     2) To produce discourse parse trees for a batch of files, do the following, where filelist is the name of the file where you store the absolute path of each file that you wish to process (one file per line):
         python parse.py -tD test_batch filelist

	 And the results will appear in "$gCRF_ROOT$/texts/results/test_batch/".

     3) To enable two-pass segmentation (see our arXiv paper), use the -g option, in conjunction with other options (if any). However, enabling this option would largely slow the segmentation, but with higher segmentation accuracy.


     4) To enable logging while processing texts, use the -l option. In this way, the time spent on preprocessing, segmentation, and parsing will be recorded individually.
         For example, for the sample text, its log will look like the following:
         ***** Parsing ../texts/wsj_0607.out...
         Finished preprocessing in 2.99 seconds.
         Finished segmentation in 1.07 seconds. Segmented into 15 EDUs.
         Finished tree building in 0.52 seconds.
         ===================================================

     5) You may save a (partially) processed document to as a binary file, by using the -e option. This is particularly useful for processing large documents, as you might not want to repeat the preprocessing part (i.e., syntactic parsing, etc.), but wish to explore some different parsing configurations. There are three places where the serialized data will be saved: after preprocessing, after segmentation, and after discourse parsing.



TROUBLESHOOTING
~~~~~~~~~~~~~~~~~~~~~~
* It seems that newer version of NLTK has a different interface for its tree objects. Our implementation was based on NLTK 2.0b9. So if you're experiencing with errors reported such as "'function' object has no attribute 'parent'", please either replace your NLTK version with 2.0b9, or go through the source codes under src/ folder, adding brackets to all *.parent, *.left_sibling, *.right_sibling, *.root, *.treepos, *.treepositions. (e.g., *.parent becomes *.parent())

* We have included a script, santiy_check.py, to test a few key dependent components (CCGSsplitter, Stanford parser, and CRFSuite) of the tool. You may run the script for a quick diagnosis.



BUGS AND COMMENTS
~~~~~~~~~~~~~~~~~~~~~~
If you encounter and bugs using the program, please report the exception thrown by the program and the specific text file(s) you used for parsing, to weifeng@cs.toronto.edu. General comments about the program and the results are also welcome!