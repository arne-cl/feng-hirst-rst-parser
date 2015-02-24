'''
Created on 2013-02-17

@author: Wei
'''
from prep.syntax_parser import SyntaxParser
from segmentation.segmenter import Segmenter
from treebuilder.build_tree import TreeBuilder
from treebuilder.build_tree_greedy import GreedyTreeBuilder
from optparse import OptionParser

import paths
import os.path
import sys
import utils.utils
import re
import time
import nltk
import traceback
import utils.rst_lib
import subprocess
import utils.serialize
from trees.parse_tree import ParseTree
import math
import utils.rst_lib
from datetime import datetime

class DiscourseParser():
    def __init__(self, verbose, seg, output, SGML, edus, feature_sets = 'FengHirst'):
        ''' This is Hilda's segmentation module '''
        self.segmenter = None
        self.verbose = verbose
        self.seg = seg
        self.output = output
        self.SGML = SGML
        self.edus = edus
        self.dependencies = True
        self.max_iters = 0
        self.feature_sets = feature_sets

        initStart = time.time()
        try:
            self.segmenter = Segmenter(_model_path = os.path.join(paths.SEG_MODEL_PATH), _model_file = "training.scaled.model", _scale_model_file = "bin_scale",
                                        _name = "segmenter",
                                       verbose = self.verbose, dependencies = self.dependencies)
            
        except Exception, e:
            print "*** Loading Segmentation module failed..."
        
            if not self.segmenter is None:
                self.segmenter.unload()
            raise
        
        self.treebuilder = None
        try:
            if self.feature_sets == 'FengHirst':
                self.treebuilder = GreedyTreeBuilder(_model_path = paths.TREE_BUILD_MODEL_PATH,
                                                     _bin_model_file = ['struct/FengHirst/within_no_context.svmperf', 
                                                                        'struct/FengHirst/above_no_context.svmperf'],
                                                     _bin_scale_model_file = None,
                                                     _mc_model_file = ['label/FengHirst/within_label_nuclearity_no_context.multiclass', 
                                                                       'label/FengHirst/above_label_nuclearity_no_context.multiclass'],
                                                     _mc_scale_model_file = None, 
                                                     _name = "FengHirst", verbose = self.verbose, use_contextual_features = False) 
                    
                
#            else:
#                self.treebuilder = TreeBuilder(_model_path = paths.INIT_TREE_BUILD_MODEL_PATH,
#                                               _bin_model_file = 'struct/hilda/liblinear_bin_model.dat', _bin_scale_model_file = 'struct/hilda/bin_scale',
#                                               _mc_model_file = 'label/hilda/libsvm_rbf_mc_model.dat', _mc_scale_model_file = 'label/hilda/mc_scale', 
#                                               _name = "hilda", verbose = self.verbose, use_contextual_features = False) 

            


        except Exception, e:
            print "*** Loading Tree-building module failed..."
            print traceback.print_exc()
            
            if not self.treebuilder is None:
                self.treebuilder.unload()
            raise

        initEnd = time.time()
        print 'finished initialization in %.2f seconds' % (initEnd - initStart)        
    
        
    def unload(self):
        if not self.segmenter is None:
            self.segmenter.unload()
        
        if not self.treebuilder is None:
            self.treebuilder.unload()
    
    def parse(self, filename):
        if not os.path.exists(filename):
            print '%s does not exist.' % filename
            return
        
        print 'parsing %s' % filename
                
        try:      
            segStart = time.time()
            text = open(filename).read()
            
            formatted_text = ''
            sentences = []
            for para_text in text.split('<p>'):
                sents = para_text.strip().split('<s>')
                formatted_text += ' '.join(sents) + '\n\n'
                sentences.extend(sents)
            
            edus = None
            
            if self.edus:
                if not os.path.exists(filename + '.edus'):
                    print 'User specified EDU file ' + filename + '.edus' + ' no found!'
                    print 'Ignore "-E" option and conduct segmentation'
                    self.edus = False
                else :
                    fin = open(filename + '.edus')
                    edus = []
                    for line in fin:
                        line = line.strip()
                        if line != '':
                            line = re.sub('\</??edu\>', '', line)
                            edus.append(' '.join(nltk.word_tokenize(line)))
                    fin.close()
                
#                for edu in edus:
#                    print edu
            
            
            ''' Step 1: segment the each sentence into EDUs '''

            (trees, deps, cuts, edus) = self.segmenter.do_segment(text, edus)
            
            #for tree in trees:
                #print tree.pprint()

            escaped_edus = self.segmenter.get_escaped_edus(trees, cuts, edus)
