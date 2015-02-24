'''
Created on 2013-02-17

@author: Vanessa Wei Feng
'''
import os

from classifiers.svm_classifier import SVMClassifier
from features.seg_feature_writer import SegFeatureWriter
from trees.lexicalized_tree import LexicalizedTree
from prep.syntax_parser import SyntaxParser
from nltk.tree import ParentedTree

import paths
import utils.utils

class Segmenter: 
    
    penn_special_chars = {'-LRB-': '(', '-RRB-': ')', '-LAB-': '<', '-RAB-': '>',
                        '-LCB-': '{', '-RCB-': '}', '-LSB-': '[', '-RSB-':']',
                      '\\/' : '/', '\\*' : '*', '``' : '"', "''" : '"', "`" : "'"}
    
    def __init__(self, _model_path = paths.SEG_MODEL_PATH, _model_file = None, _scale_model_file = None,
                 verbose=False, _name="segmenter", dependencies = False):
        self.svm_classifier = SVMClassifier(class_type = 'bin', software = 'libsvm', 
                                         model_path = _model_path, bin_model_file = _model_file, bin_scale_model_file = _scale_model_file,
                                         output_filter = float,
                                         name= _name, verbose = verbose)

        self.feature_writer = SegFeatureWriter(verbose = verbose)
        
        self.syntax_parser = SyntaxParser(verbose = verbose, dependencies = dependencies)
    

    def create_lexicalized_tree(self, mrg, heads):
        """
        Creates a lexicalized syntax tree given a MRG-style parse and a Penn2Malt style heads file. 
        """
        t = LexicalizedTree.parse(mrg, leaf_pattern = '(?<=\\s)[^\)\(]+')  # Vanessa's modification
        t.lexicalize(heads, from_string = True)
        
        return t
    
    
    def split_by_sentence(self, text):
        """
        Takes a text and returns a list of (sentence, is_paragraph_boundary) elements
        Assumes that the text is pre-processed such that end of sentences are marked with <s>, end of paragraphs with <p>
        """
        result = []
        
        text = text.replace("\n", "")
        
        parse_pos = 0
        prev_pos = 0
        
        while parse_pos < len(text):
            
            next_tok = text[parse_pos:parse_pos + 3]
            
            if next_tok == "<s>" or next_tok == "<p>":
                result.append((text[prev_pos:parse_pos].strip(), next_tok))
                parse_pos = parse_pos + 3
                prev_pos = parse_pos
            else:
                parse_pos = parse_pos + 1
            
        return result
    
    def segment_tree(self, t):
        """
        Segments a text represented as a lexicalized syntax trees
        Returns a list of class labels for each token of the tree
        """
        data_to_classify = self.feature_writer.extract_features([t])
        
        results = []
        for d in data_to_classify:
            #print d
            results.append(self.svm_classifier.classify(d))
        
        return results
    
    def get_parsed_trees_from_string(self, tree_strings):
        # tree_strings separated by "\n"
        parsed_trees = []
        for line in tree_strings:
            line = line.strip()
            if line != '':
                parsed_trees.append(LexicalizedTree.parse(line, leaf_pattern = '(?<=\\s)[^\)\(]+'))
       
        return parsed_trees


    def get_deps(self, deps_filename):
        try:
            dep_f = open(deps_filename, 'r')
            deps = []
            sent_dep_str = ''
            
            started = True
            for line in dep_f.readlines():
                line = line.strip()
                if line == '' and started:
                    started = False
                    deps.append(sent_dep_str)       
                    sent_dep_str = ''
                else:
                    started = True
                    sent_dep_str += '\n' + line
            dep_f.close()
            return deps
        except Exception, e:
            print "*** Could not read the input file..."
            raise
    

    def do_segment(self, text, input_edus = None, parsed_filename = None, heads_filename = None, deps_filename = None):
        """
        Segments a text into elementary discourse units.
        Assumes that the text is pre-processed such that end of sentences are marked with <s>, end of paragraphs with <p>
        
        Returns a list containing :
        - a list of lexicalized syntax trees for each sentence
        - a list of couples (m, n) indicating a discourse unit between tokens at index m and n in the corresponding tree
        - a list of unescaped edus (including paragraph boundaries indications
        """
        
        segmented_text = self.split_by_sentence(text)
        
        if parsed_filename and heads_filename and deps_filename:
            #print os.path.exists(parsed_filename)
            unlexicalized_trees = self.get_parsed_trees_from_string(open(parsed_filename).readlines())
            heads = open(heads_filename).read().split("\r\n\r\n")[:-1]
            
            #print open(heads_filename).read()
