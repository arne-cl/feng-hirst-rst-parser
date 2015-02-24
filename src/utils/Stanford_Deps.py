
class2type = {
'dep' : ['dep'],
'aux' : ['aux', 'auxpass', 'cop'],
'agent' : ['agent'],
'comp' : ['comp', 'acomp', 'attr', 'ccomp', 'xcomp', 'complm', 'obj', 'dobj', 'iobj', 'pobj', 'mark', 'rel', 'pcomp'],
'subj' : ['subj', 'nsubj', 'nsubjpass', 'csubj', 'csubjpass'],
'cc' : ['cc'],
'conj' : ['conj'],
'expl' : ['expl'],
'mod' : ['mod', 'abbrev', 'amod', 'appos', 'advcl', 'purpcl', 'det', 'predet', 'preconj', 'infmod', 'mwe', 'measure', 'partmod', 'advmod', 'neg', 'rcmod', 'quantmod', 'nn', 'npadvmod', 'tmod', 'num', 'number', 'prep', 'prepc', 'poss', 'possessive', 'prt'],
'parataxis' : ['parataxis'], 
'punct' : ['punct'],
'ref' : ['ref'], 
'sdep' : ['sdep', 'xsubj']
}

stanford_dep_types = []
for dep_type in class2type.keys():
    stanford_dep_types.append(dep_type + '.d')
    stanford_dep_types.append(dep_type + '.g')

stanford_dep_types_no_role = []
for dep_type in class2type.keys():
    stanford_dep_types_no_role.append(dep_type)


stanford_spec_dep_types = []
for dep_type in class2type.keys():
    stanford_spec_dep_types.extend(class2type[dep_type])

type2class = {}
for cl in class2type:
    for tp in class2type[cl]:
        type2class[tp] = cl
        type2class[tp + '.d'] = cl
        type2class[tp + '.g'] = cl 
