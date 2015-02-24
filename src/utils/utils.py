import re
from itertools import izip
from nltk.tree import Tree
from trees.parse_tree import ParseTree
import rst_lib
import string

def replace_words(text, word_dic):
    """
    take a text and <strong class="highlight">replace</strong> <strong class="highlight">words</strong> that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, word_dic)))
    def translate(match):
        return word_dic[match.group(0)]
    return rc.sub(translate, text)

def unescape_penn_special_word(text):
    penn_special_chars = {'-LRB-': '(', '-RRB-': ')', '-LAB-': '<', '-RAB-': '>',
                            '-LCB-': '{', '-RCB-': '}', '-LSB-': '[', '-RSB-':']',
                          '\\/' : '/', '\\*' : '*',
                          '``' : '"', "''" : '"', '`' : "'"}

    return replace_words(text, penn_special_chars)


def sorted_dict_values_by_key(adict):
    L = []
    for i in sorted(adict.keys()):
        L.append(adict[i])
    return L

def sorted_dict_keys(adict):
    keys = adict.keys()
    return sorted(keys)

argmax = lambda array: max(izip(array, xrange(len(array))))[1]
argmin = lambda array: min(izip(array, xrange(len(array))))[1]

def permutation_indices(data):
    return sorted(range(len(data)), key = data.__getitem__)
 
def argsmax (array, how_many):
    L = permutation_indices(array)[-how_many:]
    L.reverse()
    return L

def count_how_many(array, item):
    tot = 0
    for array_item in array:
        if item == array_item:
            tot += 1
    return tot


def split_mrg_by_sentence(s):
    
    result = []
    cnt_par = 0
    last_split_index = 0
    
    for i in range(0, len(s)):
        if s[i] == "(":
            cnt_par = cnt_par + 1
        elif s[i] == ")":
            cnt_par = cnt_par - 1
        
        if cnt_par == 0:
            # Split
            if last_split_index < i:
                result.append(s[last_split_index:i].replace("\n","").strip()[1:])
                last_split_index = i + 1
    
    return result


def simplified_tag(t):
    """
    Returns a simplified POS tag:
    NP-SBJ -> NP
    PP=4 -> PP
    -RRB- -> -RRB-
    """
    
    if t == None:
        return None
    
    if t[0:1] == "-":
            return t
    else:
        caret_pos = t.find("-")
        
        t_minus_caret = ""
        
        if not caret_pos == -1:
            t_minus_caret = t[0:caret_pos]
        else:
            t_minus_caret = t
            
        equal_pos = t_minus_caret.find("=")
        
        t_simplified = ""
        
        if not equal_pos == -1:
            t_simplified = t_minus_caret[0:equal_pos]
        else:
            t_simplified = t_minus_caret
            
        return t_simplified


def split_hilda_inputfile_by_sentence(f):
    sents = []
    for line in open(f).readlines():
        line = line.strip()
        if line == '':
            continue
        sents.append(line.split('<s>'))
    
    return sents


def get_sent_dependencies(deps):
    sent2dep_list = []
    for (i, sent_deps) in enumerate(deps):
        sent_dep_list = []
        #tree = trees[i]
        for dep_item in sent_deps.split('\r\n'):
            dep_pattern = r'(.+?)\((.+?)-(\d+?), (.+?)-(\d+?)\)'
            dep_m = re.match(dep_pattern, dep_item)
            if dep_m is not None:
                #dep_type = type2class[dep_m.group(1).split('_')[0]]
                dep_type = dep_m.group(1)
                governor_word = dep_m.group(2)
                governor_word_number = int(dep_m.group(3)) - 1
                dependent_word = dep_m.group(4)
                dependent_word_number = int(dep_m.group(5)) - 1
                
                dep_item_info = (dep_type, governor_word, governor_word_number, dependent_word, dependent_word_number)
#                print 
                sent_dep_list.append(dep_item_info)

        sent2dep_list.append(sent_dep_list)
        
    return sent2dep_list

def print_SGML_tree(parse_tree, offset = 1, depth = 0, status = None, relation = None):
    joty_script_mapping = {'textual-organization' : 'TextualOrganization',
                           'same-unit' : 'Same-Unit'}
    
    out = ''
    for i in range(depth):
        out += '  '

    if isinstance(parse_tree, basestring):
        return out + '( %s (leaf %d) (rel2par %s) (text _!%s_!) )\n' % (status, offset,
                                                                relation, parse_tree)
        
    out += '( %s (span %d %d)' % ('Root' if depth == 0 else status, offset, offset + len(parse_tree.leaves()) - 1)
    
    if depth > 0:
        out += ' (rel2par %s)' % relation
        
    out += '\n'
                                      
    left = parse_tree[0]
    #print left
    left_status = 'Nucleus' if parse_tree.node[-5] == 'N' else 'Satellite'
    right = parse_tree[1]
    #print right
    right_status = 'Nucleus' if parse_tree.node[-2] == 'N' else 'Satellite'

    if left_status[0] == 'S' and right_status[0] == 'N':
        left_relation = replace_words(parse_tree.node[ : -6], joty_script_mapping)
        right_relation = 'span'
    elif right_status[0] == 'S' and left_status[0] == 'N':
        right_relation = replace_words(parse_tree.node[ : -6], joty_script_mapping)
        left_relation = 'span'
    else:
        left_relation = replace_words(parse_tree.node[ : -6], joty_script_mapping)
        right_relation = left_relation
        
    out += print_SGML_tree(left, offset, depth + 1, left_status, left_relation)
    out += print_SGML_tree(right, offset + (len(left.leaves()) if isinstance(left, Tree) else 1), depth + 1, right_status, right_relation) 

    for i in range(depth):
        out += '  '
    out += ')\n'

    return out



def copy_subtree(subtree, detach = False):
    if isinstance(subtree, Tree):
        result = subtree.__deepcopy__()
        if detach:
            result._parent = None
    else:
        result = subtree
    
    return result

def make_new_subtree(label, subtree1, subtree2, deepcopy = False):
    if deepcopy:
        stump1_clone = copy_subtree(subtree1, True)
        stump2_clone = copy_subtree(subtree2, True)
    else:
        stump1_clone = subtree1
        stump2_clone = subtree2
        
    if isinstance(stump1_clone, ParseTree):
        stump1_clone._parent = None
        
    if isinstance(stump2_clone, ParseTree):
        stump2_clone._parent = None
    
    return ParseTree(label, [stump1_clone, stump2_clone])
#    return ParseTree(label, [stump1_clone, stump2_clone])


def find_EDU_in_sentence_index(cuts, edu_index):
    for (i, (sent_start_edu, sent_end_edu)) in enumerate(cuts):
        if edu_index >= sent_start_edu and edu_index < sent_end_edu:
            return i


def load_tree_from_file(filename, tokenize = False):
    def preprocess_leaf(leaf):
        leaf = re.sub('_!(.+?)!_', '\\1', leaf)
        if tokenize:
            return leaf.split(' ')
        else:
            return leaf
    
    if filename.endswith('.dis'):
        pt = rst_lib.load_tree(filename)
    elif filename.endswith('.tree'):
        pt = ParseTree.parse(open(filename).read(), leaf_pattern = '_!.+?!_', parse_leaf = preprocess_leaf)
    
    return pt


def is_punctuation(word):
    if not word or len(word) == 0:
        return False
    
    for i in range(len(word)):
        if word[i] not in string.punctuation:
            return False
        
    return True

def simplify_tree(tree, start):
    if not tree:
        return None
    
#        print 'before', tree
    
    if not isinstance(tree, ParseTree):
        t = ParseTree('leaf', [str(start + 1)])
    else:
        t = tree.__deepcopy__(None)
#            print t
        
        L = simplify_tree(tree[0], start)
        R = simplify_tree(tree[1], start + len(L.leaves()))
        
        t[0] = L
        t[1] = R
    
#        print 'end', t
#        print
    
    return t
    
def get_syntactic_subtrees(tree, start_word, end_word):
#    print tree
#    print 'start_word', start_word, 'end_word', end_word
#    print

    if tree.node == 'ROOT':
        tree = tree[0]
        
    assert start_word >= 0 and end_word - start_word <= len(tree.leaves()) and start_word < end_word
    
    if len(tree.leaves()) == end_word - start_word:
        return [tree]
    
    subtrees = []
    start = 0
    i = 0
#    print len(tree)
    while i < len(tree) - 1:
        if start + len(tree[i].leaves()) > start_word:
            break
        
        start += len(tree[i].leaves())
        i += 1
        
    j = len(tree) - 1
    end = len(tree.leaves())
    while j > 0:
        if end - len(tree[j].leaves()) < end_word:
            break
        end -= len(tree[j].leaves())
        j -= 1
    
#    print 'i', i, 'j', j
    for k in range(i, j + 1):
        subtree = tree[k]
        if k == i:
            if k == j:
                end1 = end_word - start
            else:
                end1 = len(subtree.leaves())
            subtrees.extend(get_syntactic_subtrees(subtree, start_word - start, end1))
        elif k == j:
            if k == i:
                start1 = start_word
            else:
                start1 = 0
            subtrees.extend(get_syntactic_subtrees(subtree, start1, end_word - (end - len(subtree.leaves()))))
        else:
            subtrees.append(subtree)
    
    length = 0
    for subtree in subtrees:
        length += len(subtree.leaves())
    
    assert length == end_word - start_word

    return subtrees

 
def get_edu_entity_grid(entity_grid_filename):
    grid = []
    for line in open(entity_grid_filename).readlines()[1 : ]:
        line = line.strip()
        if line != '':
            fields = line.split('\t')
            grid.append(fields[1 : ])    
    return grid

def compute_edit_distance(sequence1, sequence2):
    #print 'rst:' , rst_actions
    #print 'pst:', pt_actions
    
    m = len(sequence1)
    n = len(sequence2)
    
    matrix = {}
    for i in range(m + 1):
        #print matrix[i]
        matrix[(i, 0)] = i
        
    for j in range(n + 1):
        matrix[(0, j)] = j 
    
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if sequence1[i - 1] == sequence2[j - 1]:
                substitution_cost = 0
            else:
                substitution_cost = 1

            matrix[(i, j)] = min(matrix[(i - 1, j - 1)] + substitution_cost,
                                 matrix[(i - 1, j)] + 1,
                                 matrix[(i, j - 1)] + 1)
            
            if i > 1 and j > 1 and sequence1[i - 1] == sequence2[j - 2] and sequence1[i - 2] == sequence2[j - 1]:
                matrix[(i, j)] = min(matrix[i - 2, j - 2] + substitution_cost,
                                     matrix[(i, j)])
    
    #for i in range(1, m + 1):
        #print rst_actions[i - 1], pt_actions[i - 1], matrix[(i, i)]
    
    return matrix[(m, n)]