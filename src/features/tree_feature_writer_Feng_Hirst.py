'''
Created on Feb 19, 2013

@author: Vanessa Wei Feng
'''

import re

from utils.rst_lib import *
from feature_space import FeatureSpace
from trees.lexicalized_tree import LexicalizedTree
from utils.cue_phrases import cue_phrases as cue_phrases_array
from nltk.data import find
from nltk.corpus.reader.wordnet import WordNetICCorpusReader
from nltk.stem.wordnet import WordNetLemmatizer
import utils.serialize
import utils.utils
from nltk.corpus import wordnet as wn
from nltk.corpus import verbnet as vn

from utils.Stanford_Deps import *

class TreeFeatureWriter:
    
    
    def __init__(self, verbose=False, use_word_pairs=True, use_word_dep_types=True, use_syntax_production_rules=True,
                 use_RST_production_rules=True, use_semantic_similarity_features=True, use_contextual_features=False, 
                 use_cue_phrases=True, use_syntax_parallel_features=True, use_lexical_parallel_features=True,
                 use_baseline_features=True, use_ngram_features=True, use_lexical_heads=True, use_syntactic_tags=True,
                 use_top_syntactic_tags=True, use_pair_features=False, subdir=''):
        self.use_word_pairs = use_word_pairs
        self.use_word_dep_types = use_word_dep_types
        self.use_syntax_production_rules = use_syntax_production_rules
        self.use_RST_production_rules = use_RST_production_rules
        self.use_semantic_similarity_features = use_semantic_similarity_features
        self.use_contextual_features = use_contextual_features
        self.use_cue_phrases = use_cue_phrases
        self.use_syntax_parallel_features = use_syntax_parallel_features
        self.use_lexical_parallel_features = use_lexical_parallel_features
        self.use_baseline_features = use_baseline_features
        self.use_ngram_features = use_ngram_features
        self.use_lexical_heads = use_lexical_heads
        self.use_syntactic_tags = use_syntactic_tags # syntactic prefix, suffix
        self.use_top_syntactic_tags = use_top_syntactic_tags
        self.use_pair_features = use_pair_features
        
        self.ngram_len = 3
        self.nb_sentence_parts = 4
        self.nb_syntactic_tags = 1
        self.strong_sentence_bound = re.compile('\.')
        
        self.features = FeatureSpace()
        
        if self.use_word_pairs:
            self.word_pairs_dict = utils.serialize.loadData(os.path.join(subdir, "word_pairs_selected"))
            #self.word_pairs_dict = serialize.loadData("word_pair_dict")
        
            if verbose:
                print "Loaded word pairs dict: " + str(len(self.word_pairs_dict))
        
            self.inv_word_pairs_dict = {}
            for i in sorted(self.word_pairs_dict):
                #print i
                self.inv_word_pairs_dict[self.word_pairs_dict[i]] = i 
            
            self.features.add_group('Word_pair', len(self.word_pairs_dict), self.inv_word_pairs_dict)
        
        
        if self.use_RST_production_rules:# or self.use_contextual_features:
            self.relations = utils.serialize.loadData(os.path.join(subdir, "rels_list"))
            self.relations_no_nuclearity = []
            if verbose:
                print "Loaded relation list: " + str(len(self.relations))
            
            self.relations['NO-REL'] = max(self.relations.values()) + 1
            for relation in self.relations:
                plain_relation = relation[ : -6]
                if plain_relation not in self.relations_no_nuclearity:
                    self.relations_no_nuclearity.append(plain_relation)
            
            self.inv_relations = {}
            for i in sorted(self.relations):
                #print i, self.relations[i]
                self.inv_relations[self.relations[i]] = i
            
            if self.use_contextual_features:
                self.features.add_group('prev_RST_Tree', len(self.relations), self.inv_relations)
                self.features.add_group('next_RST_Tree', len(self.relations), self.inv_relations)
            
            if self.use_RST_production_rules:
#                self.RST_production_rules_legend = {}
#                self.RST_production_rules = {}
#                RST_pr_id = 0
#                for head_rel in self.relations:
#                    if head_rel == 'NO-REL':
#                        continue
#                    
#                    for left_rel in self.relations:
#                        for right_rel in self.relations:
#                            RST_pr = head_rel + '_' + left_rel + '_' + right_rel
#                            self.RST_production_rules[RST_pr] = RST_pr_id
#                            self.RST_production_rules_legend[RST_pr_id] = RST_pr
#                            RST_pr_id += 1
                self.RST_production_rules_L = utils.serialize.loadData(os.path.join(subdir, 'RST_production_rules_selected_L'))
                #self.RST_production_rules_L = serialize.loadData('RST_production_rules_selected')
                self.RST_production_rules_legend_L = {}
                #self.RST_production_rules_L = self.RST_production_rules
                #self.RST_production_rules_legend_L = self.RST_production_rules_legend
                for production in self.RST_production_rules_L:
                    self.RST_production_rules_legend_L[self.RST_production_rules_L[production]] = production               
                self.features.add_group('RST_Production_Rule_L', len(self.RST_production_rules_L), self.RST_production_rules_legend_L)
                
                self.RST_production_rules_R = utils.serialize.loadData(os.path.join(subdir, 'RST_production_rules_selected_R'))
                self.RST_production_rules_legend_R = {}
                #self.RST_production_rules_R = self.RST_production_rules_L
                #self.RST_production_rules_legend_R = self.RST_production_rules_legend_L
                for production in self.RST_production_rules_R:
                    self.RST_production_rules_legend_R[self.RST_production_rules_R[production]] = production
                self.features.add_group('RST_Production_Rule_R', len(self.RST_production_rules_R), self.RST_production_rules_legend_R)
                
                self.RST_production_rules_both = utils.serialize.loadData(os.path.join(subdir, 'RST_production_rules_selected_both'))
                self.RST_production_rules_legend_both = {}
                #self.RST_production_rules_both = self.RST_production_rules_L
                #self.RST_production_rules_legend_both = self.RST_production_rules_legend_L
                for production in self.RST_production_rules_both:
                    self.RST_production_rules_legend_both[self.RST_production_rules_both[production]] = production
                self.features.add_group('RST_Production_Rule_both', len(self.RST_production_rules_both), self.RST_production_rules_legend_both)
                

                if self.use_pair_features:
                    self.RST_production_rules_L_R = utils.serialize.loadData(os.path.join(subdir, 'RST_production_rule_pairs_selected'))
                    self.RST_production_rules_legend_L_R = {}
                    for (production_pair, index) in self.RST_production_rules_L_R.items():
                        self.RST_production_rules_legend_L_R[index] = production_pair
                        
                    self.features.add_group('RST_Production_Rule_L_R', len(self.RST_production_rules_L_R), self.RST_production_rules_legend_L_R)
                    
                if verbose:
                    print "Loaded RST production rule list for left span: " + str(len(self.RST_production_rules_L))
                    print "Loaded RST production rule list for right span: " + str(len(self.RST_production_rules_R))
                    print "Loaded RST production rule list for both spans: " + str(len(self.RST_production_rules_both))
                    if self.use_pair_features:
                        print 'Loaded RST production rules list for left-right span: ' + str(len(self.RST_production_rules_L_R))                       
        
            
        if self.use_syntax_production_rules:
            #self.syntax_production_rules = serialize.loadData("syntax_production_rules_selected")
            #self.syntax_production_rules_L = serialize.loadData("syntax_production_rules_dict")
            self.syntax_production_rules_L = utils.serialize.loadData(os.path.join(subdir, "syntax_production_rules_selected_L"))
            #self.syntax_production_rules_L = self.syntax_production_rules
            #self.syntax_production_rules_L = serialize.loadData("syntax_production_rules_selected")
            if verbose:
                print "Loaded syntax production rules list for left span: ", len(self.syntax_production_rules_L)           
            self.syntax_production_rules_legend_L = {}
            for production in self.syntax_production_rules_L:
                #print production
                self.syntax_production_rules_legend_L[self.syntax_production_rules_L[production]] = production           
            self.features.add_group('Syntax_Production_Rule_L', len(self.syntax_production_rules_L), self.syntax_production_rules_legend_L)
            
            self.syntax_production_rules_R = utils.serialize.loadData(os.path.join(subdir, "syntax_production_rules_selected_R"))
#            self.syntax_production_rules_R = self.syntax_production_rules_L
            if verbose:
                print "Loaded syntax production rules list for right span: ", len(self.syntax_production_rules_R)           
            self.syntax_production_rules_legend_R = {}
            for production in self.syntax_production_rules_R:
                #print production
                self.syntax_production_rules_legend_R[self.syntax_production_rules_R[production]] = production           
            self.features.add_group('Syntax_Production_Rule_R', len(self.syntax_production_rules_R), self.syntax_production_rules_legend_R)
            
            self.syntax_production_rules_both = utils.serialize.loadData(os.path.join(subdir, "syntax_production_rules_selected_both"))
#            self.syntax_production_rules_both = self.syntax_production_rules_L
            if verbose:
                print "Loaded syntax production rules list for both spans: ", len(self.syntax_production_rules_both)           
            self.syntax_production_rules_legend_both = {}
            for production in self.syntax_production_rules_both:
                #print production
                self.syntax_production_rules_legend_both[self.syntax_production_rules_both[production]] = production           
            self.features.add_group('Syntax_Production_Rule_both', len(self.syntax_production_rules_both), self.syntax_production_rules_legend_both)
            
            if self.use_pair_features:
                self.syntax_production_rule_pairs = utils.serialize.loadData(os.path.join(subdir, "syntax_production_rule_pairs_selected"))
                self.syntax_production_rule_pairs_legend = {}
                for production_pair in self.syntax_production_rule_pairs:
                    #print production_pair
                    self.syntax_production_rule_pairs_legend[self.syntax_production_rule_pairs[production_pair]] = production_pair
#            index = 0
#            for production1 in self.syntax_production_rules_L:
#                for production2 in self.syntax_production_rules_R:
#                    self.syntax_production_rule_pairs_legend[index] = production1 + '#' + production2
#                    self.syntax_production_rule_pairs[production1 + '#' + production2] = index
#                    index += 1
            
                self.features.add_group('Syntax_Production_Rule_L_R', len(self.syntax_production_rule_pairs), self.syntax_production_rule_pairs_legend)
                if verbose:
                    print 'Loaded syntax production rule pairs list:', len(self.syntax_production_rule_pairs)
                    
        
        if self.use_cue_phrases:
            '''cue_phrases = {}
            for (index, cue) in enumerate(cue_phrases_array):
                cue_phrases[index] = cue
                
            print "Loaded cue_phrases: ", len(cue_phrases)
            self.features.add_group('_Cue_Phrases_L', len(cue_phrases), cue_phrases)
            self.features.add_group('_Cue_Phrases_R', len(cue_phrases), cue_phrases)
            self.features.add_group('_Cue_Phrases_both', len(cue_phrases), cue_phrases)'''
