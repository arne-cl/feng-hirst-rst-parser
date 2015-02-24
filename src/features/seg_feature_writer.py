'''
Created on 2013-02-18

@author: Vanessa Wei Feng
'''
import os
import time
import re

import paths
import utils.serialize
import utils.utils
from features.feature_space import FeatureSpace


class SegFeatureWriter:   


    def __init__(self, verbose=False):

        self.words_dict = map(lambda x: x[0], utils.serialize.loadData("1-grams_dict_hugo")[0])
        self.verbose = verbose
        
        if self.verbose:
            print "Loaded word dictionary (%s words)" % len(self.words_dict)
        
        self.inv_words_dict = {}
        for i in range(0, len(self.words_dict)):
            self.inv_words_dict[i] = self.words_dict[i]
            
    
        self.pos_dict = utils.serialize.loadData("syntactic_labels_simplified")
        if self.verbose:
            print "Loaded simplified syntactic labels dictionary (%s words)" % len(self.pos_dict)
        
        self.inv_pos_dict = {}
        for i in range(0, len(self.pos_dict)):
            self.inv_pos_dict[i] = self.pos_dict[i]
            
        
        # Ordered by decreasing length...
        self.discourse_cues_dict = sorted(utils.serialize.loadData("discourse_cues"), lambda x, y: len(y) - len(x))
        if self.verbose:
            print "Loaded discourse cues dictionary (%s words)" % len(self.discourse_cues_dict)
        
        self.inv_discourse_cues_dict = {}
        for i in range(0, len(self.discourse_cues_dict)):
            self.inv_discourse_cues_dict[i] = self.discourse_cues_dict[i]    
        
        if self.verbose:
            print "Feature writer loaded"
        

        
        
    def get_word_context(self, leaf_index, t):
        """
        Returns the "context" of a word (identified by its leaf index) in a lexicalized tree
        """
    
        # Pos of w in the tree
        w_leaf_position = t.leaf_treeposition(leaf_index)
        
        start = t
        for i in w_leaf_position[:-1]:
            start = start[i]
        
        Nw = start
        
        #print Nw.parent()
        while Nw.parent != None and Nw.parent.parent != None and t.leaves()[Nw.parent.head] == t.leaves()[leaf_index] and Nw.parent.right_sibling != None:
            Nw = Nw.parent
        
    
        pos_nw = Nw.node
        pos_np = Nw.parent.node
        pos_nr = None
        head_nw = t.unescape(t.leaves()[Nw.head])
        head_np = t.unescape(t.leaves()[Nw.parent.head])
        head_nr = None
        
        if not Nw.right_sibling == None:
            pos_nr = Nw.right_sibling.node
            head_nr = t.unescape(t.leaves()[Nw.right_sibling.head])
         
        return tuple(map(lambda x: utils.utils.simplified_tag(x), [pos_nw, head_nw, pos_np, head_np, pos_nr, head_nr]))
    
    
    def extract_features(self, trees, align_with_string = None):
        """
        Extract features from a list of lexicalized trees (representing a text)
        If a string containing EDU cuts is given as extra parameter, training features are returned
        """

     
        result = []
         
        features = FeatureSpace()
        
        features.add_group("_____POS_tag_previous_word", len(self.pos_dict), self.inv_pos_dict)
        features.add_group("_____POS_tag_current_word", len(self.pos_dict), self.inv_pos_dict)
        features.add_group("_____POS_tag_next_word", len(self.pos_dict), self.inv_pos_dict)
        
        features.add_group("____POS_tag_ancestor_previous_current_word", len(self.pos_dict), self.inv_pos_dict)
        features.add_group("____POS_tag_ancestor_current_next_word", len(self.pos_dict), self.inv_pos_dict)
        
        features.add_group("____next_word_discourse_cue", len(self.discourse_cues_dict), self.inv_discourse_cues_dict)
        
        features.add_group("___POS_tag_Nw", len(self.pos_dict), self.inv_pos_dict)
        features.add_group("___head_Nw", len(self.words_dict), self.inv_words_dict)
        features.add_group("__POS_tag_Np", len(self.pos_dict), self.inv_pos_dict)
        features.add_group("__head_Np", len(self.words_dict), self.inv_words_dict)
        features.add_group("_POS_tag_Nr", len(self.pos_dict), self.inv_pos_dict)
        features.add_group("_head_Nr", len(self.words_dict), self.inv_words_dict)
        
    
        parse_pos = 0
        
        
        # Oh yeah.
        trees_words = map(lambda x: trees[0].unescape(x), reduce(lambda x, y: x+y, map(lambda x: x.leaves(), trees)))
        
        word_index = 0
        word_trace = ""
        
        for t in trees:
            
            cnt = 0
            
            for w in t.leaves():

                is_edu_boundary = False
                if align_with_string:
                    
                    ### DETERMINING IF WORD IS A EDU BOUNDARY #############################################
                    ### PARALLEL READING OF PTB AND DT
                    
                    w_pre_regex = trees_words[word_index]
                    
                    word_trace = word_trace + w_pre_regex + " "
                    
                    
                    # Hacks I
                    if w_pre_regex == "``" or w_pre_regex == "''":
                        w_pre_regex = "\""

                    # Escape regex metacharacters so the word can be searched
                    w_lookup_regex = w_pre_regex.replace("\\", u"\\\\").replace(".", u"\.").replace("^", u"\^").replace("$", u"\$").replace("*",u"\*").replace("+", u"\+").replace("?", u"\?").replace("{",u"\{").replace("}", u"\}").replace("[",u"\[").replace("]",u"\]").replace("|", u"\|").replace("(", u"\(").replace(")", u"\)")
                    
                    
                    # Hacks II
                    # Also treats cases like `` and '' (PTB) which are " in the DT.
                    # Other annoying case : "..." in PTB rendered as ". . ." in DT
        #                if w_regex == "``":
        #                    w_regex = "\""
        #                elif w_regex == "''":
        #                    w_regex = "\""
                    if w_lookup_regex == "\.\.\.":
                        w_lookup_regex = "(\.\.\.|\.\s\.\s\.)"
                    if w_lookup_regex == "`":
                        w_lookup_regex = "(`|')"
                    if w_lookup_regex == "s\.p\.a\.": # This comes back often
                        w_lookup_regex = "(s\.p\.a\.|s\.p\.\sa\.)"
        #                if w_lookup_regex == "\." and word_index > 0:
        #                    if trees_words[word_index-1] == "u.s.":
        #                        print "Skipping USA!"
        #                        cnt = cnt + 1
        #                        word_index = word_index + 1
        #                        continue
                    

                    m = re.match(r"\s*?.*?" + w_lookup_regex + "\s*", align_with_string[parse_pos:])
                    
                    if m:
                        parse_pos = parse_pos + len(m.group(0))
                        if m.group(0).find("\n") != -1:
                            is_edu_boundary = True
                    else:
                        print align_with_string[parse_pos:]
                        t.draw()
                        print "Oops, couldn't match the .edu file and PTB tree for %s, faulty word is %s (was searched with regex %s). Word trace is %s" % (w, w_pre_regex, w_lookup_regex, word_trace)
                        raise Exception
                
                
                ### FEATURE EXTRACTION ##################################################################################

                (pos_nw, head_nw, pos_np, head_np, pos_nr, head_nr) = self.get_word_context(cnt, t)
                
    
                # Previous, current, next word's POS
                if cnt != 0:
                    prev_w_path = list(t.leaf_treeposition(cnt-1))
                    prev_w_pos = utils.utils.simplified_tag(reduce(lambda x,y: x[y], [t] + prev_w_path[:-1]).node)
                    if prev_w_pos in self.pos_dict:
                        features["_____POS_tag_previous_word"][self.pos_dict.index(prev_w_pos)] = 1
    #                print "POS tag previous word: %s" % prev_w_pos
                else:
                    prev_w_path = None
             
                cur_w_path = list(t.leaf_treeposition(cnt))
                cur_w_pos = utils.utils.simplified_tag(reduce(lambda x,y: x[y], [t] + cur_w_path[:-1]).node)
                if cur_w_pos in self.pos_dict:
                    features["_____POS_tag_current_word"][self.pos_dict.index(cur_w_pos)] = 1
    #            print "POS tag cur word: %s" % cur_w_pos
                
                if cnt + 1 < len(t.leaves()):
                    next_w_path = list(t.leaf_treeposition(cnt+1))
                    next_w_pos = utils.utils.simplified_tag(reduce(lambda x,y: x[y], [t] + next_w_path[:-1]).node)
                    if next_w_pos in self.pos_dict:
                        features["_____POS_tag_next_word"][self.pos_dict.index(next_w_pos)] = 1
    #                print "POS tag next word: %s" % next_w_pos
                else:
                    next_w_path = None
                    
                
                # Common ancestor of current and next word's POS
                
                if not prev_w_path == None:
                    prev_cur_anc_path = []
                    i = 0
                    while prev_w_path[i] == cur_w_path[i]:
                        prev_cur_anc_path.append(prev_w_path[i])
                        i=i+1
                        
                    prev_cur_anc_pos = utils.utils.simplified_tag(reduce(lambda x,y: x[y], [t] + prev_cur_anc_path).node)
                    
                    if prev_cur_anc_pos in self.pos_dict:
                        features["____POS_tag_ancestor_previous_current_word"][self.pos_dict.index(prev_cur_anc_pos)] = 1
    #                print "pos of previous+current ancestor: %s" % prev_cur_anc_pos
    
                if not next_w_path == None:
                    cur_next_anc_path = []
                    i = 0
                    while cur_w_path[i] == next_w_path[i] and i + 1 < len(t.leaves()):
                        cur_next_anc_path.append(cur_w_path[i])
                        i=i+1
                        
                    cur_next_anc_pos = utils.utils.simplified_tag(reduce(lambda x,y: x[y], [t] + cur_next_anc_path).node)
                    
                    if cur_next_anc_pos in self.pos_dict:
                        features["____POS_tag_ancestor_current_next_word"][self.pos_dict.index(utils.utils.simplified_tag(cur_next_anc_pos))] = 1
    #                print "pos of current+next ancestor: %s" % cur_next_anc_pos
    
    
    
                # Is next word a discourse cue?
                next_leaves = map(lambda x: t.unescape(x), t.leaves()[cnt+1:])
                
                for c in self.discourse_cues_dict:
                    if next_leaves[:len(c)] == c:
                        features["____next_word_discourse_cue"][self.discourse_cues_dict.index(c)] = 1
    #                    print "cur word %s, next word is the discourse cue %s" % (w, c)
    
    
                # Soricut & Marcu-style features
                if pos_nw in self.pos_dict:
                    features["___POS_tag_Nw"][self.pos_dict.index(pos_nw)] = 1
                
                if head_nw in self.words_dict:
                    features["___head_Nw"][self.words_dict.index(head_nw)] = 1
    
                if pos_np in self.pos_dict:
                    features["__POS_tag_Np"][self.pos_dict.index(pos_np)] = 1
                
                if head_np in self.words_dict:
                    features["__head_Np"][self.words_dict.index(head_np)] = 1
                
                if not pos_nr == None:
                    if pos_nr in self.pos_dict:
                        features["_POS_tag_Nr"][self.pos_dict.index(pos_nr)] = 1
                    
                    if head_nr in self.words_dict:
                        features["_head_Nr"][self.words_dict.index(head_nr)] = 1
    
                # Some distances
                features["pos_in_sentence"] = cnt
                features["pos_in_text"] = word_index
                features["relative_pos_in_sentence"] = float(cnt)/float(len(t.leaves()))
                
  
                class_sign = 0
                
                if not align_with_string == None:
                    if is_edu_boundary:
                        class_sign = 1
                    else:
                        class_sign = -1

                result.append("%i\t%s" % (class_sign, features.get_full_vector()))
                
                features.reset()
                    
                cnt = cnt + 1
                word_index = word_index + 1
            
        return result