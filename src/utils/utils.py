'''
Created on 2013-02-17

@author: Vanessa Wei Feng
'''
import os.path
import paths
from datetime import datetime
import subprocess
import re
from itertools import izip
from nltk.tree import Tree
from RST_Classes import rel_status_classes, class2rel
import math
from trees.parse_tree import ParseTree
import rst_lib

def replace_words(text, word_dic):
    """
    take a text and <strong class="highlight">replace</strong> <strong class="highlight">words</strong> that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, word_dic)))
    def translate(match):
        return word_dic[match.group(0)]
    return rc.sub(translate, text)

def sorted_dict_values_by_key(adict):
    L = []
    for i in sorted(adict.keys()):
        L.append(adict[i])
    return L

def sorted_dict_keys(adict):
    keys = adict.keys()
    return sorted(keys)

argmax = lambda array: max(izip(array, xrange(len(array))))[1]

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

def get_heads(mrg, outfname = None):
    """
    Calls Penn2Malt to find the lexical heads of the syntax tree contained in
     "MRG" form-style input string.
    """

    outfname = os.path.join(paths.PENN2MALT_PATH, datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) if outfname is None else outfname
    
    f_temp = open(outfname, "w")
    f_temp.write(mrg)
    f_temp.close()
    
    p = subprocess.Popen(args = ["java", "-Xmx1500m", "-jar", os.path.join(paths.PENN2MALT_PATH, "Penn2Malt.jar"), 
                                 outfname, 
                                 os.path.join(paths.PENN2MALT_PATH, "headrules.txt"), 
                                 "1", "2", "penn"], 
                         stdout = subprocess.PIPE, 
                         stderr = subprocess.STDOUT) # shell=True
    outputlines = p.stdout.readlines()
    ret_code = p.wait()

    if ret_code == 0:
        result = open(outfname + ".1.pa.gs.tab").read().split("\n\n")[:-1]
        for fname in [outfname, outfname + '.1.pa.pos', outfname + '.1.pa.dep', outfname + '.1.pa.gs.tab']:
            os.remove(fname)
            
        return result
    else:
        for fname in [outfname, outfname + '.1.pa.pos', outfname + '.1.pa.dep', outfname + '.1.pa.gs.tab']:
            if os.path.exists(fname):
                os.remove(fname)
        raise NameError("*** Penn2Malt crashed, with trace %s..." % outputlines)
        return ""

    
def get_sent_dependencies(deps):
    sent2dep_list = []
    for (i, sent_deps) in enumerate(deps):
        sent_dep_list = []
        #tree = trees[i]
        for dep_item in sent_deps.split('\n'):
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
                sent_dep_list.append(dep_item_info)

        sent2dep_list.append(sent_dep_list)
        
    return sent2dep_list

def print_SGML_tree(parse_tree, offset = 1, depth = 0, status = None, relation = None):
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
        left_relation = parse_tree.node[ : -6]
        right_relation = 'span'
    elif right_status[0] == 'S' and left_status[0] == 'N':
        right_relation = parse_tree.node[ : -6]
        left_relation = 'span'
    else:
        left_relation = parse_tree.node[ : -6]
        right_relation = left_relation
        
    out += print_SGML_tree(left, offset, depth + 1, left_status, left_relation)
    out += print_SGML_tree(right, offset + (len(left.leaves()) if isinstance(left, Tree) else 1), depth + 1, right_status, right_relation) 

    for i in range(depth):
        out += '  '
    out += ')\n'

    return out


def transform_to_shift_reduce_actions(parse_tree, relation = True, nuclearity = True, compressed = True, offset = 1):
    if not isinstance(parse_tree, Tree):
        if not compressed:
            return ['S']
        else:
            return []
    
    if nuclearity:
        rel_classes = rel_status_classes
    else:
        rel_classes = class2rel.keys()
        
    actions = []
    left = parse_tree[0]
    right = parse_tree[1]
    if isinstance(left, Tree):
        left_span = len(left.leaves())
    else:
        left_span = 1 
        
    actions.extend(transform_to_shift_reduce_actions(left, relation, nuclearity, compressed, offset))
    actions.extend(transform_to_shift_reduce_actions(right, relation, nuclearity, compressed, offset + left_span))
    
    head_action = 'R'
    if relation:
        if nuclearity:
            action = parse_tree.node
        else:
            action = parse_tree.node[ : -6]
        
        head_action += str(rel_classes.index(action))
    else:
        if nuclearity:
            action = parse_tree.node[ -6 : ]
            head_action += action
    
    if compressed:
        left_start = offset
        left_end = offset + left_span - 1
    
        right_start = left_end + 1
        if isinstance(right, Tree):
            right_span = len(right.leaves())
        else:
            right_span = 1
        right_end = right_start + right_span - 1
        
        head_action += '[(%d,%d),(%d,%d)]' % (left_start, left_end, right_start, right_end)
        
    actions.append(head_action)
    
    return actions   
    
    
    
def transform_to_ZhangShasha_tree(parse_tree, offset = 0, treepos = 0, nuclearity = True):
    edges = []
    
    if not isinstance(parse_tree, Tree):
        return edges
    
    ''' use breadth-first search '''
    if nuclearity:
        rel_classes = rel_status_classes
    else:
        rel_classes = class2rel.keys()

    rel_classes.append('NO-REL')
    
    if nuclearity:
        parent_label = parse_tree.node
    else:
        parent_label = parse_tree.node[ : -6] if parse_tree.node != 'NO-REL' else parse_tree.node
            
    parent_label = str(rel_classes.index(parent_label))
    parent_label += ':' + str(treepos)
    parent_label = parent_label.replace('-', '_')
    
    left_treepos = treepos + 1
    left = parse_tree[0]
    if not isinstance(left, Tree):
        left_label = 'e%d' % (offset + 1)
        left_span = 1
        right_treepos = treepos + 1
   
    else:
        if nuclearity:
            left_label = left.node
        else:
            left_label = left.node[ : -6] if left.node != 'NO-REL' else left.node
        
        left_label = str(rel_classes.index(left_label)) + ':' + str(left_treepos)
        left_span = len(left.leaves())
        right_treepos = treepos + len(left.treepositions()) + len(left.leaves())
                                   
    right = parse_tree[1]
    if not isinstance(right, Tree):  
        right_label = 'e%d' % (offset + 1 + left_span) 
    else:
        if nuclearity:
            right_label = right.node
        else:
            right_label = right.node[ : -6] if right.node != 'NO-REL' else right.node
            
        right_label = str(rel_classes.index(right_label)) + ':' + str(right_treepos)
    
    edges.append(parent_label + '-' + left_label)
    edges.extend(transform_to_ZhangShasha_tree(left, offset, left_treepos))
    
    edges.append(parent_label + '-' + right_label)
    edges.extend(transform_to_ZhangShasha_tree(right, offset + left_span, right_treepos))
    
    return edges



def eval_parse_prob(pt, model_probs, smoothing_prob = 0.0001, entropy = False):
    probs = 1.0
    
    for subtree in pt.subtrees():
        left_span = subtree[0]
        right_span = subtree[1]
        head_rel = subtree.node
        left_rel = left_span.node if isinstance(left_span, Tree) else 'NO-REL'
        right_rel = right_span.node if isinstance(right_span, Tree) else 'NO-REL'
        rhs = left_rel + ' ' + right_rel

        if rhs in model_probs and head_rel in model_probs[rhs]:
            prob = model_probs[rhs][head_rel]
        else:
            prob = smoothing_prob
        
        #print head_rel + '->' + rhs, prob
        if entropy:
            probs += -prob * math.log(prob)
        else:
            probs *= prob
    
    if entropy:
        return probs
    else:
        return - math.log(probs)

def get_constituents(tree, multiEDU = False, rel = False, nuclearity = False, offset = 0):
    constituents = []
    
    if not isinstance(tree, Tree) and multiEDU:
        return []
    else:
        constituents.append(('NO-REL' if rel else None, '-' if nuclearity else None, offset, offset + 1))
    
    if not isinstance(tree, Tree):
        return constituents
    
    left = tree[0]
    span = 1 if not isinstance(left, Tree) else len(left.leaves())
    right = tree[1]
    
    constituents.extend(get_constituents(left, multiEDU, rel, nuclearity, offset))
    
    constituents.extend(get_constituents(right, multiEDU, rel, nuclearity, offset + span))
    
    constituents.append((tree.node[ : -6] if rel else None, tree.node[-6 : ] if nuclearity else None, offset, offset + len(tree.leaves())))
    
    return constituents

def get_constituent_accuracy(tree1, tree2, multiEDU = False, rel = False, nuclearity = False):
    cons1 = set(get_constituents(tree1, multiEDU, rel, nuclearity))
    cons2 = set(get_constituents(tree2, multiEDU, rel, nuclearity))
    
    return len(cons1.intersection(cons2)) * 100.0 / len(cons1)
    
    
def eval_pt_distance(rst_edges, pt_edges):
    p = subprocess.Popen(args = ["java", "-classpath", "../../tools/treedistance/treedistance.jar", 
                                     "headliner.treedistance.TestZhangShasha",
                                     ';'.join(rst_edges), ';'.join(pt_edges)], 
                         stdout = subprocess.PIPE, 
                         stderr = subprocess.STDOUT) # shell=True
    outputlines = p.stdout.readlines()
    ret_code = p.wait()
    
    dist = float(outputlines[-1].strip().split(':')[-1])
    
    return dist

def is_within_sentence(pair):
    if not isinstance(pair, Tree):
        return True
    
    for i in range(len(pair.leaves()) - 1):
        leaf = pair.leaves()[i]
        if '<s>' in leaf or '<p>' in leaf:
            return False
        
    return True


def contains_stump(pair_treepos, stump_treepos):
    #print 'stump_treepos:', stump_treepos
    #print 'pair_treepos:', pair_treepos
    if stump_treepos.startswith(pair_treepos):
        return True
    else:
        return False        
    
    
def get_adjacent_stump(prev_tree, i, scope, pos = 'L'):
#    print 'i:', i, 'pos:', pos, 'scope:', scope
    
    if i < 1 and pos == 'L':
        return None
    elif i > len(prev_tree.leaves()) - 2 and pos == 'R':
        return None
    
    stump_treepos = ''.join(str(x) for x in prev_tree.leaf_treeposition(i))
    
    #print i, len(self.prev_tree.leaves())
    if pos == 'L':
        treepos = prev_tree.treeposition_spanning_leaves(i - 1, i)
    else:
        treepos = prev_tree.treeposition_spanning_leaves(i + 1, i + 2)
        
    prev_pair = prev_tree[treepos]
    #print prev_pair
    prev_scope = is_within_sentence(prev_pair)
    #print 'prev_pair:', prev_pair
    #print 'prev_scope:', prev_scope
    
    if (not prev_scope and scope) or contains_stump(''.join(str(x) for x in treepos), stump_treepos):
        return None
    else:
        while len(treepos) > 0:
            parent_treepos = treepos[ : -1]
            parent_prev_pair = prev_tree[parent_treepos]
            parent_prev_scope = is_within_sentence(parent_prev_pair)
            #print 'parent_prev_pair:', parent_prev_pair
            #print 'parent_prev_scope:', parent_prev_scope
            
            if (not parent_prev_scope and scope) or contains_stump(''.join(str(x) for x in parent_treepos), stump_treepos):
                break
            
            treepos = parent_treepos
            
#            if not parent_prev_scope and not scope:
#                break
            
            
    
    prev_pair = prev_tree[treepos]
    prev_scope = is_within_sentence(prev_pair)
    #print 'prev_pair:', prev_pair
    #print 'prev_scope:', prev_scope
    
    if prev_scope != scope:
        return None
    else:
        return prev_pair
    
    
def get_context_stumps(prev_tree, stumps, pair, i):
    scope = is_within_sentence(pair)
    #print 'scope:', scope
    
    tot = 0
    for j in range(i):
        stump = stumps[j]
        if isinstance(stump, Tree):
            tot += len(stump.leaves())
        else:
            tot += 1
    
    #print 'L:', pair[0]
    prev_stump = get_adjacent_stump(prev_tree, tot, scope, 'L')
    #print 'prev:', prev_stump
    #print
    
    #print 'R:', pair[1]
    next_stump = get_adjacent_stump(prev_tree, tot + (1 if not isinstance(pair, ParseTree) else len(pair.leaves())) - 1, scope, 'R')
    #print 'next:', next_stump
    #print
            
    return (prev_stump, next_stump)

def copy_stump(stump, detach = False):
    if isinstance(stump, Tree):
        result = stump.__deepcopy__()
        if detach:
            result._parent = None
    else:
        result = stump
    
    return result

def make_new_stump(label, stump1, stump2):
#    stump1 = copy_stump(left, True)
#    stump2 = copy_stump(right, True)
    
    if isinstance(stump1, ParseTree):
        stump1._parent = None
        
    if isinstance(stump2, ParseTree):
        stump2._parent = None
        
    return ParseTree(label, [stump1, stump2])


def edu_in_sentence(cuts, start):
    #print cuts
    #print 'start:', start
    tot = 0
    for i in range(len(cuts)):
        if start < tot + len(cuts[i]):
#                print i, start - tot
            return i, start - tot
    
        tot += len(cuts[i])
    
    return -1, -1


def align_edus_with_syntax_trees(input_edus, lexicalized_trees, segmented_text, special_chars = None):
    edus_intervals_pairs = []
    edus = []
    
    edus_offset = 0
    for i in range(0, len(lexicalized_trees)):
        t = lexicalized_trees[i]
        
        t_words = map(lambda x: t.unescape(x), t.leaves())
        
        l = j = k = m = 0
        cur_edus_intervals = [0]
        #cur_edu_words = input_edus[edus_offset].lower().split(' ')
        cur_edu_words = input_edus[edus_offset].split(' ')
        
        #print 't_words:', t_words
        #print 'cur_edu_words:', cur_edu_words
        while l < len(t_words):
            if t_words[l] == '.' and l > 0 and t_words[l - 1].endswith('.'):
                l += 1
                continue
            
            if special_chars:
                prefix = replace_words(t_words[l][m : ], special_chars)
            else:
                prefix = t_words[l][m : ]
                
            #print 'l:', l, 'm:', m, 't_words[l][m : ]:', t_words[l][m : ], 'prefix:', prefix
            #print 'k:', k, 'j:', j, 'cur_edu_words[j][k : ]:', cur_edu_words[j][k : ]
            
            if prefix == cur_edu_words[j][k : ]:
                l += 1
                j += 1
                k = 0
                m = 0
            elif cur_edu_words[j][k : ].startswith(prefix):
                k += len(prefix)
                l += 1
                m = 0
                
                if k == len(cur_edu_words[j]):
                    k = 0
                    j += 1
            elif prefix.startswith(cur_edu_words[j][k : ]):
                m += len(cur_edu_words[j][k : ])
                if t_words[l][m] == ' ':
                    m += 1
                    
                j += 1
                k = 0
                
                if m >= len(t_words[l]):
                    m = 0
                    l += 1
            else:
                print 't_words:', t_words
                print 'cur_edu_words:', cur_edu_words
                print 'l:', l, 'm:', m, 't_words[l][m : ]:', t_words[l][m : ], 'prefix:', prefix
                print 'k:', k, 'j:', j, 'cur_edu_words[j][k : ]:', cur_edu_words[j][k : ]
                raise Exception('cannot align input edus with text file.')
                
            if j == len(cur_edu_words) or l == len(t_words):
                edus_offset += 1
                cur_edus_intervals.append(l)
                if edus_offset == len(input_edus):
                    if l == len(t_words):
                        break
                    else:
                        raise Exception('cannot align input edus with text file.')
                
                k = 0
                j = 0
                #cur_edu_words = input_edus[edus_offset].lower().split(' ')
                cur_edu_words = input_edus[edus_offset].split(' ')
                #print cur_edu_words
        
        #print cur_edus_intervals
        cur_edus = []
        cur_edus_intervals_pairs = []
                
        for j in range(0, len(cur_edus_intervals) - 1):
            cur_edus.append(t_words[cur_edus_intervals[j]:cur_edus_intervals[j+1]])
            cur_edus_intervals_pairs.append((cur_edus_intervals[j], cur_edus_intervals[j+1]))
            
        # Add eventual paragraph boundary
        #if segmented_text[i][1] == True:
            #cur_edus[len(cur_edus) - 1].append("<p>") 
        #print segmented_text[i][1]
        cur_edus[len(cur_edus) - 1].append(segmented_text[i][1]) 
        
        #print 'cur_edus', cur_edus
        edus_intervals_pairs.append(cur_edus_intervals_pairs)
        edus.extend(cur_edus)
    
    return edus, edus_intervals_pairs

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