#            cue_phrases = {}
#            cue_phrase_pairs = {}
#            for (index, cue) in enumerate(cue_phrases_array):
#                cue_phrases[index] = cue
#                for (index1, cue1) in enumerate(cue_phrases_array):
#                    cue_phrase_pairs[index * len(cue_phrases_array) + index1] = cue + '#' + cue1   
#            for i in range(0, self.nb_sentence_parts):
#                self.features.add_group('_Cue_Phrases_L_' + str(i), len(cue_phrases), cue_phrases)
#                self.features.add_group('_Cue_Phrases_R_' + str(i), len(cue_phrases), cue_phrases)
#                self.features.add_group('_Cue_Phrases_both_' + str(i), len(cue_phrases), cue_phrases)
#                for j in range(0, self.nb_sentence_parts):
#                    self.features.add_group('_Cue_Phrases_L_' + str(i) + '_R_' + str(j), len(cue_phrase_pairs), cue_phrase_pairs)
 
            self.cue_phrases_L = utils.serialize.loadData(os.path.join(subdir, 'cue_phrases_selected_L'))
            self.cue_phrases_legend_L = {}
            for (cue, index) in self.cue_phrases_L.items():
                #print cue, index
                self.cue_phrases_legend_L[index] = cue
            self.features.add_group('_Cue_Phrases_L', len(self.cue_phrases_L), self.cue_phrases_legend_L)    
            if verbose:
                print "Loaded cue_phrases_L: ", len(self.cue_phrases_L)
            
            self.cue_phrases_R = utils.serialize.loadData(os.path.join(subdir, 'cue_phrases_selected_R'))
            self.cue_phrases_legend_R = {}
            for cue in self.cue_phrases_R:
                #print cue
                self.cue_phrases_legend_R[self.cue_phrases_R[cue]] = cue
            self.features.add_group('_Cue_Phrases_R', len(self.cue_phrases_R), self.cue_phrases_legend_R)    
            if verbose:
                print "Loaded cue_phrases_R: ", len(self.cue_phrases_R)
            
            self.cue_phrases_both = utils.serialize.loadData(os.path.join(subdir, 'cue_phrases_selected_both'))
            self.cue_phrases_legend_both = {}
            for cue in self.cue_phrases_both:
                #print cue
                self.cue_phrases_legend_both[self.cue_phrases_both[cue]] = cue
            self.features.add_group('_Cue_Phrases_both', len(self.cue_phrases_both), self.cue_phrases_legend_both)    
            if verbose:
                print "Loaded cue_phrases_both: ", len(self.cue_phrases_both)
            
            if self.use_pair_features:
                self.cue_phrases_L_R = utils.serialize.loadData(os.path.join(subdir, 'cue_phrases_selected_L_R'))
                self.cue_phrases_legend_L_R = {}
                for cue in self.cue_phrases_L_R:
                    #print cue
                    self.cue_phrases_legend_L_R[self.cue_phrases_L_R[cue]] = cue
                self.features.add_group('_Cue_Phrases_L_R', len(self.cue_phrases_L_R), self.cue_phrases_legend_L_R)        
                if verbose:
                    print "Loaded cue_phrases_L_R: ", len(self.cue_phrases_L_R)
                       
       
        if self.use_word_dep_types:
#            self.words_dict = serialize.loadData('word_dict')
#            if verbose:
#                print "Loaded words dict: " + str(len(self.words_dict))
#            
#            self.word_deps_L = {}
#            index = 0
#            for word in self.words_dict:
#                for dep in class2type:
#                    self.word_deps_L[word + '_' + dep] = index
#                    index += 1
            self.word_deps_L = utils.serialize.loadData(os.path.join(subdir, 'word_dep_types_selected_L'))
            #self.word_deps_L = serialize.loadData('word_dep_types_selected')
            self.word_deps_legend_L = {}
            for word_dep in self.word_deps_L:
                #print word_dep
                self.word_deps_legend_L[self.word_deps_L[word_dep]] = word_dep          
            if verbose:
                print 'Loaded word-dep pairs for left span:', len(self.word_deps_L)
            self.features.add_group('Word_dep_L', len(self.word_deps_L), self.word_deps_legend_L)
            
            self.word_deps_R = utils.serialize.loadData(os.path.join(subdir, 'word_dep_types_selected_R'))
            #self.word_deps_R = self.word_deps_L
            self.word_deps_legend_R = {}
            for word_dep in self.word_deps_R:
                #print word_dep, i
                self.word_deps_legend_R[self.word_deps_R[word_dep]] = word_dep               
            if verbose:
                print 'Loaded word-dep pairs for right span:', len(self.word_deps_R)
            self.features.add_group('Word_dep_R', len(self.word_deps_R), self.word_deps_legend_R)
            
            self.word_deps_both = utils.serialize.loadData(os.path.join(subdir, 'word_dep_types_selected_both'))
            #self.word_deps_both = self.word_deps_L
            self.word_deps_legend_both = {}
            for word_dep in self.word_deps_both:
                #print word_dep, i
                self.word_deps_legend_both[self.word_deps_both[word_dep]] = word_dep              
            if verbose:
                print 'Loaded word-dep pairs for both spans:', len(self.word_deps_both)
            self.features.add_group('Word_dep_both', len(self.word_deps_both), self.word_deps_legend_both)
            
            #self.word_dep_pairs = {}
            if self.use_pair_features:
                self.word_dep_pairs = utils.serialize.loadData(os.path.join(subdir, 'word_dep_type_pairs_selected'))
                self.word_dep_pairs_legend = {}
                for (word_dep_pair, index) in self.word_dep_pairs.items():
                    self.word_dep_pairs_legend[index] = word_dep_pair
#            index = 0
#            for l_word_dep in self.word_deps_L:
#                for r_word_dep in self.word_deps_R:
#                    word_dep_pair = l_word_dep + '#' + r_word_dep
#                    self.word_dep_pairs_legend[index] = word_dep_pair
#                    self.word_dep_pairs[word_dep_pair] = index
#                    index += 1
                if verbose:
                    print 'Loaded word-dep pairs for left-right pair:', len(self.word_dep_pairs)
                self.features.add_group('Word_dep_L_R',
                                        len(self.word_dep_pairs), self.word_dep_pairs_legend)      
        
        self.lmtzr = WordNetLemmatizer()
        
        if self.use_semantic_similarity_features:
            ic_reader = WordNetICCorpusReader(find("corpora/wordnet_ic/"), "ic-brown-resnik-add1.dat")
            self.ic = ic_reader.ic("ic-brown-resnik-add1.dat") 
            if verbose:
                print 'Loaded information content file ic-brown-resnik-add1.dat'
            
            short_vn_cids = []
            for vn_classid in vn.classids():
                scid = vn.shortid(vn_classid)
                scid = scid.split('.')[0].split('-')[0]
                if scid not in short_vn_cids:
                    short_vn_cids.append(scid)
            
            self.vn_cids = {}
            self.vn_cid_legend = {}
            for (i, cid) in enumerate(short_vn_cids):
                self.vn_cids[cid] = i
                self.vn_cid_legend[i] = cid
            
            if verbose:
                print 'Loaded VerbNet verb classes', len(self.vn_cids)
                
            self.features.add_group('Verbnet_class_id_L', len(self.vn_cids), self.vn_cid_legend)
            self.features.add_group('Verbnet_class_id_R', len(self.vn_cids), self.vn_cid_legend)
            self.features.add_group('Verbnet_class_id_both', len(self.vn_cids), self.vn_cid_legend)
            if self.use_pair_features:
                self.vn_cid_pairs = {}
                self.vn_cid_pairs_legend = {}
                for (i, cid1) in enumerate(short_vn_cids):
                    for (j, cid2) in enumerate(short_vn_cids):
                        cid_pair = cid1 + '#' + cid2
                        index = i * len(short_vn_cids) + j
                        self.vn_cid_pairs[cid_pair] = index
                        self.vn_cid_pairs_legend[index] = cid_pair
                
                self.features.add_group('Verbnet_class_id_L_R', len(self.vn_cid_pairs), self.vn_cid_pairs_legend)
                
        if self.use_ngram_features:
#            self.ngrams_dict = serialize.loadData("n-grams_dict")
#        
#            self.inv_ngrams_dict = {}
#            for i in sorted(self.ngrams_dict):
#                #print i
#                self.inv_ngrams_dict[self.ngrams_dict[i]] = i 
            
            #self.features.add_group('__L_ngrams', len(self.ngrams_dict), self.inv_ngrams_dict)
            #self.features.add_group('__R_ngrams', len(self.ngrams_dict), self.inv_ngrams_dict)
            #self.ngram_l_pref = self.ngrams_dict
            #self.ngram_l_pref_legend = self.inv_ngrams_dict
            self.ngram_l_pref = utils.serialize.loadData(os.path.join(subdir, 'ngrams_selected_pref_L'))
            self.ngram_l_pref_legend = {}
            for (ngram, index) in self.ngram_l_pref.items():
