'''
Created on Jan 10, 2014

@author: Vanessa
'''
from constituent import Constituent
from trees.parse_tree import ParseTree

class BaseRepresentation:
    def __init__(self):
        self.constituents = []
        self.constituent_scores = []
    
    def prepare_parsing(self):
        self.constituents = self.get_bottom_level_constituents()
            

#    def update_constituents(self, c):
#        if c.l_start in self.constituents:
#            self.constituents[c.l_start][c.r_end] = c
#        else:
#            self.constituents[c.l_start] = {c.r_end : c}
#            
#        if c.r_end in self.reverse_constituents:
#            self.reverse_constituents[c.r_end][c.l_start] = c
#        else:
#            self.reverse_constituents[c.r_end] = {c.l_start : c}
#        
#        
#    def extract_constituents_from_tree(self, t, l_start = 0):
#        ''' sort by l_start '''
#        ''' include the boundaries of the constituent, and the constituent itself '''
#        
#        if not isinstance(t, ParseTree):
#            c = Constituent(t, self, l_start, l_start + 1, l_start + 1)
#            self.update_constituents(c)
#            return
#        
#            
#        left = t[0]
#        offset = 1 if not isinstance(left, ParseTree) else len(left.leaves())
#        l_end = l_start + offset
#        r_end = l_start + len(t.leaves())
#        
#        c = Constituent(t, self, l_start, l_end, r_end)
#        
#        self.update_constituents(c)
#        
#        self.extract_constituents_from_tree(left, l_start)
#        
#        right = t[1]
#        self.extract_constituents_from_tree(right, l_end)
#    
#    
#    def get_constituent(self, l_start, r_end):
##        print l_start, self.constituents
#        if l_start in self.constituents and r_end in self.constituents[l_start]:
#            return self.constituents[l_start][r_end]
#        
#        return None
#    
#  
#    def get_all_constituents(self):
#        constituents = []
#        for start in self.constituents:
#            for end in self.constituents[start]:
#                constituents.append(self.constituents[start][end])
#        
#        return constituents
#    
#    def delete_constituent(self, c):
#        if c.l_start in self.constituents:
#            if c.r_end in self.constituents[c.l_start]:
#                self.constituents[c.l_start].pop(c.r_end)
#        
#        if c.r_end in self.reverse_constituents:
#            if c.l_start in self.reverse_constituents[c.r_end]:
#                self.constituents[c.r_end].pop(c.l_end)
#    
#    
#    def insert_constituent(self, c):
#        if c.l_start in self.constituents:
#            self.constituents[c.l_start][c.r_end] = c
#        else:
#            self.constituents[c.l_start] = {c.r_end : c}
#        
#        if c.r_end in self.reverse_constituents:
#            self.reverse_constituents[c.r_end][c.l_start] = c
#        else:
#            self.reverse_constituents[c.r_end] = {c.l_start : c}