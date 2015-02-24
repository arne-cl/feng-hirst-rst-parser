'''
Created on Feb 19, 2013

@author: Vanessa Feng
'''
import utils.serialize

relations = utils.serialize.loadData("rels_list")

relations['NO-REL'] = len(relations) + 1
inv_relations = {}
for i in sorted(relations):
    inv_relations[relations[i]] = i 

print relations
print inv_relations