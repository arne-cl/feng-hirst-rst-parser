'''
Created on Feb 19, 2013

@author: Vanessa Wei Feng
'''

import utils.serialize
import time
import tempfile
import utils.utils
import random

from copy import deepcopy

#from tree_feature_writer import TreeFeatureWriter
import features.tree_feature_writer_hilda
import features.tree_feature_writer_Feng_Hirst
from trees.parse_tree import ParseTree
from classifiers.svm_classifier import SVMClassifier

import utils.RST_Classes
import paths

class TreeBuilder:

    
    def __init__(self, _model_path = paths.MODEL_PATH, _bin_model_file = None, _bin_scale_model_file = None,
                 _mc_model_file = None, _mc_scale_model_file = None, 
                 _name = "FengHirst", verbose = False, use_contextual_features = False):
        
        self.name = _name
        self.verbose = verbose
        self.use_contextual_features = use_contextual_features
        
        if self.name == 'hilda':
            self.feature_writer = features.tree_feature_writer_hilda.TreeFeatureWriter(verbose)
            self.svm_mc_classifier = SVMClassifier(class_type = 'mc', software = 'libsvm', 
                                         model_path = _model_path, mc_model_file = _mc_model_file, mc_scale_model_file = _mc_scale_model_file,
                                         output_filter = self.treat_mc_output,
                                         name= _name + "_mc", verbose = verbose)
            self.svm_bin_classifier = SVMClassifier(class_type = 'bin', software = 'liblinear', 
                                         model_path = _model_path, bin_model_file = _bin_model_file, bin_scale_model_file = _bin_scale_model_file,
                                         output_filter = self.treat_liblinear_output,
                                         name= _name + "_bin", verbose = verbose)
        elif self.name == 'FengHirst':
            self.feature_writer = features.tree_feature_writer_Feng_Hirst.TreeFeatureWriter(verbose,
                                                                                            use_contextual_features = use_contextual_features,
                                                                                            subdir = '')
            
            self.svm_bin_classifier1 = SVMClassifier(class_type = 'bin', software = 'svm_perf_classify',  
                                         model_path = _model_path, bin_model_file = _bin_model_file[0], bin_scale_model_file = _bin_scale_model_file,
                                         output_filter = float,
                                         name= _name + "_bin", verbose = verbose)
            self.svm_bin_classifier2 = SVMClassifier(class_type = 'bin', software = 'svm_perf_classify',  
                                         model_path = _model_path, bin_model_file = _bin_model_file[1], bin_scale_model_file = _bin_scale_model_file,
                                         output_filter = float,
                                         name= _name + "_bin", verbose = verbose)
            self.svm_mc_classifier1 = SVMClassifier(class_type = 'mc', software = 'svm_multiclass_classify', 
                                         model_path = _model_path, mc_model_file = _mc_model_file[0], mc_scale_model_file = _mc_scale_model_file,
                                         output_filter = self.treat_mc_output,
                                         name= _name + "_mc", verbose = verbose)
            self.svm_mc_classifier2 = SVMClassifier(class_type = 'mc', software = 'svm_multiclass_classify', 
                                         model_path = _model_path, mc_model_file = _mc_model_file[1], mc_scale_model_file = _mc_scale_model_file,
                                         output_filter = self.treat_mc_output,
                                         name= _name + "_mc", verbose = verbose)
            
        else:
            print 'Unrecognized tree_builder name: %s' % self.name
            raise Exception
        
        
    
    def get_list_hash(self, L):
        if not len(L):
            return ''
        if isinstance(L[0], ParseTree):
            ret_str = L[0].get_hash()
        else:
            ret_str = str(len(L[0]))
        return ret_str + '|' + self.get_list_hash(L[1:])
            
    
    def center_norm(self, V):
        M = max(V)
        d = float(M+min(V))/2
        return map(lambda x: float(x-d)/(M-d), V)
    
    
    def treat_mc_output(self, output):
        fields = output.split()
        if len(fields) < 2:
            return (-1, 'Error', fields)
        
        
        if int(fields[0]) in self.feature_writer.inv_relations:
            label = self.feature_writer.inv_relations[int(fields[0])]
        else: 
            label = 'Unknown'
        
        #print "####\n", int(fields[0]), label, map(float, fields[1:]), "\n###\n"
        return (int(fields[0]), label, map(float, fields[1:]))
    
    
    
    def treat_liblinear_output(self, output):
        fields = output.split()
        if len(fields) < 3:
            print "Error in liblinear output: ", fields
            exit(-1)
        return float(fields[1])
     

    def classify_pair(self, stumps, pair, offsets, i, stumps_mc_scores = None, stumps_bin_scores = None):
        if self.use_contextual_features and self.prev_tree is not None:
            (prev_stump, next_stump) = utils.utils.get_context_stumps(self.prev_tree, stumps, pair, i)
