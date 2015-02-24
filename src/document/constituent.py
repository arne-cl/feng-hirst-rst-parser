'''
Created on Aug 8, 2013

@author: Vanessa
'''
import utils.utils
from trees.parse_tree import ParseTree
import sys

class Constituent:
    def __init__(self, parse_subtree, doc, l_start, l_end, r_end, start_sent_id, end_sent_id):
        self.parse_subtree = parse_subtree
        self.doc = doc
        self.l_start = l_start
        self.l_end = l_end
        self.r_end = r_end # the ends are both exclusive
        self.start_sent_id = start_sent_id
        self.end_sent_id = end_sent_id # start_sent_id and end_sent_id are both inclusive
        
        self.start_word = self.doc.edu_word_segmentation[self.start_sent_id][self.l_start - self.doc.sentences[self.start_sent_id].start_edu][0]
            
        self.end_word = self.doc.edu_word_segmentation[self.end_sent_id][self.r_end - 1 - self.doc.sentences[self.end_sent_id].start_edu][1]
        
        self.main_edus = None
        self.left_child = None
        self.right_child = None
    
    def __str__(self):
        return self.print_span()
    
    def __repr__(self):
        return self.print_span()
    
    def print_span(self):
        return '(%d, %d, %d)' % (self.l_start, self.l_end, self.r_end)
    
    def get_subtree_height(self):
        if isinstance(self.parse_subtree, ParseTree):
            return self.parse_subtree.height()
        else:
            return 1
        
    def get_subtree_in_span(self, pos = 'L'):
        assert pos == 'L' or pos == 'R'
        
        assert self.r_end > self.l_start + 1
         
        if pos == 'L':
            return self.parse_subtree[0]
        else:
            return self.parse_subtree[1]
    
    def get_left_subtree(self):
        return self.get_subtree_in_span('L')
    
    def get_right_subtree(self):
        return self.get_subtree_in_span('R')
    
    
    def is_sentential(self):
        if self.l_start == self.r_end - 1:
            return True
        
        if utils.utils.find_EDU_in_sentence_index(self.doc.cuts, self.l_start) == utils.utils.find_EDU_in_sentence_index(self.doc.cuts, self.r_end - 1):
            return True
        else:
            return False
    
    ''' A strict-sentential constituent is such a constituent that it spans a proper part of a sentence '''
    def is_strict_sentential(self):
        if self.start_sent_id != self.end_sent_id:
            return False
        elif self.l_start == self.doc.cuts[self.start_sent_id][0] and self.r_end == self.doc.cuts[self.end_sent_id][1]:
            return False
        
        return True
    
    
    def get_num_edus_in_span(self, pos = 'L'):
        assert pos == 'L' or pos == 'R'
        
        assert self.r_end > self.l_start + 1
        
        t = self.get_subtree_in_span(pos)
        return 1 if not isinstance(t, ParseTree) else len(t.leaves())
    
    def get_num_edus(self):
        t = self.parse_subtree
        return 1 if not isinstance(t, ParseTree) else len(t.leaves())
    
    def get_num_edus_in_left(self):
        return self.get_num_edus_in_span('L')
    
    def get_num_edus_in_right(self):
        return self.get_num_edus_in_span('R')
    
    
    def get_subtree_rel_in_span(self, pos = 'L'):
        assert pos == 'L' or pos == 'R'
        
        assert self.r_end > self.l_start + 1
        
        t = self.get_subtree_in_span(pos)
        if not isinstance(t, ParseTree):
            return 'NO-REL'
        else:
            return t.node
    
    def get_num_tokens(self):
        if self.get_num_edus() == 1:
            return len(self.doc.edus[self.l_start])
        else:
            num_tokens = 0
            for i in range(self.l_end, self.r_end):
                num_tokens += len(self.doc.edus[i])
        
            return num_tokens
        
        
    def get_left_subtree_rel(self):
        return self.get_subtree_rel_in_span('L')
        
    def get_right_subtree_rel(self):
        return self.get_subtree_rel_in_span('R')
    
    def get_subtree_rel(self):
        if not isinstance(self.parse_subtree, ParseTree):
            return 'NO-REL'
        else:
            return self.parse_subtree.node
    
    
    def get_ngram(self, n):
