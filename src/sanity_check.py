'''
Created on Jul 30, 2014

@author: Vanessa
'''
import paths
import os.path
import subprocess
from prep.syntax_parser import SyntaxParser
from classifiers.crf_classifier import CRFClassifier
import traceback


test_filename = '../texts/wsj_0607.out'

def check_ssplit():
    cmd = 'perl %s/boundary.pl -d %s/HONORIFICS -i %s' % (paths.SSPLITTER_PATH, paths.SSPLITTER_PATH, os.path.abspath(test_filename))
#        print cmd
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
    output, errdata = p.communicate()

    if len(errdata) == 0:
        paras = output.strip().split('\n\n')
        sents = []
        for (i, para) in enumerate(paras):
            #print 'Paragraph #%d' % (i + 1)
            para_sents = para.split('\n')
            '''for sent in para_sents:
                print sent
            print'''
            
            sents.extend(para_sents)
        
        print "Successfully split the test file into %d paragraphs and %d sentences." % (len(paras), len(sents))
        
        return sents
    else:
        raise NameError("*** Sentence splitter crashed, with trace %s..." % errdata)
    

def check_syntax_parser(sents):
    syntax_parser = None
    try:
        syntax_parser = SyntaxParser()
    except Exception, e:
        print "*** Loading Stanford parser failed..."
        raise e
    
    for (i, sent) in enumerate(sents):
        try:
            syntax_parser.parse_sentence(sent)
            #print 'Parsing sentence %d successful' % (i + 1)
        except Exception, e:
            raise NameError("*** Parsing sentence %d failed" % (i + 1))

    if syntax_parser:
        syntax_parser.unload()
 


def check_CRFSuite():
    crfsuite_test_file = os.path.join(paths.CRFSUITE_PATH, 'test.txt')
    vectors = open(crfsuite_test_file).read().strip().split('\n')
    for (model_name, model_type, model_path, model_file) in [('segmentation', 'segmenter', paths.SEGMENTER_MODEL_PATH, 'seg.crfsuite'),
                                     ('segmentation 2nd pass', 'segmenter', paths.SEGMENTER_MODEL_PATH, 'seg_global_features.crfsuite'),
                                     ('treebuilding intra-sentnetial structure', 'treebuilder', paths.TREE_BUILD_MODEL_PATH, 'struct/intra.crfsuite'),
                                     ('treebuilding multi-sentnetial structure', 'treebuilder', paths.TREE_BUILD_MODEL_PATH, 'struct/multi.crfsuite'),
                                     ('treebuilding intra-sentnetial relation', 'treebuilder', paths.TREE_BUILD_MODEL_PATH, 'label/intra.crfsuite'),
                                     ('treebuilding multi-sentnetial relation', 'treebuilder', paths.TREE_BUILD_MODEL_PATH, 'label/multi.crfsuite')]:
        try:
            print '*** Loading classifier %s...' % model_name
            classifier = CRFClassifier(model_name, model_type, model_path, model_file, False)
            classifier.classify(vectors)
            classifier.unload()
        except Exception, e:
            raise e
                            

    
    
import sys

if __name__ == '__main__':
    c_ssplit = True
    c_ssparse = True
    c_crfsuite = True
    
    steps = 1
    if c_ssplit or c_ssparse:
        print '********** Step %d: Now checking sentence splitting module...' % steps
        try:
            sents = check_ssplit()
            print
            steps += 1
        except Exception, e:
            traceback.print_exc()
            sys.exit(1)

    if c_ssparse:
        print '********** Step %d: Now checking syntactic parsing module...' % steps
        try:
            check_syntax_parser(sents)
            print
            steps += 1
        except Exception, e:
            traceback.print_exc()
            sys.exit(1)
        
    if c_crfsuite:
        print '********** Step %d: Now checking CRFSuite classification module...' % steps
        try:
            check_CRFSuite()
            print
            steps += 1
        except Exception, e:
            traceback.print_exc()
            sys.exit(1)