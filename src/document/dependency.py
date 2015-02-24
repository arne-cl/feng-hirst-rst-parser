'''
Created on 2014-02-16

@author: Wei
'''

class Dependency:
    def __init__(self, governor_id, dependent_id, relation):
        self.governor = governor_id
        self.dependent = dependent_id
        self.relation = relation