#        print self.parse_subtree
        if isinstance(self.parse_subtree, ParseTree):
            leaves = []
            for leaf in self.parse_subtree.leaves():
                leaves.extend(leaf)
        else:
            leaves = self.parse_subtree
        
        if n > 0:
            start = 0
            end = min(n, len(leaves))
        else:
            start = max(0, len(leaves) + n)
            end = len(leaves)
        
        ngrams = []
        for i in range(start, end):
#            print leaves[i]
            ngrams.append(leaves[i].lower())
                
        #print ngrams
        return ngrams
      
    
    def get_POS_ngram(self, n):
        if n > 0:
            t = self.doc.sentences[self.start_sent_id].parse_tree
            start = self.start_word
            end = min(self.start_word + n, len(t.leaves()))
            
            if self.start_sent_id == self.end_sent_id:
                end = min(end, self.end_word)
            
#            print n
#            print 'start', start, 'end', end
#            print t
#            print self.doc.edu_word_segmentation[self.start_sent_id]
#            print self.doc.edus[self.l_start]
        else:
            t = self.doc.sentences[self.end_sent_id].parse_tree
            start = max(0, self.end_word + n)
            end = self.end_word
            
            if self.start_sent_id == self.end_sent_id:
                start = max(self.start_word, start)
        
#            print n
#            print 'start', start, 'end', end
#            print t
#            print self.doc.edu_word_segmentation[self.end_sent_id]
#            print self.doc.edus[self.r_end - 1]
#        
        ngrams = []
        for i in range(start, end):
            try:
                ngrams.append(t[t.leaf_treeposition(i)[ : -1]].node)
            except Exception, e:
                print self.l_start, self.l_end, self.r_end
                print self.parse_subtree
#                print self.cuts[self.start_sent_id]
#                print self.cuts[self.end_sent_id]
                print 'start_sent', self.start_sent_id, 'start_word', self.start_word, 'end_sent_id', self.end_sent_id, 'end_word', self.end_word
                print len(t.leaves()), t
                 
                print 'start, end: ', start, end
                print
                
                sys.exit(1)
        
#        print ngrams
#        print
        #print ngrams
        return ngrams
#        return '-'.join(ngrams)

    def span_equals(self, l_start, l_end, r_end):
        return self.l_start == l_start and self.l_end == l_end and self.r_end == r_end
    
    def span_equals_other_constituent(self, c):
        return self.l_start == c.l_start and self.l_end == c.l_end and self.r_end == c.r_end
    
    def traverse_tree(self, t, start_edu):
        if not isinstance(t, ParseTree):
            return [(t, start_edu)]
        else:
            result = []
            L = t[0]
            l_num_edus = 1 if not isinstance(L, ParseTree) else len(L.leaves())
            
            if t.node[-5] == 'N':
                result.extend(self.traverse_tree(L, start_edu))
                
            R = t[1]
            if t.node[-2] == 'N':
                result.extend(self.traverse_tree(R, start_edu + l_num_edus))
            
#            if len(result) == 0:
#                print t
#                print t.node
            
            return result
        
    def get_main_edus(self):
        if not self.main_edus:
            self.main_edus = self.traverse_tree(self.parse_subtree, self.l_start)
        
        return self.main_edus
    
    
    def is_leaf(self):
        return self.get_num_edus() == 1
    
    ''' merge this constituent with another constituent c, to make a new constituent'''
    def make_new_constituent(self, label, c, deepcopy = False):
        assert c.doc == self.doc
        assert self.r_end == c.l_start
        
        t = utils.utils.make_new_subtree(label, self.parse_subtree, c.parse_subtree, deepcopy = False)
        new_c = Constituent(t, self.doc, self.l_start, self.r_end, c.r_end, self.start_sent_id, c.end_sent_id)
        
        new_c.left_child = self
        new_c.right_child = c

        return new_c