#                print ngram, index
                self.ngram_l_pref_legend[index] = ngram
                
            self.features.add_group('NGrams_pref_L', len(self.ngram_l_pref), self.ngram_l_pref_legend)
            self.features.add_group('Main_Nucleus_NGrams_pref_L', len(self.ngram_l_pref), self.ngram_l_pref_legend)
            if verbose:
                print "Loaded ngram dict_pref_L: " + str(len(self.ngram_l_pref))
            
            #self.ngram_l_suf = self.ngrams_dict
            #self.ngram_l_suf_legend = self.inv_ngrams_dict
            self.ngram_l_suf = utils.serialize.loadData(os.path.join(subdir, 'ngrams_selected_suf_L'))
            self.ngram_l_suf_legend = {}
            for ngram in self.ngram_l_suf:
                self.ngram_l_suf_legend[index] = ngram
            self.features.add_group('NGrams_suf_L', len(self.ngram_l_suf), self.ngram_l_suf_legend)
            self.features.add_group('Main_Nucleus_NGrams_suf_L', len(self.ngram_l_suf), self.ngram_l_suf_legend)
            if verbose:
                print "Loaded ngram dict_suf_L: " + str(len(self.ngram_l_suf))
            
            #self.ngram_r_pref = self.ngrams_dict
            #self.ngram_r_pref_legend = self.inv_ngrams_dict
            self.ngram_r_pref = utils.serialize.loadData(os.path.join(subdir, 'ngrams_selected_pref_R'))
            self.ngram_r_pref_legend = {}
            for (ngram, index) in self.ngram_r_pref.items():
                self.ngram_r_pref_legend[index] = ngram
            self.features.add_group('NGrams_pref_R', len(self.ngram_r_pref), self.ngram_r_pref_legend)
            self.features.add_group('Main_Nucleus_NGrams_pref_R', len(self.ngram_r_pref), self.ngram_r_pref_legend)
            if verbose:
                print "Loaded ngram dict_pref_R: " + str(len(self.ngram_r_pref))
            
            #self.ngram_r_suf = self.ngrams_dict
            #self.ngram_r_suf_legend = self.inv_ngrams_dict
            self.ngram_r_suf = utils.serialize.loadData(os.path.join(subdir, 'ngrams_selected_suf_R'))
            self.ngram_r_suf_legend = {}
            for (ngram, index) in self.ngram_r_suf.items():
                self.ngram_r_suf_legend[index] = ngram
            self.features.add_group('NGrams_suf_R', len(self.ngram_r_suf), self.ngram_r_suf_legend)
            self.features.add_group('Main_Nucleus_NGrams_suf_R', len(self.ngram_r_suf), self.ngram_r_suf_legend)
            if verbose:
                print "Loaded ngram dict_suf_R: " + str(len(self.ngram_r_suf))
            
            #self.ngram_both_pref = self.ngrams_dict
            #self.ngram_both_pref_legend = self.inv_ngrams_dict
            self.ngram_both_pref = utils.serialize.loadData(os.path.join(subdir, 'ngrams_selected_pref_both'))
            self.ngram_both_pref_legend = {}
            for (ngram, index) in self.ngram_both_pref.items():
                self.ngram_both_pref_legend[index] = ngram
            self.features.add_group('NGrams_pref_both', len(self.ngram_both_pref), self.ngram_both_pref_legend)
            self.features.add_group('Main_Nucleus_NGrams_pref_both', len(self.ngram_both_pref), self.ngram_both_pref_legend)
            if verbose:
                print "Loaded ngram dict_pref_both: " + str(len(self.ngram_both_pref))
            
            #self.ngram_both_suf = self.ngrams_dict
            #self.ngram_both_suf_legend = self.inv_ngrams_dict
            self.ngram_both_suf = utils.serialize.loadData(os.path.join(subdir, 'ngrams_selected_suf_both'))
            self.ngram_both_suf_legend = {}
            for (ngram, index) in self.ngram_both_suf.items():
                self.ngram_both_suf_legend[index] = ngram
            self.features.add_group('NGrams_suf_both', len(self.ngram_both_suf), self.ngram_both_suf_legend)
            self.features.add_group('Main_Nucleus_NGrams_suf_both', len(self.ngram_both_suf), self.ngram_both_suf_legend)
            if verbose:
                print "Loaded ngram dict_suf_both: " + str(len(self.ngram_both_suf))
            
            if self.use_pair_features:
                self.ngram_l_pref_r_pref = utils.serialize.loadData(os.path.join(subdir, 'ngram_pairs_selected_pref_L_pref_R'))
                self.ngram_l_pref_r_pref_legend = {}
    #            index = 0
    #            for l_ngram in self.ngram_l_pref:
    #                for r_ngram in self.ngram_r_pref:
    #                    pair_pref = l_ngram + '#' + r_ngram
    #                    self.ngram_l_pref_r_pref[pair_pref] = index
    #                    self.ngram_l_pref_r_pref_legend[index] = pair_pref
    #                    index += 1
                for (ngram_pair, index) in self.ngram_l_pref_r_pref.items():
                    self.ngram_l_pref_r_pref_legend[index] = ngram_pair    
                self.features.add_group('NGrams_pref_L_pref_R', len(self.ngram_l_pref_r_pref), self.ngram_l_pref_r_pref_legend)
                self.features.add_group('Main_Nucleus_NGrams_pref_L_pref_R', len(self.ngram_l_pref_r_pref), self.ngram_l_pref_r_pref_legend)
                if verbose:
                    print 'Loaded ngram dict pref_L_pref_R:', len(self.ngram_l_pref_r_pref)
                
                self.ngram_l_pref_r_suf = utils.serialize.loadData(os.path.join(subdir, 'ngram_pairs_selected_pref_L_suf_R'))
                self.ngram_l_pref_r_suf_legend = {}
    #            index = 0
    #            for l_ngram in self.ngram_l_pref:
    #                for r_ngram in self.ngram_r_suf:
    #                    pair_pref = l_ngram + '#' + r_ngram
    #                    self.ngram_l_pref_r_suf[pair_pref] = index
    #                    self.ngram_l_pref_r_suf_legend[index] = pair_pref
    #                    index += 1
                for (ngram_pair, index) in self.ngram_l_pref_r_suf.items():
                    self.ngram_l_pref_r_suf_legend[index] = ngram_pair
                self.features.add_group('NGrams_pref_L_suf_R', len(self.ngram_l_pref_r_suf), self.ngram_l_pref_r_suf_legend)
                self.features.add_group('Main_Nucleus_NGrams_pref_L_suf_R', len(self.ngram_l_pref_r_suf), self.ngram_l_pref_r_suf_legend)
                if verbose:
                    print 'Loaded ngram dict pref_L_suf_R:', len(self.ngram_l_pref_r_suf)
                    
                self.ngram_l_suf_r_pref = utils.serialize.loadData(os.path.join(subdir, 'ngram_pairs_selected_suf_L_pref_R'))
                self.ngram_l_suf_r_pref_legend = {}
    #            index = 0
    #            for l_ngram in self.ngram_l_suf:
    #                for r_ngram in self.ngram_r_pref:
    #                    pair_pref = l_ngram + '#' + r_ngram
    #                    self.ngram_l_suf_r_pref[pair_pref] = index
    #                    self.ngram_l_suf_r_pref_legend[index] = pair_pref
    #                    index += 1
                for (ngram_pair, index) in self.ngram_l_suf_r_pref.items():
                    self.ngram_l_suf_r_pref_legend[index] = ngram_pair
                self.features.add_group('NGrams_suf_L_pref_R', len(self.ngram_l_suf_r_pref), self.ngram_l_suf_r_pref_legend)
                self.features.add_group('Main_Nucleus_NGrams_suf_L_pref_R', len(self.ngram_l_suf_r_pref), self.ngram_l_suf_r_pref_legend)
                if verbose:
                    print 'Loaded ngram dict suf_L_pref_R:', len(self.ngram_l_suf_r_pref)
                
                self.ngram_l_suf_r_suf = utils.serialize.loadData(os.path.join(subdir, 'ngram_pairs_selected_suf_L_suf_R'))
                self.ngram_l_suf_r_suf_legend = {}
    #            index = 0
    #            for l_ngram in self.ngram_l_suf:
    #                for r_ngram in self.ngram_r_suf:
    #                    pair_pref = l_ngram + '#' + r_ngram
    #                    self.ngram_l_suf_r_suf[pair_pref] = index
    #                    self.ngram_l_suf_r_suf_legend[index] = pair_pref
    #                    index += 1
                for (ngram_pair, index) in self.ngram_l_suf_r_suf.items():
                    self.ngram_l_suf_r_suf_legend[index] = ngram_pair
                self.features.add_group('NGrams_suf_L_suf_R', len(self.ngram_l_suf_r_suf), self.ngram_l_suf_r_suf_legend)
                self.features.add_group('Main_Nucleus_NGrams_suf_L_suf_R', len(self.ngram_l_suf_r_suf), self.ngram_l_suf_r_suf_legend)
                if verbose:
                    print 'Loaded ngram dict suf_L_suf_R:', len(self.ngram_l_suf_r_suf)
                    
        if self.use_lexical_heads:                              
#            self.lexical_heads = {}
#            self.lexical_heads_legend = {}
#            self.lexical_head_pairs = {}
#            self.lexical_head_pairs_legend = {}
#            for (i, tag1) in enumerate(self.inv_lexical_heads):
#                self.lexical_heads[tag1] = i 
#                self.lexical_heads_legend[i] = tag1
#                for (j, tag2) in enumerate(self.inv_lexical_heads):
#                    tag_pair = tag1 + '#' + tag2
#                    index = i * len(self.inv_lexical_heads) + j
#                    self.lexical_head_pairs[tag_pair] = index
#                    self.lexical_head_pairs_legend[index] = tag_pair
            
            self.lexical_heads_L = utils.serialize.loadData(os.path.join(subdir, 'lexical_heads_selected_L'))
            self.lexical_heads_legend_L = {}
            for (head, index) in self.lexical_heads_L.items():
                self.lexical_heads_legend_L[index] = head
            self.features.add_group('Top_lexical_head_L', len(self.lexical_heads_L), self.lexical_heads_legend_L)
            if verbose:
                print 'Loaded lexical head list_L:', len(self.lexical_heads_L)
                
            self.lexical_heads_R = utils.serialize.loadData(os.path.join(subdir, 'lexical_heads_selected_R'))
            self.lexical_heads_legend_R = {}
            for (head, index) in self.lexical_heads_R.items():
                self.lexical_heads_legend_R[index] = head
            self.features.add_group('Top_lexical_head_R', len(self.lexical_heads_R), self.lexical_heads_legend_R)
            if verbose:
                print 'Loaded lexical head list_R:', len(self.lexical_heads_R)
            
            self.lexical_heads_both = utils.serialize.loadData(os.path.join(subdir, 'lexical_heads_selected_both'))
            self.lexical_heads_legend_both = {}
            for (head, index) in self.lexical_heads_both.items():
                self.lexical_heads_legend_both[index] = head
            self.features.add_group('Top_lexical_head_both', len(self.lexical_heads_both), self.lexical_heads_legend_both)
            if verbose:
                print 'Loaded lexical head list both:', len(self.lexical_heads_both)
            
            self.lexical_heads_dominated = utils.serialize.loadData(os.path.join(subdir, 'lexical_heads_selected_dominated'))
            self.lexical_heads_legend_dominated = {}
            for (head, index) in self.lexical_heads_dominated.items():
                self.lexical_heads_legend_dominated[index] = head
            self.features.add_group('Dominated_lexical_head', len(self.lexical_heads_dominated), self.lexical_heads_legend_dominated)
            if verbose:
                print 'Loaded lexical head list_dominated:', len(self.lexical_heads_dominated)
                
            #self.lexical_head_pairs = {}
            if self.use_pair_features:
                self.lexical_head_pairs = utils.serialize.loadData(os.path.join(subdir, 'lexical_head_pairs_selected'))
                self.lexical_head_pairs_legend = {}
                for (head_pair, index) in self.lexical_head_pairs.items():
                    self.lexical_head_pairs_legend[index] = head_pair
    #            for (head1, index1) in self.lexical_heads_L.items():
    #                for (head2, index2) in self.lexical_heads_R.items():
    #                    head_pair = head1 + '#' + head2
    #                    index = index1 * len(self.lexical_heads_R) + index2
    #                    self.lexical_head_pairs[head_pair] = index
    #                    self.lexical_head_pairs_legend[index] = head_pair
                self.features.add_group('Top_lexical_head_L_R',
                                        len(self.lexical_head_pairs), self.lexical_head_pairs_legend)
                if verbose:
                    print 'Loaded lexical head list_L_R:', len(self.lexical_head_pairs)
        
        
        if self.use_syntactic_tags or self.use_top_syntactic_tags:
            if self.use_syntactic_tags:
                self.syntactic_tags_pref_L = utils.serialize.loadData(os.path.join(subdir, 'syntactic_tags_selected_pref_L'))
                self.syntactic_tags_pref_L_legend = {}
                for (tag, index) in self.syntactic_tags_pref_L.items():
                    self.syntactic_tags_pref_L_legend[index] = tag                   
                self.features.add_group('Syntactic_tags_pref_L', len(self.syntactic_tags_pref_L), self.syntactic_tags_pref_L_legend)
                if verbose:
                    print 'Loaded syntactic tag pref L:', len(self.syntactic_tags_pref_L)
                    
                self.syntactic_tags_pref_R = utils.serialize.loadData(os.path.join(subdir, 'syntactic_tags_selected_pref_R'))
                self.syntactic_tags_pref_R_legend = {}
                for (tag, index) in self.syntactic_tags_pref_R.items():
                    self.syntactic_tags_pref_R_legend[index] = tag                   
                self.features.add_group('Syntactic_tags_pref_R', len(self.syntactic_tags_pref_R), self.syntactic_tags_pref_R_legend)
                if verbose:
                    print 'Loaded syntactic tag pref R:', len(self.syntactic_tags_pref_R)
                
                self.syntactic_tags_pref_both = utils.serialize.loadData(os.path.join(subdir, 'syntactic_tags_selected_pref_both'))
                self.syntactic_tags_pref_both_legend = {}
                for (tag, index) in self.syntactic_tags_pref_both.items():
                    self.syntactic_tags_pref_both_legend[index] = tag                   
                self.features.add_group('Syntactic_tags_pref_both', len(self.syntactic_tags_pref_both), self.syntactic_tags_pref_both_legend)
                if verbose:
                    print 'Loaded syntactic tag pref both:', len(self.syntactic_tags_pref_both)
                
                
                self.syntactic_tags_suf_L = utils.serialize.loadData(os.path.join(subdir, 'syntactic_tags_selected_suf_L'))
                self.syntactic_tags_suf_L_legend = {}
                for (tag, index) in self.syntactic_tags_suf_L.items():
                    self.syntactic_tags_suf_L_legend[index] = tag                   
                self.features.add_group('Syntactic_tags_suf_L', len(self.syntactic_tags_suf_L), self.syntactic_tags_suf_L_legend)
                if verbose:
                    print 'Loaded syntactic tag suf L:', len(self.syntactic_tags_suf_L)
                
                self.syntactic_tags_suf_R = utils.serialize.loadData(os.path.join(subdir, 'syntactic_tags_selected_suf_R'))
                self.syntactic_tags_suf_R_legend = {}
                for (tag, index) in self.syntactic_tags_suf_R.items():
                    self.syntactic_tags_suf_R_legend[index] = tag                   
                self.features.add_group('Syntactic_tags_suf_R', len(self.syntactic_tags_suf_R), self.syntactic_tags_suf_R_legend)
                if verbose:
                    print 'Loaded syntactic tag suf R:', len(self.syntactic_tags_suf_R)
                    
                self.syntactic_tags_suf_both = utils.serialize.loadData(os.path.join(subdir, 'syntactic_tags_selected_suf_both'))
                self.syntactic_tags_suf_both_legend = {}
                for (tag, index) in self.syntactic_tags_suf_both.items():
                    self.syntactic_tags_suf_both_legend[index] = tag                   
                self.features.add_group('Syntactic_tags_suf_both', len(self.syntactic_tags_suf_both), self.syntactic_tags_suf_both_legend)
                if verbose:
                    print 'Loaded syntactic tag suf both:', len(self.syntactic_tags_suf_both)
                
                if self.use_pair_features:
                    self.syntactic_tag_pairs_pref_l_pref_r = utils.serialize.loadData(os.path.join(subdir, 'syntactic_tag_pairs_selected_pref_L_pref_R'))
                    self.syntactic_tag_pairs_pref_l_pref_r_legend = {}
                    for (tag_pair, index) in self.syntactic_tag_pairs_pref_l_pref_r.items():
                        self.syntactic_tag_pairs_pref_l_pref_r_legend[index] = tag_pair                   
                    self.features.add_group('Syntactic_tags_pref_L_pref_R', len(self.syntactic_tag_pairs_pref_l_pref_r), self.syntactic_tag_pairs_pref_l_pref_r_legend)
                    if verbose:
                        print 'Loaded syntactic tag pairs pref L pref R:', len(self.syntactic_tag_pairs_pref_l_pref_r)
                        
                    self.syntactic_tag_pairs_pref_l_suf_r = utils.serialize.loadData(os.path.join(subdir, 'syntactic_tag_pairs_selected_pref_L_suf_R'))
                    self.syntactic_tag_pairs_pref_l_suf_r_legend = {}
                    for (tag_pair, index) in self.syntactic_tag_pairs_pref_l_suf_r.items():
                        self.syntactic_tag_pairs_pref_l_suf_r_legend[index] = tag_pair                   
                    self.features.add_group('Syntactic_tags_pref_L_suf_R', len(self.syntactic_tag_pairs_pref_l_suf_r), self.syntactic_tag_pairs_pref_l_suf_r_legend)
                    if verbose:
                        print 'Loaded syntactic tag pairs pref L suf R:', len(self.syntactic_tag_pairs_pref_l_suf_r)
                    
                    self.syntactic_tag_pairs_suf_l_pref_r = utils.serialize.loadData(os.path.join(subdir, 'syntactic_tag_pairs_selected_suf_L_pref_R'))
                    self.syntactic_tag_pairs_suf_l_pref_r_legend = {}
                    for (tag_pair, index) in self.syntactic_tag_pairs_suf_l_pref_r.items():
                        self.syntactic_tag_pairs_suf_l_pref_r_legend[index] = tag_pair                   
                    self.features.add_group('Syntactic_tags_suf_L_pref_R', len(self.syntactic_tag_pairs_suf_l_pref_r), self.syntactic_tag_pairs_suf_l_pref_r_legend)
                    if verbose:
                        print 'Loaded syntactic tag pairs suf L pref R:', len(self.syntactic_tag_pairs_suf_l_pref_r)
                    
                    self.syntactic_tag_pairs_suf_l_suf_r = utils.serialize.loadData(os.path.join(subdir, 'syntactic_tag_pairs_selected_suf_L_suf_R'))
                    self.syntactic_tag_pairs_suf_l_suf_r_legend = {}
                    for (tag_pair, index) in self.syntactic_tag_pairs_suf_l_suf_r.items():
                        self.syntactic_tag_pairs_suf_l_suf_r_legend[index] = tag_pair                   
                    self.features.add_group('Syntactic_tags_suf_L_suf_R', len(self.syntactic_tag_pairs_suf_l_suf_r), self.syntactic_tag_pairs_suf_l_suf_r_legend)
                    if verbose:
                        print 'Loaded syntactic tag pairs suf L suf R:', len(self.syntactic_tag_pairs_suf_l_suf_r)
            
            if self.use_top_syntactic_tags:
                #self.inv_syntactic_tags = serialize.loadData("simple_syntactic_labels")
                #if verbose:
                    #print "Loaded syntactic_tags list: ", len(self.inv_syntactic_tags)
                
