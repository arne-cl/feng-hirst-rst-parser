'''
Created on Feb 19, 2013

Original codes from Hilda
'''

import re

from nltk.tree import Tree
from utils.rst_lib import *
from feature_space import FeatureSpace
from trees.lexicalized_tree import LexicalizedTree
from utils.cue_phrases import cue_phrases as cue_phrases_array

import utils.serialize
import utils.utils

from utils.Stanford_Deps import stanford_dep_types

class TreeFeatureWriter:
    
    
    def __init__(self, verbose=False):
        
        self.ngram_len = 3
        self.nb_sentence_parts = 4
        self.nb_syntactic_tags = 3
        self.RST_Tree_depth = 3
        
        self.strong_sentence_bound = re.compile('\.')
        
        self.ngrams_dict = utils.serialize.loadData("n-grams_dict")
        
        if verbose:
            print "Loaded ngram dict: " + str(len(self.ngrams_dict))
        
        self.features = FeatureSpace()
        
        self.inv_ngrams_dict = {}
        for i in sorted(self.ngrams_dict):
            self.inv_ngrams_dict[self.ngrams_dict[i]] = i 
        
        #self.features.add_group('__L_ngrams', len(self.ngrams_dict), self.inv_ngrams_dict)
        #self.features.add_group('__R_ngrams', len(self.ngrams_dict), self.inv_ngrams_dict)
        self.features.add_group('___L_ngrams_pref', len(self.ngrams_dict), self.inv_ngrams_dict)
        self.features.add_group('___R_ngrams_pref', len(self.ngrams_dict), self.inv_ngrams_dict)
        self.features.add_group('___L_ngrams_suf', len(self.ngrams_dict), self.inv_ngrams_dict)
        self.features.add_group('___R_ngrams_suf', len(self.ngrams_dict), self.inv_ngrams_dict)
        
        self.features.add_group('___L_main_ngrams_pref', len(self.ngrams_dict), self.inv_ngrams_dict)
        self.features.add_group('___R_main_ngrams_pref', len(self.ngrams_dict), self.inv_ngrams_dict)
        self.features.add_group('___L_main_ngrams_suf', len(self.ngrams_dict), self.inv_ngrams_dict)
        self.features.add_group('___R_main_ngrams_suf', len(self.ngrams_dict), self.inv_ngrams_dict)
        
        
        self.relations = utils.serialize.loadData("rels_list")
        self.relations_no_nuclearity = []
        if verbose:
            print "Loaded relation list: " + str(len(self.relations))
        self.relations['NO-REL'] = len(self.relations)+1
        for relation in self.relations:
            plain_relation = relation[ : -6]
            if plain_relation not in self.relations_no_nuclearity:
                self.relations_no_nuclearity.append(plain_relation)
        
        self.tree_size = 2**(self.RST_Tree_depth+1)-1
        
        self.RST_legend = {}
        self.inv_relations = {}
        for i in sorted(self.relations):
            self.inv_relations[self.relations[i]] = i 
        
        
        for i in range(0, self.tree_size):
            for j in range(0,len(self.inv_relations)):
                self.RST_legend[(i*len(self.inv_relations))+j] = str(i) + "][" + self.inv_relations[j+1]
                
        self.features.add_group('_L_RST_Tree', len(self.relations) * self.tree_size, self.RST_legend)
        self.features.add_group('_R_RST_Tree', len(self.relations) * self.tree_size, self.RST_legend)
        
        self.inv_syntactic_tags = utils.serialize.loadData("syntactic_labels")
        if verbose:
            print "Loaded syntactic_tags list: ", len(self.inv_syntactic_tags)
        
        self.syntactic_legend = {}
        self.syntactic_tags = {}
        self.inv_syntactic_tags.insert(0, 'none')
        for (i, tag) in enumerate(self.inv_syntactic_tags):
            self.syntactic_tags[tag] = i 
        
        for i in range(0, self.nb_syntactic_tags):
            for j in range(0, len(self.inv_syntactic_tags)):
                self.syntactic_legend[i*len(self.inv_syntactic_tags)+j] = str(i) + "][" + self.inv_syntactic_tags[j]
        
        self.features.add_group('_Syntactic_tags_pref_L', len(self.syntactic_tags)*self.nb_syntactic_tags, self.syntactic_legend)
        self.features.add_group('_Syntactic_tags_pref_R', len(self.syntactic_tags)*self.nb_syntactic_tags, self.syntactic_legend)
        self.features.add_group('_Syntactic_tags_suf_L', len(self.syntactic_tags)*self.nb_syntactic_tags, self.syntactic_legend)
        self.features.add_group('_Syntactic_tags_suf_R', len(self.syntactic_tags)*self.nb_syntactic_tags, self.syntactic_legend)
        
        self.features.add_group('_Top_Syntactic_tag_L', len(self.syntactic_tags), self.syntactic_legend)
        self.features.add_group('_Top_Syntactic_tag_R', len(self.syntactic_tags), self.syntactic_legend)
        self.features.add_group('_Dominated_Syntactic_tag', len(self.syntactic_tags), self.syntactic_legend)
        
        
        self.inv_lexical_heads = utils.serialize.loadData("lexical_heads")
        if verbose:
            print "Loaded lexical_heads list: ", len(self.inv_lexical_heads)
        
        self.lexical_heads = {}
        self.lexical_heads_legend = {}
        for (i, tag) in enumerate(self.inv_lexical_heads):
            self.lexical_heads[tag] = i 
            self.lexical_heads_legend[i] = tag
        
        self.features.add_group('___Top_lexical_head_L', len(self.lexical_heads), self.lexical_heads_legend)
        self.features.add_group('___Top_lexical_head_R', len(self.lexical_heads), self.lexical_heads_legend)
        self.features.add_group('___Dominated_lexical_head', len(self.lexical_heads), self.lexical_heads_legend)
        
        '''cue_phrases = {}
        for (index, cue) in enumerate(cue_phrases_array):
            cue_phrases[index] = cue
            
        #print "Loaded cue_phrases: ", len(cue_phrases)
        #for i in range(0, nb_sentence_parts):
        #    self.features.add_group('_Cue_Phrases_L_' + str(i), len(cue_phrases), cue_phrases)
        #    self.features.add_group('_Cue_Phrases_R_' + str(i), len(cue_phrases), cue_phrases)
        '''
        
        self.counter = 0


        
    def add_ngram(self, feature_name, ngram):
        if ngram in self.ngrams_dict:
            self.features[feature_name][self.ngrams_dict[ngram]] = 1
            #   print feature_name + "\t\t" + ngram
            
    def bin_array_to_int(self, arr):
        def bin_add(x, y): return x*2+y
        return reduce(bin_add, reversed(arr), 0)
    
    def add_subnode_rst(self, T, path, array):
        i = (self.bin_array_to_int(path) + 2**len(path) - 1) * len(self.relations)
        if isinstance(T, Tree):
            if hasattr(T, 'probs'):
                for (j, prob) in enumerate(T.probs):
                    # debug
                    if j >= len(self.relations):
                        print "ERROR", j
                        print T.probs
                        exit(-1)
                    array[i+j] = prob
            else:
                array[i + self.relations[T.node] - 1] = 1
        else:
            array[i + self.relations['NO-REL'] - 1] = 1
    
    def write_position_features(self, syntax_trees, breaks, num_edus, suffix, start_i, start_j):
        exclude_words = ".`':;!?"
        
        if start_i >= len(breaks):
            print start_i
            print breaks
        if start_j >= len(breaks[start_i]):
            print start_i, start_j
            print breaks[start_i]
            print breaks

        #print 'start_i', start_i
        #print syntax_trees[start_i]
        #print breaks, start_i, start_j
        #print breaks[start_i][start_j]
        start_word = breaks[start_i][start_j][0]
        #print len(syntax_trees[start_i].leaves())
        #print ' '.join(syntax_trees[start_i].leaves())

        while start_word < len(syntax_trees[start_i].leaves()) and not syntax_trees[start_i].leaves()[start_word].strip(exclude_words):
            start_word += 1
        
        #print 'start_word: ', start_word
        #print syntax_trees[start_i].leaves()

        tot = 0
        i = start_i
        j = start_j
        
        # end_i, end_j are *inclusive*
        while tot < num_edus:
            end_i = i
            end_j = j
            #from_syntax_tree += syntax_trees[i].leaves()[breaks[i][j][0]:breaks[i][j][1]]
            tot += 1
            j += 1
            if j >= len(breaks[i]):
                i+=1
                j = 0
    
        end_word = min(breaks[end_i][end_j][1], len(syntax_trees[end_i].leaves()))
       
        if end_i == start_i:
            while (syntax_trees[start_i].leaves()[end_word-1] == '<s>'
                   or syntax_trees[start_i].leaves()[end_word-1] == '<p>'
                   or not syntax_trees[start_i].leaves()[end_word-1].strip(exclude_words)):
                end_word -= 1
            self.features['Inside_sentence_' + suffix] = 1
            self.features['Sentence_EDUs_cover_' + suffix] = float(end_j - start_j)/len(breaks[start_i])
            self.features['Sentence_tokens_cover_' + suffix] = float(breaks[end_i][end_j][0]-breaks[end_i][end_j][1])/len(syntax_trees[start_i].leaves())
            if start_word >= end_word: ### DEBUG
                real = min(breaks[end_i][end_j][1], len(syntax_trees[end_i].leaves()))
                print start_word, real, "->", end_word
                print breaks[end_i][end_j]
                print syntax_trees[start_i].leaves()[start_word:]
                print real
                print syntax_trees[start_i].leaves()[end_word:real]
                #start_word = breaks[end_i][end_j][0]
                #end_word = breaks[end_i][end_j][1]
                
                '''print breaks
                print start_i, breaks[start_i]
                print syntax_trees[start_i]
                print ' '.join(syntax_trees[start_i].leaves()), start_word, end_word'''
            ancestor_pos = syntax_trees[start_i].treeposition_spanning_leaves(start_word, end_word)
        else:
            self.features['Inside_sentence_' + suffix] = 0
            self.features['Sentence_EDUs_cover_' + suffix] = 0
            self.features['Sentence_tokens_cover_' + suffix] = 0
            ancestor_pos = ()
    
        self.features['Ancestor_pos_' + suffix] = len(ancestor_pos)
            
        self.features['Sentence_span_' + suffix] = end_i - start_i
        
        self.features['Dist_EDU_to_sent_start_' + suffix] = start_j
        self.features['Dist_EDU_to_sent_end_' + suffix] = len(breaks[end_i]) - end_j - 1
    
        self.features['Dist_S_to_text_start_' + suffix] = start_i
        self.features['Dist_S_to_text_end_' + suffix] = len(breaks) - start_i - 1
        
        
        for i in range(0, self.nb_syntactic_tags):
            if start_word+i < len(syntax_trees[start_i].leaves()):
                tag = syntax_trees[start_i][syntax_trees[start_i].leaf_treeposition(start_word+i)[:-1]].node
                # HUGO WUZ HERE
                filtag = filter_syntactic_tag(tag)
                if filtag in self.syntactic_tags:
                    tag_id = self.syntactic_tags[filtag]
                else:
                    tag_id = 0
            else:
                tag_id = 0
                if i == 0: ### DEBUG
                    print "ERROR"
                    exit(-1)
            self.features['_Syntactic_tags_pref_' + suffix][i*len(self.syntactic_tags)+tag_id] = 1
            #print tag, i*len(syntactic_tags)+tag_id
            
            # HUGO WUZ HERE TOO
            if end_word-i > 0 :
                tag = syntax_trees[end_i][syntax_trees[end_i].leaf_treeposition(end_word-i-1)[:-1]].node
                filtag = filter_syntactic_tag(tag)
                if filtag in self.syntactic_tags:
                    tag_id = self.syntactic_tags[filter_syntactic_tag(tag)]
                else:
                    tag_id = 0
            else:
                tag_id = 0
            self.features['_Syntactic_tags_suf_' + suffix][i*len(self.syntactic_tags)+tag_id] = 1
            #print tag, i*len(syntactic_tags)+tag_id
            
        return (end_i, end_j, end_word, ancestor_pos)    
    
    def write_syntactic_features(self, start_i, start_word, end_i, end_word, syntax_trees, suffix):
   
        for i in range(0, self.nb_syntactic_tags):
            if start_word+i < len(syntax_trees[start_i].leaves()):
                tag = syntax_trees[start_i][syntax_trees[start_i].leaf_treeposition(start_word+i)[:-1]].node
                tag_id = self.syntactic_tags[filter_syntactic_tag(tag)]
    
            self.features['_Syntactic_tags_pref_' + suffix][i*len(self.syntactic_tags)+tag_id] = 1
            #print tag, i*len(syntactic_tags)+tag_id
            
            if end_word-i > 0:
                tag = syntax_trees[end_i][syntax_trees[end_i].leaf_treeposition(end_word-i-1)[:-1]].node
                tag_id = self.syntactic_tags[filter_syntactic_tag(tag)]
            else:
                tag_id = 0
            self.features['_Syntactic_tags_suf_' + suffix][i*len(self.syntactic_tags)+tag_id] = 1
            #print tag, i*len(syntactic_tags)+tag_id
    
    
    def write_string_comparison_features(self, str_array_L, str_array_R, feature_name):
        common = set(str_array_L).intersection(set(str_array_R))
        self.features[feature_name + '_L'] = float(len(common))/len(str_array_L)
        self.features[feature_name + '_R'] = float(len(common))/len(str_array_R)
    

    def write_main_nucleus_features(self, full_array, full_tree, suffix):
        if isinstance(full_tree, Tree):
            if suffix == 'L':
                main_pos = get_main_edus(full_tree)[-1]
            else:
                main_pos = get_main_edus(full_tree)[0]
            
            #print main_pos
            (main, main_num_edus, junk) = get_concat_text(full_tree[main_pos])
            start = full_tree.count_left_of(main_pos)
            ### add more main self.features
            #self.features['Num_main_' + suffix] = len(main_pos)
        else:
            (main, main_num_edus, junk) = (full_array, 1, 0)
            start = 0
            #self.features['Num_main_' + suffix] = 0
    
        for n in range(1, self.ngram_len+1):
            self.add_ngram('___' + suffix + '_main_ngrams_pref', get_one_ngram(main, n))
            self.add_ngram('___' + suffix + '_main_ngrams_suf', get_one_ngram(main, -n))
            
        return start
    

    def write_instance(self, mc_output, bin_output, L, full_tree, syntax_trees, breaks, offsetL, offsetR = 0):
        #print 'L[0]', L[0]
        #print 'L[1]', L[1]

        self.counter += 1
        if (self.counter % 1000 == 0):
            print "#", self.counter
                    
        (left, left_num_edus, left_height) = get_concat_text(L[0])
        (right, right_num_edus, right_height) = get_concat_text(L[1])
    
        self.features.reset()

        
        # GENERAL self.features:
        self.features['Len_L'] = len(left);
        self.features['Len_R'] = len(right);
        self.features['Num_edus_L'] = left_num_edus;
        self.features['Num_edus_R'] = right_num_edus;
    
        #write_string_comparison_self.features(left, right, 'Common_words')
        
        # CUE PHRASES:
        '''left_str = " ".join(left)
        right_str = " ".join(right)
        for (index, cue) in enumerate(cue_phrases_array):
            pos = left_str.find(cue)
            if pos >= 0:
                sent_part = int(nb_sentence_parts * float(pos)/(len(left_str)-len(cue)+1))
                self.features['_Cue_Phrases_L_' + str(sent_part)][index] = 1
            pos = right_str.find(cue)
            if pos >= 0:
                sent_part = int(nb_sentence_parts * float(pos)/(len(right_str)-len(cue)+1))
                self.features['_Cue_Phrases_R_' + str(sent_part)][index] = 1
        '''
        
        # SYNTACTIC self.features
        #print 'offsetL', offsetL
        tot = 0
        for (i, sent_breaks) in enumerate(breaks):
            #print tot, i, sent_breaks
            if tot + len(sent_breaks) > offsetL:
                break;
            tot += len(sent_breaks)
    
        l_start_i = i
        l_start_j = j = offsetL - tot
        #print 'l_start_i', l_start_i
        #print 'l_start_j', l_start_j
        ####
        (l_end_i, l_end_j, l_end_word, l_ancestor_pos) = self.write_position_features(syntax_trees, breaks, left_num_edus,
                                                                     'L', l_start_i, l_start_j)
        #print 'l_end_i', l_end_i
        #print 'l_end_j', l_end_j
        #print 'l_end_word', l_end_word
        #print 'l_ancestor_pos', l_ancestor_pos
        #print 'offsetR', offsetR
        if offsetR == 0:
            if l_end_j + 1 >= len(breaks[l_end_i]):
                if l_end_i + 1 >= len(syntax_trees): ### DEBUG
                    print "\n#####\n\n"
                    print offsetL
                    print breaks
                    print "\n\n####", l_end_i, l_end_j
                    print breaks[l_end_i]
                    print left
                    print "i: ", l_start_i, l_end_i, "j: ", l_start_j, l_end_j
                    print right
                    print syntax_trees[l_start_i].leaves()
                    print syntax_trees[l_start_i].leaves()[breaks[l_start_i][l_start_j][0]:breaks[l_start_i][l_start_j][1]]
                    print syntax_trees[l_start_i].leaves()[breaks[l_start_i][l_start_j][0]:l_end_word]
                    
                r_start_i = l_end_i + 1
                r_start_j = 0
            else:
                r_start_i = l_end_i
                r_start_j = l_end_j + 1
        else:
            tot = 0
            for (i, sent_breaks) in enumerate(breaks):
                if tot + len(sent_breaks) > offsetR:
                    break;
                tot += len(sent_breaks)
            r_start_i = i
            r_start_j = j = offsetR - tot
            
        (r_end_i, r_end_j, r_end_word, r_ancestor_pos) = self.write_position_features(syntax_trees, breaks, right_num_edus,
                                                                     'R', r_start_i, r_start_j)
    
        if l_start_i == r_end_i:
            self.features['Within_same_sentence'] = 1
            self.features['Within_same_ext_sentence'] = 1
            self.features['Sentence_EDUs_cover_RL'] = float(r_end_j-l_start_j)/len(breaks[l_start_i])
            self.features['Sentence_tokens_cover_RL'] = float(len(left)+len(right))/len(syntax_trees[l_start_i].leaves())
            common_ancestor_pos = common_ancestor(l_ancestor_pos, r_ancestor_pos)
        else:
            self.features['Within_same_sentence'] = 0
            self.features['Sentence_EDUs_cover_RL'] = 0
            self.features['Sentence_tokens_cover_RL'] = 0
            common_ancestor_pos = ()
            if (not self.strong_sentence_bound.search(" ".join(left)) is None
                and self.strong_sentence_bound.search(" ".join(right)) is None):
                self.features['Within_same_ext_sentence'] = 1
            else:
                self.features['Within_same_ext_sentence'] = 0
    
            
        self.features['Paragraphs_L'] = utils.utils.count_how_many(left, '<p>')
        self.features['Paragraphs_R'] = utils.utils.count_how_many(right, '<p>')    
        
        dist_ancestor_l = len(l_ancestor_pos) - len(common_ancestor_pos)
        dist_ancestor_r = len(r_ancestor_pos) - len(common_ancestor_pos)
        self.features['Dist_ancestor_L'] = dist_ancestor_l
        self.features['Dist_ancestor_R'] = dist_ancestor_r
    
        self.features['Head_in_L'] = 0
        self.features['Head_in_R'] = 0
        self.features['Common_ancestor_RL'] = len(common_ancestor_pos)
        self.features['Head_pos_in_sentence'] = 0
        self.features['L_Dominates_R'] = 0
        self.features['R_Dominates_L'] = 0
    
        if dist_ancestor_l:
            head = filter_lexical_head(syntax_trees[l_start_i].get_head(l_ancestor_pos))
            if head and head in self.lexical_heads:
                self.features['___Top_lexical_head_L'][self.lexical_heads[head]] = 1
            tag = filter_syntactic_tag(syntax_trees[l_start_i].get_syntactic_tag(l_ancestor_pos))
            if tag and tag in self.syntactic_tags:
                self.features['_Top_Syntactic_tag_L'][self.syntactic_tags[tag]] = 1
        if dist_ancestor_r:
            head = filter_lexical_head(syntax_trees[r_start_i].get_head(r_ancestor_pos))
            if head and head in self.lexical_heads:
                self.features['___Top_lexical_head_R'][self.lexical_heads[head]] = 1
            tag = filter_syntactic_tag(syntax_trees[r_start_i].get_syntactic_tag(r_ancestor_pos))
            if tag and tag in self.syntactic_tags:
                self.features['_Top_Syntactic_tag_R'][self.syntactic_tags[tag]] = 1
    
        if common_ancestor_pos:
            head_pos = syntax_trees[l_start_i][common_ancestor_pos].head
            self.features['Head_pos_in_sentence'] = float(head_pos)/len(syntax_trees[l_start_i].leaves())
            if head_pos >= l_end_word:
                self.features['Head_in_R'] = 1
            else:
                self.features['Head_in_L'] = 1
    
            self.features['Dist_ancestor_L_norm'] = dist_ancestor_l/float(len(common_ancestor_pos))
            self.features['Dist_ancestor_R_norm'] = dist_ancestor_r/float(len(common_ancestor_pos))
     
            if dist_ancestor_l == 0 or dist_ancestor_r == 0: 
                if dist_ancestor_l == 0:# L >> R
                    self.features['L_Dominates_R'] = 1
                    dom_pos = r_ancestor_pos[:-1]
                else: # R >> L
                    self.features['R_Dominates_L'] = 1
                    dom_pos = l_ancestor_pos[:-1]
    
                head = filter_lexical_head(syntax_trees[l_start_i].get_head(dom_pos))
                if head and head in self.lexical_heads:
                    self.features['___Dominated_lexical_head'][self.lexical_heads[head]] = 1
    
                tag = filter_syntactic_tag(syntax_trees[l_start_i].get_syntactic_tag(dom_pos))
                if tag and tag in self.syntactic_tags:
                    self.features['_Dominated_Syntactic_tag'][self.syntactic_tags[tag]] = 1
                
        else:
            self.features['Dist_ancestor_L_norm'] = 1
            self.features['Dist_ancestor_R_norm'] = 1
    
    
        # N-GRAMS
        for n in range(1, self.ngram_len+1):
            #print "\n\n*** %i ***\n" % n
            '''ngrams = get_ngrams(left[1:-1], n, {})
            for (ng, freq) in ngrams.iteritems():
                add_ngram('__L_ngrams', ng)
            
            ngrams = get_ngrams(right[1:-1], n, {})
            for (ng, freq) in ngrams.iteritems():
                add_ngram('__R_ngrams', ng)
            '''
                 
            self.add_ngram('___L_ngrams_pref', get_one_ngram(left, n))
            self.add_ngram('___R_ngrams_pref', get_one_ngram(right, n))
            self.add_ngram('___L_ngrams_suf', get_one_ngram(left, -n))
            self.add_ngram('___R_ngrams_suf', get_one_ngram(right, -n))
     
        # MAIN NUCLEUS self.features:
        offset_main_l = self.write_main_nucleus_features(left, L[0], 'L')
        offset_main_r = self.write_main_nucleus_features(right, L[1], 'R')
        #if (left_num_edus > 1):
        #    self.features['Dist_Main_Nucleus'] = len(L[0].leaves()) - offset_main_l + offset_main_r;
        #else:
        #    self.features['Dist_Main_Nucleus'] = 1 + offset_main_r;
            
            
        # RST STRUCTURE of sub-trees
        self.features['Depth_index_L'] = left_height;
        self.features['Depth_index_R'] = right_height;
        traverse_tree_path(L[0], self.add_subnode_rst, self.RST_Tree_depth, self.features['_L_RST_Tree'])
        traverse_tree_path(L[1], self.add_subnode_rst, self.RST_Tree_depth, self.features['_R_RST_Tree'])
    
        #self.features['TEST_FOR_FUN'] = 1.0;

        # Multi-class
        if L.node != 'NO-REL' and L.node in self.relations:
            label = self.relations[L.node]
        else:
            label = 1
        mc_line = "%i\t%s\n" % (label, self.features.get_full_vector())
        if L.node != 'NO-REL' and mc_output:
            mc_output.write(mc_line)
            
            
        # Binary
        #print 'L.node', L.node
        if L.node == 'NO-REL':
            label = -1
        elif L.node in self.relations:
            label = 1
        else:
            label = 0
        bin_line = "%i\t%s\n" % (label, self.features.get_full_vector())
        #bin_line = "%i\t%s\n" % (label, self.features.get_full_legend())
        if bin_output:
            bin_output.write(bin_line)
    
    
        # Negative instances (only for the training corpus)
        if (full_tree and L.node != 'NO-REL'):
            if isinstance(L[1], Tree):
                self.write_instance(mc_output, bin_output, Tree('NO-REL', [L[0], L[1][0]]), full_tree,
                               syntax_trees, breaks, offsetL)
                
                if isinstance(L[1][0], Tree):
                    self.write_instance(mc_output, bin_output, Tree('NO-REL', [L[0], L[1][0][0]]), full_tree,
                               syntax_trees, breaks, offsetL)
                    
            if isinstance(L[0], Tree):
                if isinstance(L[0][0], Tree):
                    new_offset = offsetL + len(L[0][0].leaves())
                else:
                    new_offset = offsetL + 1
                self.write_instance(mc_output, bin_output, Tree('NO-REL', [L[0][1], L[1]]), full_tree,
                               syntax_trees, breaks, new_offset)
                
                if isinstance(L[0][1], Tree):
                    if isinstance(L[0][1][0], Tree):
                        new_offset = offsetL + len(L[0][1][0].leaves())
                    else:
                        new_offset = offsetL + 1
                    self.write_instance(mc_output, bin_output, Tree('NO-REL', [L[0][1][1], L[1]]), full_tree,
                               syntax_trees, breaks, new_offset)
            elif offsetL > 0:
                self.write_instance(mc_output, bin_output, Tree('NO-REL', [full_tree.leaves()[offsetL-1], L[0]]), full_tree,
                               syntax_trees, breaks, offsetL-1)
    
        '''print L
        print
        print bin_line
        print
        print mc_line'''
        return (bin_line, mc_line)
        #exit(-1) # debug
    
    def write_instance_leaves_only(self, mc_output, bin_output, T, full_tree, syntax_trees, breaks, offset):
        if not isinstance(T[0], Tree) and not isinstance(T[1], Tree):
            self.write_instance(mc_output, bin_output, T, full_tree, syntax_trees, breaks, offset)
    
    
    def write_features(self, input_dir, output_file, my_function = write_instance, output_path = './'):
        files = locate("*.tok.dis", input_dir)
        mc_output = open(output_path + 'mc_' + output_file, "w")
        bin_output = open(output_path + 'bin_' + output_file, "w")
        for filename in files:
            (syntax_trees, breaks, edus) = utils.serialize.loadData(filename[:-8]+'_parsed', '')
            T = load_tree(filename)
            traverse_tree_with_offset(T, lambda x, y: my_function(mc_output, bin_output, x, T, syntax_trees, breaks, y))
        legend = self.features.get_full_legend()
        utils.serialize.saveData('svm_legend', legend)
        return legend
