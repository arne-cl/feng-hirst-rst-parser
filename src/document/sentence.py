'''
Created on 2014-01-09

@author: Wei
'''
import utils.rst_lib
from base_representation import BaseRepresentation
from constituent import Constituent

class Sentence(BaseRepresentation):
    def __init__(self, sent_id, raw_text, doc):
        BaseRepresentation.__init__(self)
        
        self.sent_id = sent_id
        self.raw_text = raw_text
        self.doc = doc
        
        self.tokens = []
        self.dependencies = []
        
        self.unlexicalized_parse_tree = None
        self.parse_tree = None
        self.heads = None
    
    def set_unlexicalized_tree(self, tree):
        self.unlexicalized_parse_tree = tree
    
    def set_lexicalized_tree(self, tree):
        self.parse_tree = tree
        
    def add_token(self, token):
        assert len(self.tokens) == token.id - 1
        
        self.tokens.append(token)
        
    def add_dependency(self, dep):
        self.dependencies.append(dep)
            
    def get_ngram(self, token_offset, n):
        if n > 0:
            start = token_offset
            end = min(token_offset + n, len(self.tokens))
        else:
            start = max(0, token_offset + n)
            end = token_offset
        
        ngrams = []
        for i in range(start, end):
            ngrams.append(self.tokens[i].word.lower())
                
        #print ngrams
        return ngrams
      
    
    def get_POS_ngram(self, token_offset, n):
        if n > 0:
            start = token_offset
            end = min(token_offset + n, len(self.tokens))
        else:
            start = max(0, token_offset + n)
            end = token_offset

        ngrams = []
        for i in range(start, end):
            ngrams.append(self.parse_tree[self.parse_tree.leaf_treeposition(i)[ : -1]].node)
        
        return ngrams
    
    
    def get_edu(self, token_id):
        for i in range(self.start_edu, self.end_edu):
            (start_word, end_word) = self.doc.edu_word_segmentation[self.sent_id][i - self.start_edu]
            if token_id >= start_word and token_id < end_word:
                return i
            
            
    def get_bottom_level_constituents(self):
        constituents = []
        (start_edu, end_edu) = self.doc.cuts[self.sent_id]
        
        for i in range(start_edu, end_edu):
            c = Constituent(self.doc.edus[i], self.doc,
                            i, i + 1, i + 1, self.sent_id, self.sent_id)
            
            constituents.append(c)
        
        return constituents