#                self.syntactic_tags_legend = {}
#                self.syntactic_tags = {}
#                self.syntactic_tag_pairs_legend = {}
#                self.syntactic_tag_pairs = {}  
#
#                for (i, tag) in enumerate(self.inv_syntactic_tags):
#                    self.syntactic_tags[tag] = i 
#                    self.syntactic_tags_legend[i] = tag
#                    for (j, tag2) in enumerate(self.inv_syntactic_tags):
#                        pair_tag = tag + '#' + tag2
#                        index = i * len(self.inv_syntactic_tags) + j
#                        self.syntactic_tag_pairs[pair_tag] = index
#                        self.syntactic_tag_pairs_legend[index] = pair_tag
                
                self.top_syntactic_tags_L = utils.serialize.loadData(os.path.join(subdir, 'top_syntactic_tags_selected_L'))
                self.top_syntactic_tags_L_legend = {}
                for (tag, index) in self.top_syntactic_tags_L.items():
                    self.top_syntactic_tags_L_legend[index] = tag                 
                self.features.add_group('Top_Syntactic_tag_L', len(self.top_syntactic_tags_L), self.top_syntactic_tags_L_legend)
                if verbose:
                    print 'Loaded top syntactic tag list L:', len(self.top_syntactic_tags_L)
                    
                self.top_syntactic_tags_R = utils.serialize.loadData(os.path.join(subdir, 'top_syntactic_tags_selected_R'))
                self.top_syntactic_tags_R_legend = {}
                for (tag, index) in self.top_syntactic_tags_R.items():
                    self.top_syntactic_tags_R_legend[index] = tag                 
                self.features.add_group('Top_Syntactic_tag_R', len(self.top_syntactic_tags_R), self.top_syntactic_tags_R_legend)
                if verbose:
                    print 'Loaded top syntactic tag list R:', len(self.top_syntactic_tags_R)
                
                self.top_syntactic_tags_both = utils.serialize.loadData(os.path.join(subdir, 'top_syntactic_tags_selected_both'))
                self.top_syntactic_tags_both_legend = {}
                for (tag, index) in self.top_syntactic_tags_both.items():
                    self.top_syntactic_tags_both_legend[index] = tag                 
                self.features.add_group('Top_Syntactic_tag_both',
                                        len(self.top_syntactic_tags_both), self.top_syntactic_tags_both_legend)
                if verbose:
                    print 'Loaded top syntactic tag list both:', len(self.top_syntactic_tags_both)
                
                if self.use_pair_features:
                    self.top_syntactic_tags_L_R = utils.serialize.loadData(os.path.join(subdir, 'top_syntactic_tags_selected_L_R'))
                    self.top_syntactic_tags_L_R_legend = {}
                    for (tag, index) in self.top_syntactic_tags_L_R.items():
                        self.top_syntactic_tags_L_R_legend[index] = tag                 
                    self.features.add_group('Top_Syntactic_tag_L_R', len(self.top_syntactic_tags_L_R), self.top_syntactic_tags_L_R_legend)
                    if verbose:
                        print 'Loaded top syntactic tag list L R:', len(self.top_syntactic_tags_L_R)
                
                self.top_syntactic_tags_dominated = utils.serialize.loadData(os.path.join(subdir, 'top_syntactic_tags_selected_dominated'))
                self.top_syntactic_tags_dominated_legend = {}
                for (tag, index) in self.top_syntactic_tags_dominated.items():
                    self.top_syntactic_tags_dominated_legend[index] = tag                 
                self.features.add_group('Top_Syntactic_tag_dominated',
                                        len(self.top_syntactic_tags_dominated), self.top_syntactic_tags_dominated_legend)
                if verbose:
                    print 'Loaded top syntactic tag list dominated:', len(self.top_syntactic_tags_dominated)
                 
                            
        if self.use_baseline_features:
            self.RST_Tree_depth = 3
            self.tree_size = 2**(self.RST_Tree_depth+1)-1
                 
            self.RST_legend = {}
            for i in range(0, self.tree_size):
                for j in range(0,len(self.inv_relations)):
                    self.RST_legend[(i*len(self.inv_relations))+j] = str(i) + "][" + self.inv_relations[j+1]
                
            self.features.add_group('_L_RST_Tree', len(self.relations) * self.tree_size, self.RST_legend)
            self.features.add_group('_R_RST_Tree', len(self.relations) * self.tree_size, self.RST_legend)

               
#        fout = open('feature selection/legend_RST_production_rule_pairs.txt', 'w')
#        legend = self.features.get_full_legend()
#        for (i, feature) in legend.items():
#            fout.write(str(i) + ' ' + feature + '\n')
#        fout.flush()
#        fout.close()

        if verbose:
            print 'Finised loading all necessary dictionaries!'
        
        self.counter = 0

    
    def get_main_spans(self, span, offset):
        main_span_list = []
        if isinstance(span, Tree):
            for main_pos in get_main_edus(span):
                main_span = span[main_pos]
                ''' find out the index of this edu '''
                for i in range(len(span.leaves())):
                    if list(span.leaf_treeposition(i)) == main_pos:
                        break
                
                #print i, span.leaf_treeposition(i), main_pos
                main_offset = offset + i
                main_span_list.append((main_span, main_offset))
        else:
            main_span_list = [(span, offset)]
    
        return main_span_list

    def add_ngram(self, feature_name, ngram):
        if ngram in self.ngrams_dict:
            self.features[feature_name][self.ngrams_dict[ngram]] = 1

    def bin_array_to_int(self, arr):
        def bin_add(x, y): return x*2+y
        return reduce(bin_add, reversed(arr), 0)
    
    def write_position_features(self, syntax_trees, breaks, num_edus, suffix, start_i, start_j):
        exclude_words = ",.`':;!?"
        if start_i >= len(breaks):
            print start_i
            print breaks
        if start_j >= len(breaks[start_i]):
            print start_i, start_j
            print breaks[start_i]
            print breaks

        start_word = breaks[start_i][start_j][0]
        
        while start_word < len(syntax_trees[start_i].leaves()) and not syntax_trees[start_i].leaves()[start_word].strip(exclude_words):
            start_word += 1
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
            ancestor_pos = syntax_trees[start_i].treeposition_spanning_leaves(start_word, end_word)
            start_leaf_pos = syntax_trees[start_i].leaf_treeposition(start_word)
            end_leaf_pos = syntax_trees[start_i].leaf_treeposition(end_word - 1)
            
            start_word_str = syntax_trees[start_i].leaves()[start_word]
            end_word_str = syntax_trees[start_i].leaves()[end_word - 1]
            if not isinstance(syntax_trees[start_i][ancestor_pos], Tree):
                self.features['Embedded_in_subtree_with_other_EDU'] = 0
            else:
                if syntax_trees[start_i][ancestor_pos].leaves()[0] == start_word_str \
                and syntax_trees[start_i][ancestor_pos].leaves()[-1] == end_word_str:
                    self.features['Embedded_in_subtree_with_other_EDU'] = 0
                else:
                    self.features['Embedded_in_subtree_with_other_EDU'] = 1            
        else:
            self.features['Inside_sentence_' + suffix] = 0
            self.features['Sentence_EDUs_cover_' + suffix] = 0
            self.features['Sentence_tokens_cover_' + suffix] = 0
            ancestor_pos = ()
            conservative_top_tag = None
            self.features['Embedded_in_subtree_with_other_EDU'] = 1
    
        self.features['Sentence_span_' + suffix] = end_i - start_i
        
            
        return (end_i, end_j, end_word, ancestor_pos)    

       
    def write_baseline_features(self, L, full_tree, syntax_trees, breaks, offsetL, offsetR):
