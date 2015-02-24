'''
Created on 2014-01-17

@author: Vanessa Wei Feng
'''

from segmenters.crf_segmenter import CRFSegmenter
from treebuilder.build_tree_CRF import CRFTreeBuilder

from optparse import OptionParser

import paths
import os.path
import sys
from document.doc import Document
import time
import traceback
from datetime import datetime

from logs.log_writer import LogWriter
from prep.preprocesser import Preprocesser

import utils.serialize

class DiscourseParser():
    def __init__(self, options, output_dir = None, 
                 log_writer = None):
        self.verbose = options.verbose
        self.skip_parsing = options.skip_parsing
        self.global_features = options.global_features
        self.save_preprocessed_doc = options.save_preprocessed_doc
        
        self.output_dir = os.path.join(paths.OUTPUT_PATH, output_dir if output_dir is not None else '')
        if not os.path.exists(self.output_dir):
            print 'Output directory %s not exists, creating it now.' % self.output_dir
            os.makedirs(self.output_dir)
        
        self.log_writer = LogWriter(log_writer)
        
        self.feature_sets = 'gCRF'
        
        initStart = time.time()

        self.preprocesser = None
        try:
            self.preprocesser = Preprocesser()
        except Exception, e:
            print "*** Loading Preprocessing module failed..."
            print traceback.print_exc()

            raise e
        try:
            self.segmenter = CRFSegmenter(_name = self.feature_sets, verbose = self.verbose, global_features = self.global_features)
        except Exception, e:
            print "*** Loading Segmentation module failed..."
            print traceback.print_exc()

            raise e
        
        try:        
            if not self.skip_parsing:
                self.treebuilder = CRFTreeBuilder(_name = self.feature_sets, verbose = self.verbose) 
            else:
                self.treebuilder = None
        except Exception, e:
            print "*** Loading Tree-building module failed..."
            print traceback.print_exc()
            raise e
        
        
        initEnd = time.time()
        print 'Finished initialization in %.2f seconds.' % (initEnd - initStart)
        print       
    
        
    def unload(self):
        if self.preprocesser is not None:
            self.preprocesser.unload()
        
        if not self.segmenter is None:
            self.segmenter.unload()
        
        if not self.treebuilder is None:
            self.treebuilder.unload()
        
    
    def parse(self, filename):
        if not os.path.exists(filename):
            print '%s does not exist.' % filename
            return
        
        self.log_writer.write('***** Parsing %s...' % filename)
        
        try:
            core_filename = os.path.split(filename)[1]
            serialized_doc_filename = os.path.join(self.output_dir, core_filename + '.doc.ser')
            doc = None
            if os.path.exists(serialized_doc_filename):
                doc = utils.serialize.loadData(core_filename, self.output_dir, '.doc.ser')
            
            if doc is None or not doc.preprocessed:   
                preprocessStart = time.time()
                doc = Document()                 
                doc.preprocess(filename, self.preprocesser)               
                
                preprocessEnd = time.time()
                
                print 'Finished preprocessing in %.2f seconds.' % (preprocessEnd - preprocessStart)
                self.log_writer.write('Finished preprocessing in %.2f seconds.' % (preprocessEnd - preprocessStart))
                
                if self.save_preprocessed_doc:
                    print 'Saved preprocessed document data to %s.' % serialized_doc_filename           
                    utils.serialize.saveData(core_filename, doc, self.output_dir, '.doc.ser')
                
            else:
                print 'Loaded saved serialized document data.'
            
            print
        except Exception, e:
            print "*** Preprocessing failed ***"
            print traceback.print_exc()
               
            raise e
        
        try:
            if not doc.segmented:
                segStart = time.time()
                
                self.segmenter.segment(doc)
                
                if self.verbose:
                    print 'edus'
                    for e in doc.edus:
                        print e
                    print
                    print 'cuts'
                    for cut in doc.cuts:
                        print cut
                    print
                    print 'edu_word_segmentation'
                
                segEnd = time.time()
                print 'Finished segmentation in %.2f seconds.' % (segEnd - segStart)     
                print 'Segmented into %d EDUs.' % len(doc.edus)
                
                
                self.log_writer.write('Finished segmentation in %.2f seconds. Segmented into %d EDUs.' % ((segEnd - segStart), len(doc.edus)))
                if self.save_preprocessed_doc:
                    print 'Saved segmented document data to %s.' % serialized_doc_filename           
                    utils.serialize.saveData(core_filename, doc, self.output_dir, '.doc.ser')
            else:
                print 'Already segmented into %d EDUs.' % len(doc.edus)
            
            print
        
            if options.verbose:
                for e in doc.edus:
                    print e
            
                 
        except Exception, e:
            print "*** Segmentation failed ***"
            print traceback.print_exc()
               
            raise e
        
        
        try:    
            ''' Step 2: build text-level discourse tree '''
            if self.skip_parsing:
                outfname = os.path.join(self.output_dir, core_filename + ".edus")
                print 'Output EDU segmentation result to %s' % outfname
                f_o = open(outfname, "w")
                for sentence in doc.sentences:
                    sent_id = sentence.sent_id
                    edu_segmentation = doc.edu_word_segmentation[sent_id]
                    i = 0
                    sent_out = []
                    for (j, token) in enumerate(sentence.tokens):
                        sent_out.append(token.word)
                        if j < len(sentence.tokens) - 1 and j == edu_segmentation[i][1] - 1:
                            sent_out.append('EDU_BREAK')
                            i += 1
                    f_o.write(' '.join(sent_out) + '\n')
                    
                f_o.flush()
                f_o.close()
            else:
                treeBuildStart = time.time()
    #                
                outfname = os.path.join(self.output_dir, core_filename + ".tree")
                
                pt = self.treebuilder.build_tree(doc)
                        
                print 'Finished tree building.'
    
                if pt is None:
                    print "No tree could be built..."
                        
                    if not self.treebuilder is None:
                        self.treebuilder.unload()
    
                    return -1
                                 
    #           Unescape the parse tree
                if pt:
                    doc.discourse_tree = pt
                    treeBuildEnd = time.time()
                    
    #                print out
                    print 'Finished tree building in %.2f seconds.' % (treeBuildEnd - treeBuildStart)  
                    self.log_writer.write('Finished tree building in %.2f seconds.' % (treeBuildEnd - treeBuildStart))
                    
                    for i in range(len(doc.edus)):
                        pt.__setitem__(pt.leaf_treeposition(i), '_!%s!_' % ' '.join(doc.edus[i]))
                    
                    out = pt.pprint()
                    print 'Output tree building result to %s.' % outfname
                    f_o = open(outfname, "w")
                    f_o.write(out)
                    f_o.close()
    
                
                if self.save_preprocessed_doc:
                    print 'Saved fully processed document data to %s.' % serialized_doc_filename           
                    utils.serialize.saveData(core_filename, doc, self.output_dir, '.doc.ser')
            
            print
        except Exception, e:
            print traceback.print_exc()
            
            raise e
    
        print '==================================================='
        #return dists#, probs

