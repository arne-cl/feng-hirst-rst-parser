'''
Created on 2013-05-10

@author: Wei
'''
import utils.rst_lib
from nltk.tree import Tree
import os.path
import paths
import utils.serialize

class Estimation:
    def __init__(self):
        self.probs = {}
    
    def estimate_file(self, filename):
        parse_tree = utils.rst_lib.load_tree(filename)
        
        for subtree in parse_tree.subtrees():
            left_span = subtree[0]
            right_span = subtree[1]
            head_rel = subtree.node
            left_rel = left_span.node if isinstance(left_span, Tree) else 'NO-REL'
            right_rel = right_span.node if isinstance(right_span, Tree) else 'NO-REL'
            rhs = left_rel + ' ' + right_rel
            
            if rhs in self.probs:
                if head_rel in self.probs[rhs]:
                    self.probs[rhs][head_rel] += 1
                else:
                    self.probs[rhs][head_rel] = 1
            else:
                self.probs[rhs] = {head_rel : 1}
    
    
if __name__ == '__main__':
    estimation = Estimation()
    
    for subdir in [
                   #'TEST', 
                   'TRAINING']:
        for fname in os.listdir(os.path.join('../../texts/RSTtrees-WSJ-main-1.0/', subdir)):
            if not fname.endswith('.dis'):
                continue
            
            estimation.estimate_file(os.path.join('../../texts/RSTtrees-WSJ-main-1.0/', subdir, fname))
    
    prob_sum = 0
    for rhs in estimation.probs:
        prob_sum += sum(estimation.probs[rhs].values())
        
    for rhs in estimation.probs:
        for head_rel in estimation.probs[rhs]:
            estimation.probs[rhs][head_rel] = float(estimation.probs[rhs][head_rel]) / prob_sum
    
    for rhs in estimation.probs:
        for head_rel in estimation.probs[rhs]:
            print head_rel + '->' + rhs, estimation.probs[rhs][head_rel]
            
    utils.serialize.saveData('rst_prod_probs', estimation.probs, '../../model/')