#        print L[0]
#        print L[1]
        
        (left, left_num_edus, left_height) = get_concat_text(L[0])
        (right, right_num_edus, right_height) = get_concat_text(L[1])
    
        
        # GENERAL self.features:
        self.features['Len_L'] = len(left)
        self.features['Len_R'] = len(right)
        self.features['Num_edus_L'] = left_num_edus
        self.features['Num_edus_R'] = right_num_edus
    
        tot = 0
        for (i, sent_breaks) in enumerate(breaks):
            #print tot, i, sent_breaks
            if tot + len(sent_breaks) > offsetL:
                break;
            tot += len(sent_breaks)
    
        l_start_i = i
        l_start_j = j = offsetL - tot
        (l_end_i, l_end_j, l_end_word, l_ancestor_pos) = self.write_position_features(syntax_trees, breaks, left_num_edus,
                                                                     'L', l_start_i, l_start_j)
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
        else:
            self.features['Dist_ancestor_L_norm'] = 1
            self.features['Dist_ancestor_R_norm'] = 1
    
        
        self.features['Depth_index_L'] = left_height
        self.features['Depth_index_R'] = right_height
        
        traverse_tree_path(L[0], self.add_subnode_rst, self.RST_Tree_depth, self.features['_L_RST_Tree'])
        traverse_tree_path(L[1], self.add_subnode_rst, self.RST_Tree_depth, self.features['_R_RST_Tree'])
            
    
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
            
            
    def write_instance(self, mc_output, bin_output, L, prev_stump, next_stump, full_tree, syntax_trees, deps, breaks, offsetL, offsetR = 0,
                       reset_contextual_features = False):
        self.features.reset()
        
        if self.use_baseline_features:
            self.write_baseline_features(L, full_tree, syntax_trees, breaks, offsetL, offsetR)
        
        l_span_pos = self.get_span_pos(L[0], syntax_trees, breaks, offsetL)
        l_num_edus = 1 if not isinstance(L[0], Tree) else len(L[0].leaves())
        r_span_pos = self.get_span_pos(L[1], syntax_trees, breaks, offsetL + l_num_edus)
        
        l_main_word_list = self.get_word_list_from_main_edus(L[0])
        r_main_word_list = self.get_word_list_from_main_edus(L[1])
        l_word_list = self.get_word_list_from_span(L[0])
        r_word_list = self.get_word_list_from_span(L[1])
        
        l_main_span_list = self.get_main_spans(L[0], offsetL)
        l_main_span_pos_list = []
        #print 'left_span', L[0], offsetL
        for (l_main_span, l_main_offset) in l_main_span_list:
            #print l_main_span, l_main_offset
            l_main_span_pos_list.append(self.get_span_pos(l_main_span, syntax_trees, breaks, l_main_offset))
        
        r_main_span_list = self.get_main_spans(L[1], offsetL + l_num_edus)
        r_main_span_pos_list = []
        #print 'right_span', L[1], offsetL + l_num_edus
        for (r_main_span, r_main_offset) in r_main_span_list:
            #print r_main_span, r_main_offset
            r_main_span_pos_list.append(self.get_span_pos(r_main_span, syntax_trees, breaks, r_main_offset))
        #print
        #l_main_span_pos_list = [l_span_pos]
        #r_main_span_pos_list = [r_span_pos]
        
        if self.use_word_pairs:
            self.write_word_pairs_features(l_main_word_list, r_main_word_list)
            #self.write_word_pairs_features(l_word_list, r_word_list)
        
        if self.use_word_dep_types:                 
#            print L[0]
#            print L[1]
#            print 'l_num_edus', l_num_edus
#            print l_span_pos
#            print r_span_pos
            #self.write_word_dep_types_features(deps, syntax_trees, [l_span_pos], [r_span_pos])
            self.write_word_dep_types_features(deps, syntax_trees, l_main_span_pos_list, r_main_span_pos_list)
        
        if self.use_syntax_production_rules:
            #self.write_syntax_production_rules(syntax_trees, [l_span_pos], [r_span_pos])
            self.write_syntax_production_rules(syntax_trees, l_main_span_pos_list, r_main_span_pos_list)
        
        if self.use_RST_production_rules:
            self.write_RST_prodution_rules(L)
        
#        if self.use_contextual_features:
#            self.write_contextual_features(prev_stump, next_stump)
        
        if self.use_cue_phrases:
            #self.write_cue_phrase_features(l_word_list, r_word_list)
            self.write_cue_phrase_features(l_main_word_list, r_main_word_list)
        
        if self.use_semantic_similarity_features:
            #self.write_semantic_similarity_features(l_span_pos, r_span_pos, syntax_trees)
            for l_main_span_pos in l_main_span_pos_list:
                for r_main_span_pos in r_main_span_pos_list:
                    self.write_semantic_similarity_features(l_main_span_pos, r_main_span_pos, syntax_trees)
            #self.write_semantic_similarity_features(l_span_pos, r_span_pos, syntax_trees)
            
        if self.use_lexical_parallel_features:
            self.write_lexical_parallel_features(l_main_word_list, r_main_word_list)
            #self.write_lexical_parallel_features(l_word_list, r_word_list)
        
        if self.use_syntax_parallel_features:
            self.write_syntactic_parallel_features()
        
        ''' Not doing main-only for the following features because they're borrowed from Hilda '''  
        if self.use_ngram_features:
            self.write_ngrams_features(l_word_list, r_word_list, '')
            self.write_ngrams_features(l_main_word_list, r_main_word_list, 'Main_Nucleus_')
            
        if self.use_lexical_heads or self.use_syntactic_tags or self.use_top_syntactic_tags:
            l_start_i = l_span_pos[0]
            l_end_i = l_span_pos[3]
            l_start_j = l_span_pos[1]
            l_end_j = l_span_pos[4]
            l_num_edus = 1 if not isinstance(L[0], Tree) else len(L[0].leaves())
            (l_ancestor_pos, l_pref_tag, l_suf_tag, l_top_tag) = self.get_conservative_top_ancestors(syntax_trees, breaks, 
                                                                                                       l_start_i, l_end_i, 
                                                                                                       l_start_j, l_end_j, 
                                                                                                       l_num_edus, 'L')
            
            r_start_i = r_span_pos[0]
            r_end_i = r_span_pos[3]
            r_start_j = r_span_pos[1]
            r_end_j = r_span_pos[4]
            r_num_edus = 1 if not isinstance(L[1], Tree) else len(L[1].leaves())
            (r_ancestor_pos, r_pref_tag, r_suf_tag, r_top_tag) = self.get_conservative_top_ancestors(syntax_trees, breaks, 
                                                                                                       r_start_i, r_end_i, 
                                                                                                       r_start_j, r_end_j, 
                                                                                                       r_num_edus, 'R')
            
            if self.use_lexical_heads:
                self.write_lexical_head_features(l_start_i, l_end_i, r_start_i, r_end_i, syntax_trees,
                                                 l_ancestor_pos, l_pref_tag, l_suf_tag, l_top_tag,
                                                 r_ancestor_pos, r_pref_tag, r_suf_tag, r_top_tag)
            
            if self.use_syntactic_tags:
                self.write_syntactic_tag_features(l_pref_tag, l_suf_tag, r_pref_tag, r_suf_tag)
                
            if self.use_top_syntactic_tags:
                self.write_top_syntactic_tag_features(syntax_trees, l_start_i, l_end_i, r_start_i, 
                                         r_end_i, l_ancestor_pos, r_ancestor_pos, l_top_tag, r_top_tag)
                    
        
        label = 1
        bin_line = "%i\t%s\n" % (label, self.features.get_full_vector())
        
        mc_line = bin_line
        
