
from trees.parse_tree import ParseTree
import os.path

class BaseParser:
    def __init__(self, name, verbose = False, window_size = 3):
        self.name = name
        self.verbose = verbose
        self.window_size = window_size
        
        self.cached_mc_features = {}
        self.cached_struct_features = {}
        
    
    def clear_cache(self):
        self.cached_mc_features = {}
        self.cached_struct_features = {}
    
         
    def parse_single_sequence(self, s, labeling):
        features = []
        
        if not labeling:
            for k in range(len(s) - 1):
                c1 = s[k]
                c2 = s[k + 1]
    
                if k == 0:
                    c0 = None
                else:
                    c0 = s[k - 1]
                
                if k == len(s) - 2:
                    c3 = None
                else:
                    c3 = s[k + 2]
                    
                
                C = [c0, c1, c2, c3]
                if c0:
                    c0_num_edus = c0.get_num_edus()
                else:
                    c0_num_edus = 0
                
                c1_tot = c1.l_start
                c1_num_edus = c1.get_num_edus()
                c2_num_edus = c2.get_num_edus()
                
                if c3:
                    c3_num_edus = c3.get_num_edus()
                else:
                    c3_num_edus = 0
                    
                positions = [-1, 0, 1]
                hash_key = (c1_tot, c0_num_edus, c1_num_edus, c2_num_edus, c3_num_edus)
                
                if hash_key in self.cached_struct_features:
#                if False:
                    inst_features_str = self.cached_struct_features[hash_key]
                else:     
                    if self.verbose:       
                        print 'c0:', c0
                        print 'c1:', c1
                        print 'c2:', c2
                        print 'c3:', c3
                    inst_features = self.feature_writer.write_features_for_constituents(C, positions,
                                                                                        self.scope,
                                                                                        labeling = False)
                    
                    inst_features_str = '\t'.join(list(inst_features))
                    self.cached_struct_features[hash_key] = inst_features_str
                    
                features.append('%d\t%s' % (0, inst_features_str))
                
        else:
            for k in range(len(s)):
                c = s[k]
                
#                print 'k', k, c
#                print c
#                print
                    
                if k == 0:
                    c0 = None
                else:
                    c0 = s[k - 1]
                
                if k == len(s) - 1:
                    c3 = None
                else:
                    c3 = s[k + 1]
                
                if not c.is_leaf():
                    c1 = c.left_child
                    c2 = c.right_child
                    
                    C = [c0, c1, c2, c3]
                    if c0:
                        c0_num_edus = c0.get_num_edus()
                    else:
                        c0_num_edus = 0
                    
                    c1_tot = c1.l_start
                    c1_num_edus = c1.get_num_edus()
                    c2_num_edus = c2.get_num_edus()
                    
                    if c3:
                        c3_num_edus = c3.get_num_edus()
                    else:
                        c3_num_edus = 0
                        
                    positions = [-1, 0, 1]
                    hash_key = (c1_tot, c0_num_edus, c1_num_edus, c2_num_edus, c3_num_edus)
                    
#                    if post_editing:
#                        if c0:
#                            print 'c0:', c0, c0.parse_subtree
#                        print 'c1:', c1, c1.parse_subtree
#                        print 'c2:', c2, c2.parse_subtree
#                        if c3:
#                            print 'c3:', c3, c3.parse_subtree
                        
                    if self.verbose:
                        print 'c0:', c0
                        print 'c1:', c1
                        print 'c2:', c2
                        print 'c3:', c3
                            
                    if hash_key in self.cached_mc_features:
#                    if False:
                        inst_features_str = self.cached_mc_features[hash_key]
                    else:
                        inst_features = self.feature_writer.write_features_for_constituents(C, positions, 
                                                                                            self.scope,
                                                                                            labeling = True)
                        
                        inst_features_str = '\t'.join(list(inst_features))
                        self.cached_mc_features[hash_key] = inst_features_str
                else:
                    inst_features_str = 'Num_EDUs=1'
        
                features.append('%d\t%s' % (0, inst_features_str))
#                print inst_features_str

        if not labeling:
            classifier = self.bin_classifier
        else:
            classifier = self.mc_classifier


#        print classifier.name
        (sequence_prob, predictions) = classifier.classify(features)

        scores = []
        for i in range(len(predictions)):    
            (prediction, prob) = predictions[i]

            if not labeling:
                struct_prediction = int(prediction)
                if struct_prediction == 0:
                    prob = 1.0 - prob
            
                scores.append(prob)
            else:
                scores.append(prediction)
        
        return sequence_prob, scores


    def generate_crf_sequences(self, stumps, i, labeling = False):
        if self.scope:
            return [(stumps, i)]
        
        
        pref_start = i - (self.window_size - 1)
        if labeling:
            suf_start = i + 1
            suf_end = i + self.window_size
        else:
            suf_start = i + 2
            suf_end = i + 1 + self.window_size
        

        prefix_sequence = stumps[max(0, pref_start) : i]

        if suf_start < len(stumps):
            suffix_sequence = stumps[suf_start : min(len(stumps), suf_end)]
        else:
            suffix_sequence = []

        
        S = []
        if labeling:
            c = [stumps[i]]
        else:
            c = [stumps[i], stumps[i + 1]]

        max_length = min(self.window_size - 1, len(stumps) - (1 if labeling else 2))
        
        for j in range(0, self.window_size):
            k = max_length - j
            
            pref_s = prefix_sequence[-j : ] if j > 0 else []
            suf_s = suffix_sequence[ : k]
            
            if len(pref_s) + len(suf_s) != max_length:
                continue

            s = (pref_s + c + suf_s, len(pref_s))
       
            if s not in S:
                S.append(s)

        
        return S
    
    
    def unload(self):
        pass