#            print cuts

            if options.verbose:
                for e in edus:
                    print e
            
            print 'finished segmentation, segmented into %d EDUs' % len(edus)
            
            if self.output and not self.edus:
                print 'output segmentation result to %s.edus' % filename
                
                f_o = open(filename + ".edus", "w")
                for e in escaped_edus:
                    f_o.write("<edu>%s</edu>\n" % e)
                f_o.close()
            '''else:
                for e in escaped_edus:
                    print "<edu>%s</edu>" % e'''

            segEnd = time.time()
            
            print 'finished segmentation in %.2f seconds' % (segEnd - segStart)
            
                
        except Exception, e:
            print "*** Segmentation failed ***"
            print traceback.print_exc()

            if not self.segmenter is None:
                self.segmenter.unload()
                
            if not self.treebuilder is None:
                self.treebuilder.unload()
               
            raise
        try:    
            if not self.seg:
                ''' Step 2: build text-level discourse tree '''
                treeBuildStart = time.time()
                
                outfname = filename + ".%s" % ("tree" if not self.SGML else "dis")
                parse_trees = self.treebuilder.build_tree((trees, deps, cuts, edus), "pouet", paths.MODEL_PATH)
                        
                print 'finished tree building'
#                        print parse_trees[0]
#                        print
                if parse_trees == []:
                    print "No tree could be built..."
                        
                    if not self.treebuilder is None:
                        self.treebuilder.unload()

                    return -1
                                 
#               Unescape the parse tree
                if parse_trees and len(parse_trees):
                    pt = parse_trees[0]
                    
                    #pt_edges = utils.utils.transform_to_ZhangShasha_tree(pt)
                    #pts.append(pt_edges)
                    for i in range(len(escaped_edus)):
                        #print i, escaped_edus[i], pt.leaves()[i]
                        pt.__setitem__(pt.leaf_treeposition(i), '_!%s!_' % escaped_edus[i])
        
                    #print pt.pprint()
                    out = pt.pprint() if not self.SGML else utils.utils.print_SGML_tree(pt)
                    
                    print 'output tree building result to %s' % outfname
                    f_o = open(outfname, "w")
                    f_o.write(out)
                    f_o.close()
                    
                    treeBuildEnd = time.time()
                    
                    print 'finished tree building in %.2f seconds' % (treeBuildEnd - treeBuildStart)     


        except Exception, e:
            print traceback.print_exc()
            
            if not self.treebuilder is None:
                self.treebuilder.unload()

            raise

        print '==================================================='
        #return dists#, probs
        
v = '1.0'
if __name__ == '__main__':
    usage = "usage: %prog [options] input_file/dir1 [input_file/dir2] ..."

    optParser = OptionParser(usage=usage, version="%prog " + v)
    
    optParser.add_option("-o", "--output", dest="output", action = "store_true",
                      help="write the results to input_file.edus, input_file.tree (or input_file.dis if use \"-S\" option)", 
              default=False)
    optParser.add_option("-s", "--seg-only",
                      action="store_true", dest="seg", default=False,
                      help="perform segmentation only")
    optParser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="verbose mode")
    optParser.add_option("-D", "--directory",
                      action="store_true", dest="directory", default=False,
                      help="parse all .txt files in the given directory")
    optParser.add_option("-S", "--SGML",
                      action="store_true", dest="SGML", default=False,
                      help="print discourse tree in SGML format")
    optParser.add_option("-E", "--Edus",
                         action="store_true", dest="edus", default=False,
                         help="use the edus given by the users (do not perform segmentation). " +\
             "Given edus need to be stored in a file called input_file.edus, with " +\
             "an EDU surrounded by \"<edu>\" and \"</edu>\" tags per line.")
    
    
    (options, args) = optParser.parse_args()

    parser = None
    try:
        if len(args) == 0:
            print usage
            sys.exit(1)
        
        parser = DiscourseParser(verbose = options.verbose, seg = options.seg, output = options.output, SGML = options.SGML, edus = options.edus)
        
        if options.directory:
            for subdir in args:
                for fname in os.listdir(subdir):
                    if fname.endswith('.out'):
                        '''if options.SGML and os.path.exists(os.path.join(subdir, fname + '.dis')):
                            continue
                        
                        if not options.SGML and os.path.exists(os.path.join(subdir, fname + '.tree')):
                            continue'''
                        
                        outfname = fname + ".%s" % ("tree" if not parser.SGML else "dis")
                        if not os.path.exists(os.path.join(subdir, outfname)):
                        #if True:
                            parser.parse(os.path.join(subdir, fname))                
        else:
            for fname in args:
                #print reference_fname
                #(dists, probs) = parser.parse(fname, reference_fname)
                outfname = fname + ".%s" % ("tree" if not parser.SGML else "dis")
                #if not os.path.exists(outfname):
                if True:
                    dists = parser.parse(fname)
                
        parser.unload()
        
    except Exception, e:
        print traceback.print_exc()
        if not parser is None:
            parser.unload()

