'''
Created on 2013-11-03

@author: Wei
'''

from build_tree import TreeBuilder
import paths
import utils.utils
from trees.parse_tree import ParseTree
import random

class GreedyTreeBuilder(TreeBuilder):
    def __init__(self, _model_path = [paths.MODEL_PATH], _bin_model_file = None, _bin_scale_model_file = None,
                 _mc_model_file = None, _mc_scale_model_file = None, 
                 _name = "FengHirst", verbose = False, use_contextual_features = False):
        TreeBuilder.__init__(self, _model_path, _bin_model_file, _bin_scale_model_file, _mc_model_file, _mc_scale_model_file,
                             _name, verbose, use_contextual_features)
    
    
    def build_tree(self, input_file, output_file, model_path = './cur_set/', reset_contextual_features = False):
        TreeBuilder.build_tree(self, input_file, output_file, model_path, reset_contextual_features)
        
#        print len(self.stumps)
        while len(self.stumps) > 1:
            best_one = None
            max_bin_score = -2000
            for (index, bin_score) in enumerate(self.stumps_bin_scores):
                if bin_score > max_bin_score:
                    best_one = index
                    max_bin_score = bin_score
                                         
            if best_one is None:
                best_one = utils.utils.argsmax(self.stumps_bin_scores, 1)[0]
                    
            best_score = self.stumps_bin_scores[best_one]
            
            #print self.stumps
            if self.verbose:
                print 'best_one'
                print self.stumps[best_one]
                print self.stumps[best_one + 1]
                print 'best_score', best_score
                print 'bin scores'
                for i in range(len(self.stumps_bin_scores)):
                    print i, self.stumps_bin_scores[i]
                print
                
            instance_clone = (self.stumps, self.stumps_mc_scores, self.stumps_bin_scores, self.offsets, self.tree_score)
            self.connect_stumps(best_one, instance_clone)
            
        return (self.stumps[0], best_score)