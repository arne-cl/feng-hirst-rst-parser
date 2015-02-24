
from nltk.tree import ParentedTree

class ParseTree(ParentedTree):
    def get_hash(self, T = None):
        if T is None:
            T = self
        if isinstance(T, ParseTree):
            return T.node + '(' + self.get_hash(T[0]) + ',' + self.get_hash(T[1]) + ')'
        else:
            return str(len(T))
    
    def __deepcopy__(self, memo = None):
        return self.copy(True)
    
    def count_left_of(self, pos):
        if not pos:
            return 0
        if pos[-1] == 1:
            if isinstance(self[pos[:-1]][0], ParseTree):
                add = len(self[pos[:-1]][0].leaves())
            else:
                add = 1
        else:
            add = 0
        return add + self.count_left_of(pos[:-1])
        
    def count_right_of(self, pos):
        if not pos:
            return 0
        if pos[-1] == 0:
            if isinstance(self[pos[:-1]][1], ParseTree):
                add = len(self[pos[:-1]][1].leaves())
            else:
                add = 1
        else:
            add = 0
        return add + self.count_right_of(pos[:-1])
            
    def get_first_left(self, pos):
        if not pos:
            return ()
        if pos[-1] == 1:
            return pos[:-1] + [0]
        else:
            return self.get_first_left(pos[:-1])
        
    def get_first_right(self, pos):
        if not pos:
            return ()
        if pos[-1] == 0:
            return pos[:-1] + [1]
        else:
            return self.get_first_right(pos[:-1])
