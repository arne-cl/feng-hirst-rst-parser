from base_parser import BaseParser
from trees.parse_tree import ParseTree
import utils.utils
import random
import os.path
import paths

class IntraSententialParser(BaseParser):
    def __init__(self, name = 'IntraParser', verbose = False, window_size = 3):
        BaseParser.__init__(self, name, verbose, window_size)
        
        self.scope = True
#        signature = random.getrandbits(24)
#        self.tmp_test_fname = os.path.join(paths.TMP_PATH, 'tmp_intra_struct_crf_test_%s.txt' % signature)
        
    def add_classifier(self, classifier, name):
        if name == 'bin':
            self.bin_classifier = classifier
        elif name == 'mc':
            self.mc_classifier = classifier
        else:
            raise Exception('Unknown classifier name', name)
        
        print 'Added classifier', name, 'to treebuilder', self.name
        
        
    def parse_sequence(self, sentence):
        if len(sentence.constituents) == 1:
            sentence.discourse_tree = sentence.constituents[0]
            return
        
        sentence.constituents_scores = self.parse_single_sequence(sentence.constituents, 
                                                                  labeling = False)[1]
                                                                  
        while len(sentence.constituents) > 1:
            best_one = None
            max_bin_score = -20.0
            
            for (index, bin_score) in enumerate(sentence.constituents_scores):

                if bin_score > max_bin_score:
                    best_one = index
                    max_bin_score = bin_score

            L = sentence.constituents[best_one]
            R = sentence.constituents[best_one + 1]
            new_constituent = L.make_new_constituent('n/a', R)
            sentence.constituents[best_one : best_one + 2] = [new_constituent]
            
            if len(sentence.constituents) > 1:
                sentence.constituents_scores = self.parse_single_sequence(sentence.constituents, 
                                                                          labeling = False)[1]
            
            
            ''' Assign relations '''
            seq_prob, mc_predictions = self.parse_single_sequence(sentence.constituents, 
                                                                  labeling = True)

            for k in range(len(sentence.constituents)):
                c = sentence.constituents[k]
                
                if c.get_num_edus() > 1:
                    predicted_label = mc_predictions[k]
                    
                    c.parse_subtree.node = predicted_label
                    if self.verbose:
                        print 'Relabling'
                        print 'L', c.left_child
                        print 'R', c.right_child
                        print 'with predicted label', predicted_label
                        print
        
#        print stumps[0]

        sentence.discourse_tree = sentence.constituents[0].parse_subtree
        if self.verbose:
            print sentence.discourse_tree

    def relabel_stumps(self, stumps):
        seq_prob, mc_predictions = self.parse_single_sequence(stumps, labeling = True)
            
        for k in range(len(stumps)):
            c = stumps[k]
            
            if not c.is_leaf():
                c1 = c.left_child
                c2 = c.right_child
                
                predicted_label = mc_predictions[k]
                stumps[k].node = predicted_label
                if self.verbose:
                    print 'Relabling'
                    print 'L', c1
                    print 'R', c2
                    print 'with predicted label', predicted_label
                    print
        
        
    def parse_each_sentence(self, sentence):
        self.clear_cache()
        
        sentence.prepare_parsing()
        
        return self.parse_sequence(sentence)
    