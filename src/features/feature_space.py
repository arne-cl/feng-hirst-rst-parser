'''
Created on 2013-02-18

@author: Vanessa Wei Feng
'''
from utils.utils import sorted_dict_keys

class FeatureGroup:
    def __init__(self, size = 1, legend = {}):
        self.data = {}
        self.size = size
        self.legend = legend

    def check_index(self, i):
        if i >= self.size:
            raise IndexError('Index out of bound: ' + str(i) + ' > ' + str(self.size-1))
        if not isinstance(i, int):
            raise TypeError('Index must be an int')
    def has_key(self, key):
        return self.data.has_key(key)
        
    def __getitem__(self, i):
        self.check_index(i)
        return self.data.__getitem__(i)

    def __setitem__(self, i, v):
        if not isinstance(v, (int, long, float)):
            raise TypeError('Value must be a numeric value')
        self.check_index(i)
        self.data.__setitem__(i, v)
        if (i not in self.legend or self.legend[i] == '') and self.size > 1:
            self.legend[i] = '[' + str(i) + ']'
            
    def __str__(self):
        return self.str_offset(0)
        
    def str_offset(self, offset):
        ret = ''
        for i in sorted_dict_keys(self.data):
            if self.data[i] > 0:
                ret += str(i+offset) + ':' + str(self.data[i]) + '\t'
        return ret

    def reset(self):
        self.data = {}

    def get_legend(self, offset = 0, group_name = ''):
        legend = {}
        
        for i in sorted_dict_keys(self.legend):
            if self.size > 1:
                legend[i+offset] = str(group_name) + '[' + str(self.legend[i]) + ']'
            else:
                legend[i+offset] = str(group_name)
        return legend

    
class FeatureSpace:
    def __init__(self):
        self.data = {}
        self.locked = False

    def __getitem__(self, i):
        if i in self.data:
            return self.data[i]
        else:
            self.add_group(i, 1, {0:i})
            return self.data[i]
            #raise IndexError('Feature Group does not exist')

    def __setitem__(self, i, v):
        self[i][0] = v
        #self.add_group(i, v)

    def add_group(self, name, size, legend = {}):
        if not isinstance(size, int):
            raise TypeError('Size of the group must be an int: ' + str(size))
        if self.locked:
            raise KeyError('FeatureSpace cannot be modified after first output.')
        self.data.__setitem__(name, FeatureGroup(size, legend))

    def __str__(self):
        ret = 'Feature groups: '
        for i in sorted_dict_keys(self.data):
            ret += "\n - " + str(i) + ":\t" + str(self.data[i])
        return ret

    def get_full_vector(self):
        self.locked = True # prevent further modifications of vector size
        ret = ''
        offset = 1 # feature indices must be 1-based
        for i in sorted_dict_keys(self.data):
            ret += self.data[i].str_offset(offset)
            offset += self.data[i].size
        return ret

    def get_full_legend(self):
        legend = {}
        offset = 1
        for i in sorted_dict_keys(self.data):
            legend.update(self.data[i].get_legend(offset, i))
            offset += self.data[i].size
        return legend

    def reset(self):
        for i in self.data:
            self.data[i].reset()