#        print mc_line
        return (mc_line, mc_line)
        #return vectors, vectors
    

    ''' Only consider main edus? '''
    def write_semantic_similarity_features(self, l_span_pos, r_span_pos, syntax_trees):
        ''' use numerous similarity scores to represent semantic similarity for nouns '''
        self.write_semantic_similarity_features_for_nouns(l_span_pos, r_span_pos, syntax_trees)
        ''' cluster verbs into their highest Verbnet classes '''
        self.write_semantic_similarity_feature_for_verbs(l_span_pos, r_span_pos, syntax_trees)
        
        
    def write_semantic_similarity_feature_for_verbs(self, l_span_pos, r_span_pos, syntax_trees):
        left_word_list = self.get_words_from_span_belong_to_pos(l_span_pos, 'V', syntax_trees)
        right_word_list = self.get_words_from_span_belong_to_pos(r_span_pos, 'V', syntax_trees)
        
        #print left_word_list
        #print right_word_list
        left_vn_classid_list = []
        right_vn_classid_list = []
        for word in left_word_list:
            vn_classes = vn.classids(word)
            for vn_classid in vn_classes[ : min(3, len(vn_classes))]:
                scid = vn.shortid(vn_classid)
                scid = scid.split('.')[0].split('-')[0]
                if scid in self.vn_cids:
                    #print 'left', scid
                    self.features['Verbnet_class_id_L'][self.vn_cids[scid]] = 1
                    left_vn_classid_list.append(scid)
            
        for word in right_word_list:
            vn_classes = vn.classids(word)
            for vn_classid in vn_classes[ : min(3, len(vn_classes))]:
                scid = vn.shortid(vn_classid)
                scid = scid.split('.')[0].split('-')[0]
                if scid in self.vn_cids:
                    #print 'right', scid
                    self.features['Verbnet_class_id_R'][self.vn_cids[scid]] = 1
                    right_vn_classid_list.append(scid)
        
        for scid in left_vn_classid_list:
            if scid in right_vn_classid_list:
                #print 'both', scid
                self.features['Verbnet_class_id_both'][self.vn_cids[scid]] = 1
            
            if self.use_pair_features:
                for scid1 in right_vn_classid_list:
                    pair_cid = scid + '#' + scid1
                    if pair_cid in self.vn_cid_pairs:
                        self.features['Verbnet_class_id_L_R'][self.vn_cid_pairs[pair_cid]] = 1
        
    
    
    def write_semantic_similarity_features_for_nouns(self, l_span_pos, r_span_pos, syntax_trees):
        left_word_list = self.get_words_from_span_belong_to_pos(l_span_pos, 'N', syntax_trees)
        right_word_list = self.get_words_from_span_belong_to_pos(r_span_pos, 'N', syntax_trees)
        
        global_path_sim = 0.0
        global_lch_sim = 0.0
        global_wup_sim = 0.0
        global_res_sim = 0.0
        global_jcn_sim = 0.0
        global_lin_sim = 0.0
        
        MAX_SIM = 1.0
        if len(left_word_list) == 0 or len(right_word_list) == 0:
            self.features['path_sim'] = global_path_sim
            self.features['lch_sim'] = global_lch_sim
            self.features['wup_sim'] = global_wup_sim
            self.features['res_sim'] = global_res_sim
            self.features['jcn_sim'] = global_jcn_sim
            self.features['lin_sim'] = global_lin_sim
            return
        
        for word1 in left_word_list:
            max_path_sim = 0.0
            max_lch_sim = 0.0
            max_wup_sim = 0.0
            max_res_sim = 0.0
            max_jcn_sim = 0.0
            max_lin_sim = 0.0
            synsets1 = wn.synsets(word1)
            for word2 in right_word_list:
                synsets2 = wn.synsets(word2)
                for syn1 in synsets1[ : min(3, len(synsets1))]:
                    if syn1.pos != 'n':
                        continue
                    
                    for syn2 in synsets2[ : min(3, len(synsets1))]:
                        if syn2.pos != 'n':
                            continue
                        
                        try:
                            path_sim = syn1.path_similarity(syn2)
                        except Exception, e:
                            path_sim = MAX_SIM
                        try:
                            lch_sim = syn1.lch_similarity(syn2)
                        except Exception, e:
                            lch_sim = MAX_SIM
                        try:
                            wup_sim = syn1.wup_similarity(syn2)
                        except Exception, e:
                            wup_sim = MAX_SIM
                        try:
                            res_sim = syn1.res_similarity(syn2, self.ic)
                        except Exception, e:
                            res_sim = MAX_SIM
                        try:
                            jcn_sim = syn1.jcn_similarity(syn2, self.ic)
                        except Exception, e:
                            jcn_sim = MAX_SIM
                        try:
                            lin_sim = syn1.lin_similarity(syn2, self.ic)
                        except Exception, e:
                            lin_sim = MAX_SIM
                        
                        if path_sim > max_path_sim:
                            max_path_sim = path_sim                     
                        if lch_sim > max_lch_sim:
                            max_lch_sim = lch_sim                       
                        if wup_sim > max_wup_sim:
                            max_wup_sim = wup_sim                       
                        if res_sim > max_res_sim:
                            max_res_sim > res_sim                       
                        if jcn_sim > max_jcn_sim:
                            max_jcn_sim > jcn_sim                       
                        if lin_sim > max_lin_sim:
                            max_lin_sim = lin_sim
            
            global_path_sim += max_path_sim
            global_lch_sim += max_lch_sim
            global_wup_sim += max_wup_sim
            global_res_sim += max_res_sim
            global_jcn_sim += max_jcn_sim
            global_lin_sim += max_lin_sim
        
        denominator = len(left_word_list) * len(right_word_list)    
        global_path_sim /= denominator
        global_lch_sim /= denominator
        global_wup_sim /= denominator
        global_res_sim /= denominator
        global_jcn_sim /= denominator
        global_lin_sim /= denominator
        
        #print global_path_sim, global_lch_sim, global_wup_sim, global_res_sim, global_jcn_sim, global_lin_sim
        self.features['path_sim'] = round(global_path_sim, 2)
        self.features['lch_sim'] = round(global_lch_sim, 2)
        self.features['wup_sim'] = round(global_wup_sim, 2)
        self.features['res_sim'] = round(global_res_sim, 2)
        self.features['jcn_sim'] = round(global_jcn_sim, 2)
        self.features['lin_sim'] = round(global_lin_sim, 2)
        
        
    def get_words_from_span_belong_to_pos(self, span_pos, pos, syntax_trees):
        start_sent_id = span_pos[0]
        start_word_offset = span_pos[2]
        end_sent_id = span_pos[3]
        end_word_offset = span_pos[5]
        
        word_list = []
        if start_sent_id == end_sent_id:
            tree = syntax_trees[start_sent_id]
            leaves = tree.leaves()
            for i in range(start_word_offset, end_word_offset + 1):
                leaf_pos = tree[tree.leaf_treeposition(i)[ : -1]].node
                if leaf_pos.startswith(pos):
                    word_list.append(leaves[i])
        else:
            tree = syntax_trees[start_sent_id]
            leaves = tree.leaves()
            for i in range(start_word_offset, len(leaves)):
                leaf_pos = tree[tree.leaf_treeposition(i)[ : -1]].node
                if leaf_pos.startswith(pos):
                    word_list.append(leaves[i])
            
            for sent_id in range(start_sent_id + 1, end_sent_id):
                tree = syntax_trees[sent_id]
                leaves = tree.leaves()
                for i in range(len(leaves)):
                    leaf_pos = tree[tree.leaf_treeposition(i)[ : -1]].node
                    if leaf_pos.startswith(pos):
                        word_list.append(leaves[i])
                
            tree = syntax_trees[end_sent_id]
            leaves = tree.leaves()
            for i in range(0, end_word_offset + 1):
                leaf_pos = tree[tree.leaf_treeposition(i)[ : -1]].node
                if leaf_pos.startswith(pos):
                    word_list.append(leaves[i])
        
        return word_list
    
    def write_word_pairs_features(self, left_word_list, right_word_list):
        for word1 in left_word_list:
            for word2 in right_word_list:
                #print word1, word2
                word_pair = word1.lower() + '_' + word2.lower()
                if word_pair in self.word_pairs_dict:
                    self.features['Word_pair'][self.word_pairs_dict[word_pair]] = 1
        
    
    def get_word_list_from_main_edus(self, span):
        word_list = []
        if isinstance(span, Tree):
            all_main_pos = get_main_edus(span)
            for main_pos in all_main_pos:
                word_list.extend(self.get_word_list_from_span(span[main_pos]))
        else:
            word_list = self.get_word_list_from_span(span)
            
        return word_list
    
    def get_word_list_from_span(self, span):
        word_list = []
        if isinstance(span, Tree):
            for leaf in span.leaves():
                word_list.extend(leaf)
        else:
            word_list = span
            
        return word_list
    
    def write_contextual_features(self, prev_stump, next_stump):
        if prev_stump is not None:
            prev_RST_rel = 'NO-REL' if not isinstance(prev_stump, ParseTree) else prev_stump.node
            self.features['prev_RST_Tree'][self.relations[prev_RST_rel] - 1] = 1
        
        if next_stump is not None:
            next_RST_rel = 'NO-REL' if not isinstance(next_stump, ParseTree) else next_stump.node
            self.features['next_RST_Tree'][self.relations[next_RST_rel] - 1] = 1
            
    
    
    def write_word_dep_types_features(self, deps, syntax_trees, l_span_pos_list, r_span_pos_list):
        left_word_dep_types = []
        for l_span_pos in l_span_pos_list:
            left_word_dep_types.extend(self.write_word_dep_types_features_from_span(deps, syntax_trees, l_span_pos, 'L'))
            
        right_word_dep_types = []
        for r_span_pos in r_span_pos_list:
            right_word_dep_types.extend(self.write_word_dep_types_features_from_span(deps, syntax_trees, r_span_pos, 'R'))
        
        for l_word_dep in left_word_dep_types:
            if l_word_dep in right_word_dep_types:
                if l_word_dep in self.word_deps_both:
                    #print word_dep
                    self.features['Word_dep_both'][self.word_deps_both[l_word_dep]] = 1
            
            if self.use_pair_features:
                for r_word_dep in right_word_dep_types:
                    word_dep_pair = l_word_dep + '#' + r_word_dep
                    if word_dep_pair in self.word_dep_pairs:
                        self.features['Word_dep_L_R'][self.word_dep_pairs[word_dep_pair]] = 1
            
                
                
    def write_word_dep_types_features_from_span(self, deps, syntax_trees, span_pos, suffix):
        start_sent_id = span_pos[0]
        start_word_offset = span_pos[2]
        end_sent_id = span_pos[3]
        end_word_offset = span_pos[5]
        
        sent2deps = []
        if start_sent_id == end_sent_id:
            sent_deps = []
            for (dep_type, governor_word, governor_word_number, dependent_word, dependent_word_number) in deps[start_sent_id]:
                if governor_word_number >= start_word_offset and governor_word_number <= end_word_offset \
                and dependent_word_number >= start_word_offset and dependent_word_number <= end_word_offset:
                    sent_deps.append((dep_type, governor_word, governor_word_number, dependent_word, dependent_word_number))
            
            sent2deps.append(sent_deps)
        else:
            sent_deps = []
            for (dep_type, governor_word, governor_word_number, dependent_word, dependent_word_number) in deps[start_sent_id]:
                if governor_word_number >= start_word_offset and dependent_word_number >= start_word_offset:
                    sent_deps.append((dep_type, governor_word, governor_word_number, dependent_word, dependent_word_number))
            sent2deps.append(sent_deps)
            
            if end_sent_id > start_sent_id + 1:
                for i in range(start_sent_id + 1, end_sent_id):
                    sent2deps.append(deps[i])
            
            sent_deps = []
            for (dep_type, governor_word, governor_word_number, dependent_word, dependent_word_number) in deps[end_sent_id]:
                if governor_word_number <= end_word_offset and dependent_word_number <= end_word_offset:
                    sent_deps.append((dep_type, governor_word, governor_word_number, dependent_word, dependent_word_number))
            sent2deps.append(sent_deps)
        
        word_dep_types = []   
        for i in range(len(sent2deps)):
            sent_deps = sent2deps[i]
            syntax_tree = syntax_trees[start_sent_id + i]
            #print syntax_tree
            #print sent_deps
            for (dep_type, governor_word, governor_word_number, dependent_word, dependent_word_number) in sent_deps:
                #print dep_type, governor_word, governor_word_number, dependent_word, dependent_word_number
                governor_tag = syntax_tree[syntax_tree.leaf_treeposition(governor_word_number)[ : -1]].node
                governor_word = governor_word.lower()
                if governor_tag.startswith('V'):
                    governor_word = self.lmtzr.lemmatize(governor_word, 'v')
                elif governor_tag.startswith('N'):
                    governor_word = self.lmtzr.lemmatize(governor_word, 'n')
                
                dep_type = type2class[dep_type.split('_')[0]]
                word_dep = governor_word + '_' + dep_type
                #print word_dep
                if (suffix == 'L' and word_dep in self.word_deps_L) or (suffix == 'R' and word_dep in self.word_deps_R):
                    #print word_dep
                    word_dep_types.append(word_dep)
                    if suffix == 'L':
                        self.features['Word_dep_' + suffix][self.word_deps_L[word_dep]] = 1
                    else:
                        self.features['Word_dep_' + suffix][self.word_deps_R[word_dep]] = 1
                      
                dependent_tag = syntax_tree[syntax_tree.leaf_treeposition(dependent_word_number)[ : -1]].node
                dependent_word = dependent_word.lower()
                if dependent_tag.startswith('V'):
                    dependent_word = self.lmtzr.lemmatize(dependent_word, 'v')
                elif dependent_tag.startswith('N'):
                    dependent_word = self.lmtzr.lemmatize(dependent_word, 'n')
                
                word_dep = dependent_word + '_' + dep_type
                #print word_dep
                if (suffix == 'L' and word_dep in self.word_deps_L) or (suffix == 'R' and word_dep in self.word_deps_R):
                    #print word_dep
                    word_dep_types.append(word_dep)
                    if suffix == 'L':
                        self.features['Word_dep_' + suffix][self.word_deps_L[word_dep]] = 1
                    else:
                        self.features['Word_dep_' + suffix][self.word_deps_R[word_dep]] = 1
        
        return word_dep_types
    
                
    def write_syntax_production_rules(self, syntax_trees, l_span_pos_list, r_span_pos_list):
        left_production_list = []
        for l_span_pos in l_span_pos_list:
            left_production_list.extend(self.write_syntax_production_rules_from_span(syntax_trees, l_span_pos, 'L'))
            
        right_production_list = []
        for r_span_pos in r_span_pos_list:
            right_production_list.extend(self.write_syntax_production_rules_from_span(syntax_trees, r_span_pos, 'R'))
            
        for production in left_production_list:
            if production in right_production_list:
                if production in self.syntax_production_rules_both:
                    self.features['Syntax_Production_Rule_both'][self.syntax_production_rules_both[production]] = 1
                    
            if self.use_pair_features:
                for production_r in right_production_list:
                    pair_production = production + '#' + production_r
                    if pair_production in self.syntax_production_rule_pairs:
                        self.features['Syntax_Production_Rule_L_R'][self.syntax_production_rule_pairs[pair_production]] = 1
        
    ''' Consider main edus only? '''
    def write_syntax_production_rules_from_span(self, syntax_trees, span_pos, suffix):
        start_sent_id = span_pos[0]
        start_word_offset = span_pos[2]
        end_sent_id = span_pos[3]
        end_word_offset = span_pos[5]
        
        production_list = []
        if start_sent_id == end_sent_id:
            syntax_tree = syntax_trees[start_sent_id]
            production_list = self.get_syntax_production_rules_from_subtrees(syntax_tree, start_word_offset, end_word_offset)
        else:
            syntax_tree = syntax_trees[start_sent_id]
            production_list.extend(self.get_syntax_production_rules_from_subtrees(syntax_tree, start_word_offset, len(syntax_tree.leaves()) - 1))
            for i in range(start_sent_id + 1, end_sent_id):
                syntax_tree = syntax_trees[i]
                production_list.extend(self.get_syntax_production_rules_from_subtrees(syntax_tree, 0, len(syntax_tree.leaves()) - 1))
            
            syntax_tree = syntax_trees[end_sent_id]
            production_list.extend(self.get_syntax_production_rules_from_subtrees(syntax_tree, 0, end_word_offset))
    
        production_str_list = []
        for production in production_list:
            production = str(production)
            if (suffix == 'L' and production in self.syntax_production_rules_L) \
            or (suffix == 'R' and production in self.syntax_production_rules_R):
                #print production
                production_str_list.append(production)
                if suffix == 'L':
                    self.features['Syntax_Production_Rule_' + suffix][self.syntax_production_rules_L[production]] = 1
                else:
                    self.features['Syntax_Production_Rule_' + suffix][self.syntax_production_rules_R[production]] = 1
        
        return production_str_list
            
    
    def get_syntax_production_rules_from_subtrees(self, syntax_tree, start_word_offset, end_word_offset):
        production_list = []
        start_tree_pos = syntax_tree.leaf_treeposition(start_word_offset)[ : -1]
        spanning_tree_pos = syntax_tree.treeposition_spanning_leaves(start_word_offset, end_word_offset + 1)
        tot = start_word_offset
        #print 'start_tree_pos', start_tree_pos
        #print 'spanning_tree_pos', spanning_tree_pos
        while tot < end_word_offset:
            i = len(start_tree_pos) - 1
            subtree_pos = start_tree_pos
            while i >= len(spanning_tree_pos):
                if start_tree_pos[i] != 0:
                    break
                subtree_pos = start_tree_pos[ : i + 1]
                i -= 1
            
            #print 'start_tree_pos', start_tree_pos
            #print 'subtree_pos', subtree_pos    
            subtree = syntax_tree[subtree_pos]
            #print subtree
            production_list.extend(subtree.productions())
            tot += len(subtree.leaves())
