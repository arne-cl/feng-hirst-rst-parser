
import string
from nltk.tree import Tree
from trees.parse_tree import ParseTree
from utils.utils import unescape_penn_special_word

class LexicalizedTree(ParseTree):
    "Extends nltk.tree to support lexical heads"
    head = -1
    head_sup = -1
    
    def unescape(self, mystr):
        #return replace_words(mystr.lower(), self.penn_special_chars)
        return unescape_penn_special_word(mystr)
    
    
    def unescape_leaves(self):
        unescaped_leaves = []
        for leaf in self.leaves():
            unescaped_leaves.append(unescape_penn_special_word(leaf))
        
        return unescaped_leaves
    
    def get_head(self, pos):
        if not isinstance(self[pos], LexicalizedTree):
            return self.get_head(pos[:-1])
        if self[pos].head < 0:
            raise IndexError("No head present")
        
        
        return self.leaves()[self[pos].head].lower()
    
    def get_head_tag(self, pos):
        if not isinstance(self[pos], LexicalizedTree):
            return self.get_head_tag(pos[:-1])
        if self[pos].head < 0:
            raise IndexError("No head present")
        
        
        leaf_pos = self.leaf_treeposition(self[pos].head)
        return self.leaves()[self[pos].head].lower(), self.get_syntactic_tag(leaf_pos)

    def get_syntactic_tag(self, pos):
        if not isinstance(self[pos], LexicalizedTree):
            return self.get_syntactic_tag(pos[:-1])
        return self[pos].node
    
    def remove_null_elements(self):
        to_delete = []
        
        for i in range(0, len(self.leaves())):
            pos = self.leaf_treeposition(i)[0:-1]
            #print 'pos', pos, self[pos]
            if self[pos].node == '-NONE-':
                to_delete += [pos]
        
        for pos in reversed(to_delete):
            del self[pos]
            while len(self[pos[0:-1]]) == 0:
                del self[pos[0:-1]]
                pos = pos[0:-1]

    def relexicalize(self, index):
        for pos in self.treepositions():
            if isinstance(self[pos], LexicalizedTree) and self[pos].head >= index:
                self[pos].head -= 1        
    
    # TODO CHECKKKKK
    # If from_string = True, heads_file is directly the content of a head descriptor, no need to open the file
    def lexicalize(self, heads, offset = 0):
        #print 'inital self:', self
        self.offset = offset
        
        #print heads
        self.remove_null_elements()
        
        for i in range(0, len(self.leaves())):
            #print 'leaf:', self.leaves()[i]
            pos = self.leaf_treeposition(i)[0:-1]
            sub = self[pos]
            
            while len(heads[offset]) < 2:
                offset += 1
            
            sub.head = i
            sub.head_sup = int(heads[offset][2])-1
 
            word_tb = self.unescape(sub[0]).replace(' ', '')  # Vanessa's modification
            #word_malt = self.unescape(heads[offset][0].lower())
            word_malt = self.unescape(heads[offset][0])
#            print 'offset', offset, heads[offset]
            
            if word_tb != word_malt:
                print "LEXICALIZATION ERROR: " + word_tb + " != " + word_malt
                print sub
                exit(-1)
            offset += 1
            #print
        
        self._lexicalize()
        return offset
    
    def _lexicalize(self):
        done = False
        
        if not isinstance(self[0], Tree):
            return

        heads = []
        head_sups = []

        #print 'self in lexicalize:', self
        for child in self:
            #print 'child:'
            child._lexicalize()

            #print 'lexicalized_child:', child
            heads.append(child.head)
            head_sups.append(child.head_sup)
        
        #print
        if len(heads) == 1:
            self.head = heads[0]
            self.head_sup = head_sups[0]
            return

        for head_sup in head_sups:
            if head_sup in heads:
                self.head = head_sup
                self.head_sup = head_sups[heads.index(head_sup)]
                done = True     
        
        if not done:
            self.head = heads[0]
            self.head_sup = head_sups[0]
#            print "\n\n#### Lexicalization ERROR\n"
#            print heads
#            print head_sups
#            print self
#            exit(-1)
            
    def _pprint_flat(self, nodesep, parens, quotes):
        childstrs = []
        
        for child in self:
            if isinstance(child, Tree):
                childstrs.append(child._pprint_flat(nodesep, parens, quotes))
            elif isinstance(child, tuple):
                childstrs.append("/".join(child))
            elif isinstance(child, str) and not quotes:
                childstrs.append('%s' % child)
            else:
                childstrs.append('%r' % child)

        # Add lexical head info:
        if self.head >= 0:
            if self.head >= len(self.root.leaves()):
                print self.head
                print self.root.leaves()
            head_str = '[' + self.root.leaves()[self.head] + ' ' + str(self.head) + ' ' + str(self.head_sup) + '] '
        else:
            head_str = ''

        #print 'head_str:', head_str
        #print 'node:', self.node
        if isinstance(self.node, basestring):
            return '%s%s%s%s %s%s' % (parens[0], self.node, head_str, nodesep, 
                                    string.join(childstrs), parens[1])
        else:
            return '%s%r%s%s %s%s' % (parens[0], self.node, head_str, nodesep, 
                                    string.join(childstrs), parens[1])

    def pprint(self, margin=70, indent=0, nodesep='', parens='()', quotes=False): 

        s = self._pprint_flat(nodesep, parens, quotes) 
        if len(s)+indent < margin: 
            return s 

        # Add lexical head info:
        if self.head >= 0:
            if self.head >= len(self.root.leaves()):
                print self.head
                print self.root.leaves()
            head_str = '[' + self.root.leaves()[self.head] + '] '
        else:
            head_str = '' + str(self.head)
            
        if isinstance(self.node, basestring):
            s = '%s%s%s%s' % (parens[0], self.node, head_str, nodesep) 
        else: 
            s = '%s%r%s%s' % (parens[0], self.node, head_str, nodesep) 
        for child in self: 
            if isinstance(child, Tree): 
                s += '\n'+' '*(indent+2)+child.pprint(margin, indent+2, 
                                        nodesep, parens, quotes) 
            elif isinstance(child, tuple): 
                s += '\n'+' '*(indent+2)+ "/".join(child) 
            elif isinstance(child, str) and not quotes: 
                s += '\n'+' '*(indent+2)+ '%s' % child 
            else: 
                s += '\n'+' '*(indent+2)+ '%r' % child 
        return s+parens[1]

