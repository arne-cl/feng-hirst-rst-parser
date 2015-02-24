'''
Created on Aug 8, 2013

@author: Vanessa
'''
from base_representation import BaseRepresentation

class Document(BaseRepresentation):
    def __init__(self, 
                 ssplit_filename = None, 
                 dis_filename = None, 
                 edu_filename = None,
                 parse_filename = None, 
                 heads_filename = None,
                 deps_filename = None):
        
        BaseRepresentation.__init__(self)
        
        self.preprocessed = False
        self.segmented = False
        self.parsed = False
        
        self.sentences = []
        self.edus = None
        self.cuts = None
        self.edu_word_segmentation = None
        self.start_edu = None
        self.end_edu = None
        self.discourse_tree = None
        
    
    def add_sentence(self, sentence):
        self.sentences.append(sentence)
        
    def preprocess(self, raw_filename, preprocesser):
        preprocesser.preprocess(raw_filename, self)
        self.preprocessed = True
        
        
    def get_bottom_level_constituents(self):
        constituents = []
        for sentence in self.sentences:
            assert sentence.discourse_tree and len(sentence.constituents) == 1
            constituents.append(sentence.constituents[0])
        
        return constituents