#            if tot == end_word_offset + 1:
#                break
            #print 'start', start_word_offset, 'tot', tot, 'end', end_word_offset
            start_tree_pos = syntax_tree.leaf_treeposition(tot)[ : -1]
            spanning_tree_pos = syntax_tree.treeposition_spanning_leaves(tot, end_word_offset + 1)
            #print 'start_tree_pos', start_tree_pos
            #print 'spanning_tree_pos', spanning_tree_pos
            #print
        
        return production_list
    
    
    def write_RST_prodution_rules(self, L):
        #print L[0]
        left_span = L[0]
        right_span = L[1]
        left_production_list = self.get_RST_production_rules_from_subtree(left_span)
        right_production_list = self.get_RST_production_rules_from_subtree(right_span)
        
        for production in left_production_list:
            if production in self.RST_production_rules_L:
                #print production
                self.features['RST_Production_Rule_L'][self.RST_production_rules_L[production]] = 1
                if production in right_production_list and production in self.RST_production_rules_both:
                    self.features['RST_Production_Rule_both'][self.RST_production_rules_both[production]] = 1
           
            if self.use_pair_features:    
                for production_r in right_production_list:
                    pair_production = production + '#' + production_r
                    if pair_production in self.RST_production_rules_L_R:
                        self.features['RST_Production_Rule_L_R'][self.RST_production_rules_L_R[pair_production]] = 1
        
        #print
        #print L[1]      
        
        for production in right_production_list:
            if production in self.RST_production_rules_R:
                #print production
                self.features['RST_Production_Rule_R'][self.RST_production_rules_R[production]] = 1
    
    
    def write_cue_phrase_features(self, l_word_list, r_word_list):
        left_str = " " + ' '.join(l_word_list) + " "
        right_str = " " + ' '.join(r_word_list) + " "
        for (cue, index) in self.cue_phrases_L.items():
            sent_part = int(cue.split('#')[0])
            cue_phrase = cue.split('#')[1]
            
            l_pos = left_str.find(" " + cue_phrase + " ")
            if l_pos >= 0:
                l_sent_part = int(self.nb_sentence_parts * float(l_pos)/(len(left_str)-len(cue_phrase)+1))
                if l_sent_part == sent_part:
                    #print cue, cue_phrase, index
                    self.features['_Cue_Phrases_L'][index] = 1

        for (cue, index) in self.cue_phrases_R.items():
            #print cue, index
            sent_part = int(cue.split('#')[0])
            cue_phrase = cue.split('#')[1]
            r_pos = right_str.find(" " + cue_phrase + " ")
            if r_pos >= 0:
                r_sent_part = int(self.nb_sentence_parts * float(r_pos)/(len(right_str)-len(cue_phrase)+1))
                if r_sent_part == sent_part:
                    self.features['_Cue_Phrases_R'][index] = 1
        
        for (cue, index) in self.cue_phrases_both.items():
            sent_part = int(cue.split('#')[0])
            cue_phrase = cue.split('#')[1]
            l_pos = left_str.find(" " + cue_phrase + " ")
            r_pos = right_str.find(" " + cue_phrase + " ")
            if l_pos >= 0 and r_pos >= 0:
                l_sent_part = int(self.nb_sentence_parts * float(l_pos)/(len(left_str)-len(cue_phrase)+1))
                r_sent_part = int(self.nb_sentence_parts * float(r_pos)/(len(right_str)-len(cue_phrase)+1))
                if l_sent_part == r_sent_part and l_sent_part == sent_part:
                    self.features['_Cue_Phrases_both'][index] = 1
                
        if self.use_pair_features:
            for (cue, index) in self.cue_phrases_L_R.items():
                #print cue, index
                sent_part_l = int(cue.split('#')[0])
                sent_part_r = int(cue.split('#')[1])
                cue_phrase_l = cue.split('#')[2]
                cue_phrase_r = cue.split('#')[3]
                l_pos = left_str.find(" " + cue_phrase_l + " ")
                r_pos = right_str.find(" " + cue_phrase_r + " ")
                if l_pos >= 0 and r_pos >= 0:
                    l_sent_part = int(self.nb_sentence_parts * float(l_pos)/(len(left_str)-len(cue_phrase_l)+1))
                    r_sent_part = int(self.nb_sentence_parts * float(r_pos)/(len(right_str)-len(cue_phrase_r)+1))
                    if l_sent_part == sent_part_l and r_sent_part == sent_part_r:
                        self.features['_Cue_Phrases_L_R'][index] = 1        
        
        
    def write_lexical_parallel_features(self, l_word_list, r_word_list):
        ''' common word counts '''
#        print 'l_word_list', l_word_list
#        print 'r_word_list', r_word_list
#        print
        common_word_cnt = 0
        for i in range(len(l_word_list)):
            for j in range(len(r_word_list)):
                k = 0
                while k < min(len(l_word_list) - i, len(r_word_list) - j):
                    if l_word_list[i + k].lower() != r_word_list[j + k].lower():
                        break
                    
                    k += 1
                
                common_word_cnt += k
        
        self.features['Common_word_count'] = common_word_cnt
        
    
    def write_syntactic_parallel_features(self):
        pass
        
