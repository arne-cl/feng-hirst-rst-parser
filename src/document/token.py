'''
Created on 2014-01-09

@author: Wei
'''

class Token:
    def __init__(self, word, word_id, sentence):
        self.word = word
        self.id = word_id
        self.sentence = sentence
        self.lemma = None
        self.char_begin_offset = None
        self.char_end_offset = None
        self.pos = None
        
        
    def set_lemma(self, lemma):
        self.lemma = lemma
        
    def get_lemma(self):
        return self.lemma
    
    
    def set_char_begin_offset(self, offset):
        self.char_begin_offset = offset
        
    
    def get_char_begin_offset(self):
        return self.char_begin_offset
    
    
    def set_char_end_offset(self, offset):
        self.char_end_offset = offset
        
        
    def get_char_end_offset(self):
        return self.char_end_offset
        
        
    def get_treepos(self):
        if self.sentence.parse_tree is not None:
            return self.sentence.parse_tree.leaf_treeposition(self.id - 1)
        elif self.sentence.unlexicalized_parse_tree is not None:
            return self.sentence.unlexicalized_parse_tree.leaf_treeposition(self.id - 1)
    
    def get_PoS_tag(self):
        if not self.pos:
            if self.sentence.parse_tree is not None:
                t = self.sentence.parse_tree
                self.pos = t[self.get_treepos()[ : -1]].node
                
            elif self.sentence.unlexicalized_parse_tree is not None:
                t = self.sentence.unlexicalized_parse_tree
            
                self.pos = t[self.get_treepos()[ : -1]].node
                
        return self.pos
    
    
    def is_sentence_end(self):
        return self.id == len(self.sentence.parse_tree.leaves())
    
    
    def is_sentence_begin(self):
        return self.id == 1
    
    
    def get_relative_position(self):
        return (self.id - 1) * 1.0 / (len(self.sentence.parse_tree.leaves()) - 1)