#            for head in heads:
#                print head
                
            lexicalized_trees = []
            for line in open(parsed_filename).readlines():
                line = line.strip()
                if line != '':
                    t = LexicalizedTree.parse(line, leaf_pattern = '(?<=\\s)[^\)\(]+')
                    t.lexicalize(heads[len(lexicalized_trees)], from_string = True)
                    lexicalized_trees.append(t)
        
            dep_parses = self.get_deps(deps_filename)
            
        else:
            unlexicalized_trees, heads, dep_parses = self.syntax_parser.parse(map(lambda x: x[0], segmented_text))
            lexicalized_trees = map(lambda x, y: self.create_lexicalized_tree(x, y), unlexicalized_trees, heads)
        
#        for tree in unlexicalized_trees:
#            print tree
            
        #print unlexicalized_trees
        #print heads
        
        edus_intervals_pairs = []
        edus = []
        
        if input_edus:
            edus, edus_intervals_pairs = utils.utils.align_edus_with_syntax_trees(input_edus, lexicalized_trees, segmented_text, self.penn_special_chars)
        else:
            for i in range(0, len(lexicalized_trees)):
                t = lexicalized_trees[i]
                
                t_words = map(lambda x: t.unescape(x), t.leaves())
                
                # Vanessa's modification
                # check if breaks contains all exclude words
                exclude_words = ".`':;!?"
                
                eval_boundaries = self.segment_tree(t)

                for j in range(len(eval_boundaries) - 1):
                    if eval_boundaries[j] == 1.0 and eval_boundaries[j + 1] == 1.0:
                        #if not t_words[j].strip(exclude_words) and not t_words[j + 1].strip(exclude_words):
                        if not t_words[j + 1].strip(exclude_words):
                            eval_boundaries[j] = -1.0
            
                cur_edus_intervals = [k+1 for k in range(0, len(eval_boundaries)) if eval_boundaries[k] == +1.0]
                if not 0 in cur_edus_intervals:
                    cur_edus_intervals = [0] + cur_edus_intervals
                if not len(eval_boundaries) in cur_edus_intervals:
                    cur_edus_intervals.append(len(eval_boundaries))
   
                #print cur_edus_intervals
                cur_edus = []
                cur_edus_intervals_pairs = []
                        
                for j in range(0, len(cur_edus_intervals) - 1):
                    cur_edus.append(t_words[cur_edus_intervals[j]:cur_edus_intervals[j+1]])
                    cur_edus_intervals_pairs.append((cur_edus_intervals[j], cur_edus_intervals[j+1]))
                    
                # Add eventual paragraph boundary
                #if segmented_text[i][1] == True:
                    #cur_edus[len(cur_edus) - 1].append("<p>") 
                #print segmented_text[i][1]
                cur_edus[len(cur_edus) - 1].append(segmented_text[i][1]) 
                
                #print 'cur_edus', cur_edus
                edus_intervals_pairs.append(cur_edus_intervals_pairs)
                edus.extend(cur_edus)
        
        #print lexicalized_trees
        #print "edus_intervals_pairs: ", edus_intervals_pairs
        #print "edus: ", edus
        #print
         
        return [lexicalized_trees, dep_parses, edus_intervals_pairs, edus]
    
    
    def get_escaped_edus(self, trees, cuts, edus):
        """
        Returns the edus in their original format
        """
        result = []
        
        tot = 0
        for i in range(0, len(trees)):
            leaves = trees[i].leaves()
            for (j, (m, n)) in enumerate(cuts[i]):
                #print ' '.join(leaves[m:])
                escaped_edu = utils.utils.replace_words(" ".join(leaves[m:n]), self.penn_special_chars)
                
                ending = edus[tot + j][-1]
                if ending in ['<s>', '<p>']:
                    escaped_edu += " " + ending
                    
                result.append(escaped_edu)
            
            tot += len(cuts[i])
                
                
        return result
    

    def poll(self):
        """
        Checks if the classifier and syntax parser are still alive
        """
        return self.svm_classifier.poll() or self.syntax_parser.poll()
    

    def unload(self):
        self.svm_classifier.unload()
        self.syntax_parser.unload()
        pass