#
    def write_ngrams_features(self, left, right, feature_pref = ''):
        for n in range(1, self.ngram_len + 1):
            ngram_l_pref = get_one_ngram(left, n)
            #print ngram_l_pref
            if ngram_l_pref in self.ngram_l_pref:
                self.features[feature_pref + 'NGrams_pref_L'][self.ngram_l_pref[ngram_l_pref]] = 1
                    
            ngram_l_suf = get_one_ngram(left, -n)
            if ngram_l_suf in self.ngram_l_suf:
                self.features[feature_pref + 'NGrams_suf_L'][self.ngram_l_suf[ngram_l_suf]] = 1
            
            #print right
            ngram_r_pref = get_one_ngram(right, n)
            if ngram_r_pref in self.ngram_r_pref:
                self.features[feature_pref + 'NGrams_pref_R'][self.ngram_r_pref[ngram_r_pref]] = 1
                    
            if ngram_l_pref == ngram_r_pref and ngram_l_pref in self.ngram_both_pref:
                self.features[feature_pref + 'NGrams_pref_both'][self.ngram_both_pref[ngram_r_pref]] = 1
                    
            ngram_r_suf = get_one_ngram(right, -n)
            if ngram_r_suf in self.ngram_r_suf:
                self.features[feature_pref + 'NGrams_suf_R'][self.ngram_r_suf[ngram_r_suf]] = 1
                    
            if ngram_l_suf == ngram_r_suf and ngram_r_suf in self.ngram_both_suf:
                self.features[feature_pref + 'NGrams_suf_both'][self.ngram_both_suf[ngram_r_suf]] = 1

            if self.use_pair_features:
                pref_l_pref_r = ngram_l_pref + '#' + ngram_r_pref
                if pref_l_pref_r in self.ngram_l_pref_r_pref:
                    self.features[feature_pref + 'NGrams_pref_L_pref_R'][self.ngram_l_pref_r_pref[pref_l_pref_r]] = 1
                
                pref_l_suf_r = ngram_l_pref + '#' + ngram_r_suf
                if pref_l_suf_r in self.ngram_l_pref_r_suf:
                    self.features[feature_pref + 'NGrams_pref_L_suf_R'][self.ngram_l_pref_r_suf[pref_l_suf_r]] = 1
                
                suf_l_pref_r = ngram_l_suf + '#' + ngram_r_pref
                if suf_l_pref_r in self.ngram_l_suf_r_pref:
                    self.features[feature_pref + 'NGrams_suf_L_pref_R'][self.ngram_l_suf_r_pref[suf_l_pref_r]] = 1
                
                suf_l_suf_r = ngram_l_suf + '#' + ngram_r_suf
                if suf_l_suf_r in self.ngram_l_suf_r_suf:
                    self.features[feature_pref + 'NGrams_suf_L_suf_R'][self.ngram_l_suf_r_suf[suf_l_suf_r]] = 1
    
    
    def write_lexical_head_features(self, l_start_i, l_end_i, r_start_i, r_end_i, syntax_trees,
                                    l_ancestor_pos, l_pref_tags, l_suf_tags, l_top_tag,
                                    r_ancestor_pos, r_pref_tags, r_suf_tags, r_top_tag):
        if l_start_i == r_end_i:
            common_ancestor_pos = common_ancestor(l_ancestor_pos, r_ancestor_pos)
        else:
            common_ancestor_pos = ()
            
        dist_ancestor_l = len(l_ancestor_pos) - len(common_ancestor_pos)
        dist_ancestor_r = len(r_ancestor_pos) - len(common_ancestor_pos)

        if dist_ancestor_l:
            l_head = filter_lexical_head(syntax_trees[l_start_i].get_head(l_ancestor_pos))
            if l_head and l_head in self.lexical_heads_L:
                self.features['Top_lexical_head_L'][self.lexical_heads_L[l_head]] = 1
        else:
            l_head = None
                            
        if dist_ancestor_r:
            r_head = filter_lexical_head(syntax_trees[r_start_i].get_head(r_ancestor_pos))
            if r_head and r_head in self.lexical_heads_R:
                self.features['Top_lexical_head_R'][self.lexical_heads_R[r_head]] = 1
        else:
            r_head = None
            
        
        if l_head and r_head:
            if l_head == r_head and l_head in self.lexical_heads_both:
                self.features['Top_lexical_head_both'][self.lexical_heads_both[l_head]] = 1
            
            if self.use_pair_features:
                head_pair = l_head + '#' + r_head
                if head_pair in self.lexical_head_pairs:
                    self.features['Top_lexical_head_L_R'][self.lexical_head_pairs[head_pair]] = 1
    
        if common_ancestor_pos:
            if dist_ancestor_l == 0 or dist_ancestor_r == 0: 
                if dist_ancestor_l == 0:# L >> R
                    dom_pos = r_ancestor_pos[:-1]
                else: # R >> L
                    dom_pos = l_ancestor_pos[:-1]
    
                head = filter_lexical_head(syntax_trees[l_start_i].get_head(dom_pos))
                if head and head in self.lexical_heads_dominated:
                    self.features['Dominated_lexical_head'][self.lexical_heads_dominated[head]] = 1
                        
    
    def write_syntactic_tag_features(self, l_pref_tag, l_suf_tag, r_pref_tag, r_suf_tag):
        if l_pref_tag and l_pref_tag in self.syntactic_tags_pref_L:
            self.features['Syntactic_tags_pref_L'][self.syntactic_tags_pref_L[l_pref_tag]] = 1
                
        if l_suf_tag and l_suf_tag in self.syntactic_tags_suf_L:
            self.features['Syntactic_tags_suf_L'][self.syntactic_tags_suf_L[l_suf_tag]] = 1
                
        if r_pref_tag and r_pref_tag in self.syntactic_tags_pref_R:
            self.features['Syntactic_tags_pref_R'][self.syntactic_tags_pref_R[r_pref_tag]] = 1
                
        if l_pref_tag and r_pref_tag and l_pref_tag == r_pref_tag and l_pref_tag in self.syntactic_tags_pref_both:
            self.features['Syntactic_tags_pref_both'][self.syntactic_tags_pref_both[l_pref_tag]] = 1
                
        if r_suf_tag and r_suf_tag in self.syntactic_tags_suf_R:
            self.features['Syntactic_tags_suf_R'][self.syntactic_tags_suf_R[r_suf_tag]] = 1
                                   
        if l_suf_tag and r_suf_tag and l_suf_tag == r_suf_tag and l_suf_tag in self.syntactic_tags_suf_both:
            self.features['Syntactic_tags_suf_both'][self.syntactic_tags_suf_both[l_suf_tag]] = 1

        if self.use_pair_features:
            if l_pref_tag and r_pref_tag:
                pair_tag = l_pref_tag + '#' + r_pref_tag
                if pair_tag in self.syntactic_tag_pairs_pref_l_pref_r:
                    self.features['Syntactic_tags_pref_L_pref_R'][self.syntactic_tag_pairs_pref_l_pref_r[pair_tag]] = 1
            
            if l_pref_tag and r_suf_tag:
                pair_tag = l_pref_tag + '#' + r_suf_tag
                if pair_tag in self.syntactic_tag_pairs_pref_l_suf_r:
                    self.features['Syntactic_tags_pref_L_suf_R'][self.syntactic_tag_pairs_pref_l_suf_r[pair_tag]] = 1
            
            if l_suf_tag and r_pref_tag:
                pair_tag = l_suf_tag + '#' + r_pref_tag
                if pair_tag in self.syntactic_tag_pairs_suf_l_pref_r:
                    self.features['Syntactic_tags_suf_L_pref_R'][self.syntactic_tag_pairs_suf_l_pref_r[pair_tag]] = 1
            
            if l_suf_tag and r_suf_tag:
                pair_tag = l_suf_tag + '#' + r_suf_tag
                if pair_tag in self.syntactic_tag_pairs_suf_l_suf_r:
                    self.features['Syntactic_tags_suf_L_suf_R'][self.syntactic_tag_pairs_suf_l_suf_r[pair_tag]] = 1
    
    
    def write_top_syntactic_tag_features(self, syntax_trees, l_start_i, l_end_i, r_start_i, 
                                         r_end_i, l_ancestor_pos, r_ancestor_pos, l_top_tag, r_top_tag):
        if l_top_tag and l_top_tag in self.top_syntactic_tags_L:
            self.features['Top_Syntactic_tag_L'][self.top_syntactic_tags_L[l_top_tag]] = 1
        
        if r_top_tag and r_top_tag in self.top_syntactic_tags_R:
            self.features['Top_Syntactic_tag_R'][self.top_syntactic_tags_R[r_top_tag]] = 1
        
        if l_top_tag and r_top_tag:
            if l_top_tag == r_top_tag and l_top_tag in self.top_syntactic_tags_both:
#                print l_top_tag
#                print self.top_syntactic_tags_both
                self.features['Top_Syntactic_tag_both'][self.top_syntactic_tags_both[l_top_tag]] = 1
            
            if self.use_pair_features:
                tag_pair = l_top_tag + '#' + r_top_tag
                #print tag_pair
                if tag_pair in self.top_syntactic_tags_L_R:
                    #print tag_pair
                    self.features['Top_Syntactic_tag_L_R'][self.top_syntactic_tags_L_R[tag_pair]] = 1
        
        if l_start_i == r_end_i:
            common_ancestor_pos = common_ancestor(l_ancestor_pos, r_ancestor_pos)
        else:
            common_ancestor_pos = ()
            
        dist_ancestor_l = len(l_ancestor_pos) - len(common_ancestor_pos)
        dist_ancestor_r = len(r_ancestor_pos) - len(common_ancestor_pos)

        if common_ancestor_pos:
            if dist_ancestor_l == 0 or dist_ancestor_r == 0: 
                if dist_ancestor_l == 0:# L >> R
                    dom_pos = r_ancestor_pos[:-1]
                else: # R >> L
                    dom_pos = l_ancestor_pos[:-1]
  
                tag = filter_syntactic_tag(syntax_trees[l_start_i].get_syntactic_tag(dom_pos))
                if tag and tag in self.top_syntactic_tags_dominated:
                    self.features['Top_Syntactic_tag_dominated'][self.top_syntactic_tags_dominated[tag]] = 1
    
                         
    def get_RST_production_rules_from_subtree(self, subtree):
        if not isinstance(subtree, Tree):
            return []
        
        left_span = subtree[0]
        right_span = subtree[1]
        head_rel = subtree.node
        left_rel = left_span.node if isinstance(left_span, Tree) else 'NO-REL'
        right_rel = right_span.node if isinstance(right_span, Tree) else 'NO-REL'
        production = head_rel + '_' + left_rel + '_' + right_rel
        production_list = [production]
        
        production_list.extend(self.get_RST_production_rules_from_subtree(left_span))
        production_list.extend(self.get_RST_production_rules_from_subtree(right_span))
        return production_list
    
                
    def get_span_pos(self, span, syntax_trees, breaks, offset):
        tot = 0
        for (i, sent_breaks) in enumerate(breaks):
            if tot + len(sent_breaks) > offset:
                break;
            tot += len(sent_breaks)
    
        start_sent_id = i # sent_id
        start_edu_offset = offset - tot # edu_offset in this sent
        start_word_offset = breaks[start_sent_id][start_edu_offset][0]

        tot = 0
        i = start_sent_id
        j = start_edu_offset
        num_edus = 1 if not isinstance(span, Tree) else len(span.leaves())
        
        # end_i, end_j are *inclusive*
        while tot < num_edus:
            end_i = i
            end_j = j
            #from_syntax_tree += syntax_trees[i].leaves()[breaks[i][j][0]:breaks[i][j][1]]
            tot += 1
            j += 1
            if j >= len(breaks[i]):
                i +=1
                j = 0
        
        end_sent_id = end_i
        end_edu_offset = end_j
        end_word_offset = min(breaks[end_i][end_j][1], len(syntax_trees[end_i].leaves())) - 1
        
        return (start_sent_id, start_edu_offset, start_word_offset, end_sent_id, end_edu_offset, end_word_offset)

    def get_conservative_top_ancestors(self, syntax_trees, breaks, start_i, end_i, start_j, end_j, num_edus, suffix):
        exclude_words = ",.`':;!?"
        if start_i >= len(breaks):
            print start_i
            print breaks
        if start_j >= len(breaks[start_i]):
            print start_i, start_j
            print breaks[start_i]
            print breaks

        start_word = breaks[start_i][start_j][0]
        
        while start_word < len(syntax_trees[start_i].leaves()) and not syntax_trees[start_i].leaves()[start_word].strip(exclude_words):
            start_word += 1
    
        end_word = min(breaks[end_i][end_j][1], len(syntax_trees[end_i].leaves()))
       
        if end_i == start_i:
            while (syntax_trees[start_i].leaves()[end_word-1] == '<s>'
                   or syntax_trees[start_i].leaves()[end_word-1] == '<p>'
                   or not syntax_trees[start_i].leaves()[end_word-1].strip(exclude_words)):
                end_word -= 1
            
            if start_word >= end_word: ### DEBUG
                real = min(breaks[end_i][end_j][1], len(syntax_trees[end_i].leaves()))
                print start_word, real, "->", end_word
                print breaks[end_i][end_j]
                print syntax_trees[start_i].leaves()[start_word:]
                print real
                print syntax_trees[start_i].leaves()[end_word:real]
            
            ancestor_pos = syntax_trees[start_i].treeposition_spanning_leaves(start_word, end_word)
            start_leaf_pos = syntax_trees[start_i].leaf_treeposition(start_word)
            end_leaf_pos = syntax_trees[start_i].leaf_treeposition(end_word - 1)
            
            start_word_str = syntax_trees[start_i].leaves()[start_word]
            end_word_str = syntax_trees[start_i].leaves()[end_word - 1]
            if not isinstance(syntax_trees[start_i][ancestor_pos], Tree):
                conservative_top_pos = ancestor_pos[ : -1]
            else:
                if syntax_trees[start_i][ancestor_pos].leaves()[0] == start_word_str \
                and syntax_trees[start_i][ancestor_pos].leaves()[-1] == end_word_str:
                    conservative_top_pos = ancestor_pos
                else:
                    if suffix == 'R':
                        for j in range(len(start_leaf_pos) - 1, 0, -1):
                            if syntax_trees[start_i][start_leaf_pos[: j]].leaves()[0] != start_word_str \
                            or len(syntax_trees[start_i][start_leaf_pos[: j]].leaves()) + start_word >= end_word:
                                break
                        
                        conservative_top_pos = start_leaf_pos[: j + 1]
                    else:
                        for j in range(len(end_leaf_pos) - 1, 0, -1):
                            if syntax_trees[start_i][end_leaf_pos[: j]].leaves()[-1] != end_word_str \
                            or end_word - len(syntax_trees[start_i][end_leaf_pos[: j]].leaves()) <= start_word:
                                break
                        
                        conservative_top_pos = end_leaf_pos[: j + 1]
            
            conservative_top_tag = syntax_trees[start_i][conservative_top_pos].node
        else:
            conservative_top_pos = ()
            conservative_top_tag = None

        if start_word < len(syntax_trees[start_i].leaves()):
            pref_tag = syntax_trees[start_i][syntax_trees[start_i].leaf_treeposition(start_word)[:-1]].node
        else:
            pref_tag = None
        
        if end_word > 0 :
            suf_tag = syntax_trees[end_i][syntax_trees[end_i].leaf_treeposition(end_word-1)[:-1]].node
        else:
            suf_tag = None
            
        return (conservative_top_pos, pref_tag, suf_tag, conservative_top_tag) 