def main(options, args):
    parser = None
    try:
        if options.output_dir:
            output_dir = args[0]
            start_arg = 1
        else:
            output_dir = None
            start_arg = 0
        
        log_writer = None
        if options.logging:
            log_fname = os.path.join(paths.LOGS_PATH, 'log_%s.txt' % (output_dir if output_dir else datetime.now().strftime('%Y_%m_%d_%H_%M_%S')))
            log_writer = open(log_fname, 'w')

        
        if options.filelist:
            file_fname = args[start_arg]
            if not os.path.exists(file_fname) or not os.path.isfile(file_fname):
                print 'The specified file list %s is not a file or does not exist' % file_fname
                return
                 
        parser = DiscourseParser(options = options,
                                 output_dir = output_dir, 
                                 log_writer = log_writer)
        
        files = []
        skips = 0
        if options.filelist:
            file_fname = args[start_arg]
            for line in open(file_fname).readlines():
                fname = line.strip()
                    
                if os.path.exists(fname):
                    if os.path.exists(os.path.join(parser.output_dir, os.path.split(fname)[1] + '.tree')):
                        skips += 1
                    else:
                        files.append(fname)
                else:
                    skips += 1
#                    print 'Skip %s since it does not exist.' % fname          
        else:
            fname = args[start_arg]
#            print os.path.join(paths.tmp_folder, os.path.split(fname)[1] + '.xml')
            if os.path.exists(fname):
                if os.path.exists(os.path.join(parser.output_dir, os.path.split(fname)[1] + '.tree')):
                    skips += 1
                else:
                    files.append(fname)
            else:
                skips += 1
        
        print 'Processing %d documents, skipping %d' % (len(files), skips)
        
        for (i, filename) in enumerate(files):
            print 'Parsing %s, progress: %.2f (%d out of %d)' % (filename, i * 100.0 / len(files), i, len(files))
                    
            try:
                parser.parse(filename)
                
                parser.log_writer.write('===================================================')
            except Exception, e:
                print 'Some error occurred, skipping the file'
                raise e
           
        parser.unload()
        
    except Exception, e:
        print traceback.print_exc()
        if not parser is None:
            parser.unload()



v = '1.0'
if __name__ == '__main__':
    usage = "Usage: %prog [options] input_file/dir"
    
    optParser = OptionParser(usage=usage, version="%prog " + v)
    optParser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="verbose mode")
    optParser.add_option("-s", "--skip_parsing",
                      action="store_true", dest="skip_parsing", default=False,
                      help="Skip parsing, i.e., conduct segmentation only.")
    optParser.add_option("-D", "--filelist",
                      action="store_true", dest="filelist", default=False,
                      help="parse all files specified in the filelist file, one file per line.")
    optParser.add_option("-t", "--output_dir",
                         action="store_true", dest="output_dir", default=False,
                         help="Specify a directory for output files.")
    optParser.add_option("-g", "--global_features",
                         action="store_true", dest="global_features", default=False,
                         help="Perform a second pass of EDU segmentation using global features.")
    optParser.add_option("-l", "--logging",
                         action="store_true", dest="logging", default=False,
                         help="Perform logging while parsing.")
    optParser.add_option("-e", "--save",
                         action="store_true", dest="save_preprocessed_doc", default=False,
                         help="Save preprocessed document into serialized file for future use.")
    
    
       
    (options, args) = optParser.parse_args()
    if len(args) == 0:
        optParser.print_help()
        sys.exit(1)
                
        
    main(options, args)
    