#            print 'L:', stumps[i]
#            print 'R:', stumps[i+1]
#            print pair
#            print 'prev:', prev_stump
#            print 'next:', next_stump
#            print
        else:
            prev_stump = None
            next_stump = None
            
        scope = utils.utils.is_within_sentence(pair)
        if self.name == 'FengHirst':
            (bin_inst, mc_inst) = self.feature_writer.write_instance(None, None, pair, prev_stump, next_stump, None, 
                                                                         self.syntax_trees, self.sent2deps_list, 
                                                                         self.breaks, offsets[i],
                                                                         reset_contextual_features = not scope)
            
        else:
            (bin_inst, mc_inst) = self.feature_writer.write_instance(None, None, pair, None, self.syntax_trees, self.breaks, 
                                                                         offsets[i])

            
        if self.name == 'FengHirst':
            if scope:
                bin_score = self.svm_bin_classifier1.classify(bin_inst)
                mc_score = self.svm_mc_classifier1.classify(mc_inst)
            else:
                bin_score = self.svm_bin_classifier2.classify(bin_inst)
                mc_score = self.svm_mc_classifier2.classify(mc_inst)
        else:
            bin_score = self.svm_bin_classifier.classify(bin_inst)
            mc_score = self.svm_mc_classifier.classify(mc_inst)
        return (bin_score, mc_score)
    
                
    def connect_stumps(self, i, (stumps, stumps_mc_scores, stumps_bin_scores, offsets, tree_score)):
        #print stumps_mc_scores[i]
        
        new_stump = utils.utils.make_new_stump(stumps_mc_scores[i][1], stumps[i], stumps[i+1])
        new_stump.probs = self.center_norm(stumps_mc_scores[i][2])
        tree_score[0] = tree_score[0] + stumps_bin_scores[i] # + max(new_stump.probs)
        tree_score[1] += 1
        
        
        if i > 0: # left pair
            #print "\n### Erasing score [%d]: %f" %(i-1, stumps_bin_scores[i-1])
            pair = utils.utils.make_new_stump('n/a', stumps[i-1], new_stump)
            (bin_score, mc_score) = self.classify_pair(stumps, pair, offsets, i - 1, stumps_mc_scores, stumps_bin_scores)
                
            #print i, bin_inst
            stumps_bin_scores[i-1:i] = [bin_score]
            #print stumps_bin_scores[i - 1]
            stumps_mc_scores[i-1:i] = [mc_score]
            
        if i+2 < len(stumps): # right pair
            pair = utils.utils.make_new_stump('n/a', new_stump, stumps[i+2])
            (bin_score, mc_score) = self.classify_pair(stumps, pair, offsets, i, stumps_mc_scores, stumps_bin_scores)
                
            #print i, bin_inst
            stumps_bin_scores[i+1:i+2] = [bin_score]
            #print stumps_bin_scores[i - 1]
            stumps_mc_scores[i+1:i+2] = [mc_score]
    
        #print "\n### Erasing score [%d]: %f" %(i, stumps_bin_scores[i])
        stumps_bin_scores[i:i+1] = []
        stumps_mc_scores[i:i+1] = []
        stumps[i:i+2] = [new_stump, ]
        offsets[i+1:i+2] = []
    
    
    
    def best_so_far(self, (tot_score, nb_rels), exploration = 1.0):
        
        if nb_rels < 3:
            return True
       
        if nb_rels not in self.best_tree_scores:
            self.best_tree_scores[nb_rels] = tot_score
            return True
        
        if self.best_tree_scores[nb_rels] * exploration > tot_score:
            return False
        else:
            self.best_tree_scores[nb_rels] = max(self.best_tree_scores[nb_rels], tot_score)
            return True

    def build_tree(self, input_file, output_file, model_path = './cur_set/', reset_contextual_features = False):
        
        self.best_tree_scores = {}
        self.reset_contextual_features = reset_contextual_features
        
        #(self.syntax_trees, self.deps, self.breaks, self.edus) = utils.serialize.loadData(input_file, '', '')
        (self.syntax_trees, self.deps, self.breaks, self.stumps) = (input_file[0], input_file[1], input_file[2], 
                                                                                  input_file[3])
#        for i in range(len(self.syntax_trees)):
#            print self.syntax_trees[i]
#            print self.deps[i]
            
        if self.name == 'FengHirst':
            self.sent2deps_list = utils.utils.get_sent_dependencies(self.deps)
        # Check if only one EDU
        if len(self.stumps) == 1:
            return [ParseTree("n/a", [self.stumps[0]])]

        #for edu in self.edus:
            #print edu
            
        self.stumps_bin_scores = []
        self.stumps_mc_scores = []
        self.offsets = range(0, len(self.stumps)-1)
        self.tree_score = [0, 0]
        
        for (i, offset) in enumerate(self.offsets):
            pair = utils.utils.make_new_stump('n/a', self.stumps[i], self.stumps[i+1])
            (bin_score, mc_score) = self.classify_pair(self.stumps, pair, self.offsets, i)
            
            self.stumps_bin_scores += [bin_score]
            self.stumps_mc_scores += [mc_score]
            

    
    def poll(self):
        return self.svm_bin.poll() or self.svm_mc.poll()    
    
    
    def unload(self):
        if self.name == 'FengHirst':
            self.svm_bin_classifier1.unload()
            self.svm_bin_classifier2.unload()
            
            self.svm_mc_classifier1.unload()
            self.svm_mc_classifier2.unload()
        else:
            self.svm_bin_classifier.unload()
        
            self.svm_mc_classifier.unload()
        
