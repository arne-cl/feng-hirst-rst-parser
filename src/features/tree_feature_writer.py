'''
Created on 2013-12-22

@author: Wei
'''
import utils.serialize
from utils.rst_lib import *

class CRFTreeFeatureWriter:
    def __init__(self, verbose):
        self.features = set()
        
        self.verbose = verbose
        
        self.cue_phrases = utils.serialize.loadData('cue_phrases')
        if self.verbose:
            print 'Loaded %d cue phrases for CRF labeling' % len(self.cue_phrases)
        
    
    def write_organization_features(self, constituent, scope, unit, position):
        '''
        1. number of EDUs in unit1 or unit2.
        2. number of tokens in unit1 or unit2.
        3. distance of unit1 in EDUs to the beginning (or to the end) of the sentence.
        4. distance of unit2 in EDUs to the beginning (or to the end) of the sentence.
        '''
        
        num_edus = constituent.get_num_edus()

        if scope:
            assert constituent.start_sent_id == constituent.end_sent_id
            start_edu_offset = constituent.l_start - constituent.doc.sentences[constituent.start_sent_id].start_edu
            end_edu_offset = constituent.doc.sentences[constituent.end_sent_id].end_edu - constituent.r_end
  

            if start_edu_offset == 0:
                self.features.add("First_EDU_Unit%d@%d" % (unit, position))
            
            if end_edu_offset == 0:
                self.features.add("Last_EDU_Unit%d@%d" % (unit,position))
            

        subtree_height = constituent.get_subtree_height()
        if subtree_height == 1:
            self.features.add('Bottom_Level_Subtree_Unit%d@%d' % (unit, position))
            
        return num_edus, subtree_height
        

    def write_Ngram_features(self, constituent, unit, position):
        '''
        N = 1, 2, 3
        1. Beginning (or end) lexical N-grams in unit 1.
        2. Beginning (or end) lexical N-grams in unit 2.
        3. Beginning (or end) POS N-grams in unit 1.
        4. Beginning (or end) POS N-grams in unit 2.
        '''
        
        for n in range(1, 4):
#            if self.verbose:
#                print 'stump', stump
#                print breaks
#                print offset
#                print
    
    
            pref_PoS_ngrams = constituent.get_POS_ngram(n)
            self.features.add('Beginning_POS_%d-grams_Unit%d=%s@%d' % (n, unit, '-'.join(pref_PoS_ngrams), position))        
            
            
            pref_lexical_ngrams = constituent.get_ngram(n)
            self.features.add('Beginning_Lexical_%d-grams_Unit%d=%s@%d' % (n, unit, '-'.join(pref_lexical_ngrams), position))


            end_lexical_ngrams = constituent.get_ngram(-n)
            self.features.add('End_Lexical_Lexical_%d-grams_Unit%d=%s@%d' % (n, unit, '-'.join(end_lexical_ngrams), position))


            end_PoS_ngrams = constituent.get_POS_ngram(-n)
            self.features.add('End_POS_%d-grams_Unit%d=%s@%d' % (n, unit, '-'.join(end_PoS_ngrams), position))

 
        
    def write_dominance_set_features(self, L, R, position):
        assert L.doc == R.doc
        
        l_start_sent = L.start_sent_id
        l_start_word = L.start_word
        l_end_sent = L.end_sent_id
        l_end_word = L.end_word
        
        r_start_sent = R.start_sent_id
        r_start_word = R.start_word
        r_end_sent = R.end_sent_id
        r_end_word = R.end_word
        
        
        l_subtrees_top_tags = []
        if l_start_sent == l_end_sent:
            t = L.doc.sentences[l_start_sent].parse_tree
            
            l_ancestor_pos = t.treeposition_spanning_leaves(l_start_word, l_end_word)
            if l_end_word == l_start_word + 1:
                l_ancestor_pos = l_ancestor_pos[ : -1]
                
            l_ancestor_subtree = t[l_ancestor_pos]
            
            self.features.add('Top_syntactic_tag_Unit1=%s@%d' % (l_ancestor_subtree.node, position))
            
            if len(l_ancestor_subtree.leaves()) == l_end_word - l_start_word:
                self.features.add('Valid_syntax_subtree_Unit1@%d' % position)
            
            l_subtrees = utils.utils.get_syntactic_subtrees(t, l_start_word, l_end_word)
            self.features.add('Num_Syntax_subtrees_Unit1=%d@%d' % (len(l_subtrees), position))
            
            if len(l_subtrees) == 1:
                self.features.add('Top_Syntax_tag_Unit1=%s@%d' % (l_subtrees[0].node, position))
                

            l_subtree_top_tags = []
            for (i, subtree) in enumerate(l_subtrees):
                l_subtree_top_tags.append(subtree.node)

            l_subtrees_top_tags.append(l_subtree_top_tags)
        else:
            l_ancestor_pos = ()
          
        r_subtrees_top_tags = []
        if r_start_sent == r_end_sent:
            t = R.doc.sentences[r_start_sent].parse_tree

            
            r_ancestor_pos = t.treeposition_spanning_leaves(r_start_word, r_end_word)
            if r_end_word == r_start_word + 1:
                r_ancestor_pos = r_ancestor_pos[ : -1]
                
            r_ancestor_subtree = t[r_ancestor_pos]
            
            self.features.add('Top_syntactic_tag_Unit2=%s@%d' % (r_ancestor_subtree.node, position))
            
            if len(r_ancestor_subtree.leaves()) == r_end_word - r_start_word:
                self.features.add('Valid_syntax_subtree_Unit2@%d' % position)
            
            r_subtrees = utils.utils.get_syntactic_subtrees(t, r_start_word, r_end_word)
            self.features.add('Num_Syntax_subtrees_Unit2=%d@%d' % (len(r_subtrees), position))
            
            if len(r_subtrees) == 1:
                self.features.add('Top_Syntax_tag_Unit2=%s@%d' % (r_subtrees[0].node, position))
                
            r_subtree_top_tags = []
            for (i, subtree) in enumerate(r_subtrees):
                r_subtree_top_tags.append(subtree.node)

            r_subtrees_top_tags.append(r_subtree_top_tags)
        else:
            r_ancestor_pos = ()
        
        min_top_tags_edit_distance = 1.0
        for l_top_tags in l_subtrees_top_tags:
            for r_top_tags in r_subtrees_top_tags:
                distance = utils.utils.compute_edit_distance(l_top_tags, r_top_tags)
                distance_norm = distance * 1.0 / max(len(l_top_tags), len(r_top_tags))
                min_top_tags_edit_distance = min(min_top_tags_edit_distance, distance_norm)
        
        self.features.add('Min_Subtrees_Top_Syntactic_Tags_Distance=%.3f@%d' % (min_top_tags_edit_distance,
                                                                                position))
        
        if l_start_sent != r_end_sent:
            return
        
        t = L.doc.sentences[l_start_sent].parse_tree
        common_ancestor_pos = common_ancestor(l_ancestor_pos, r_ancestor_pos)
           
        dist_ancestor_l = len(l_ancestor_pos) - len(common_ancestor_pos)
        dist_ancestor_r = len(r_ancestor_pos) - len(common_ancestor_pos)
        
        if dist_ancestor_l:
            head = filter_lexical_head(t.get_head(l_ancestor_pos))
            self.features.add('Top_lexical_head_Unit1=%s@%d' % (head, position))
            
            self.features.add('Dist_ancestor_norm_Unit1=%s@%d' % (dist_ancestor_l/float(len(common_ancestor_pos)), position))
                
        if dist_ancestor_r:
            head = filter_lexical_head(t.get_head(r_ancestor_pos))
            self.features.add('Top_lexical_head_Unit2=%s@%d' % (head, position))
            
            self.features.add('Dist_ancestor_norm_Unit2=%s@%d' % (dist_ancestor_l/float(len(common_ancestor_pos)), position))
    
        if common_ancestor_pos:
            syntax_tree = t
            head_pos = syntax_tree[common_ancestor_pos].head
            
            if head_pos >= l_end_word:
                self.features.add('Head_in_R@%d' % position)
            else:
                self.features.add('Head_in_L@%d' % position)
     
            if dist_ancestor_l == 0 or dist_ancestor_r == 0: 
                if dist_ancestor_l == 0:# L >> R
                   
                    self.features.add('L_Dominates_R@%d' % position)
                    dom_pos = r_ancestor_pos[:-1]
                else: # R >> L
                    
                    self.features.add('R_Dominates_L@%d' % position)
                    dom_pos = l_ancestor_pos[:-1]
    
                head = filter_lexical_head(syntax_tree.get_head(dom_pos))
#                if head and head in self.lexical_heads:
                if head:
                    self.features.add('Dominated_lexical_head=%s@%d' % (head, position))
    
                tag = filter_syntactic_tag(syntax_tree.get_syntactic_tag(dom_pos))
                if tag :
                    self.features.add('Dominated_Syntactic_tag=%s@%d' % (tag, position))
    
    
    def write_substructure_features(self, constituent, unit = 1, position = 0):
        self.features.add("Unit%d_Subtree_Rel_Root=%s@%d" % (unit, constituent.get_subtree_rel(), position))


    def write_text_structureal_features(self, constituent, unit, position):
        '''
        Number of sentences in unit 1 (or unit 2).
        '''
        
        start_sent = constituent.start_sent_id
        
        end_sent = constituent.end_sent_id
        
        
        if start_sent == 0:
            self.features.add('First_Sentence_Unit%d@%d' % (unit, position))
            
        if end_sent == len(constituent.doc.sentences) - 1:
            self.features.add('Last_Sentence_Unit%d@%d' % (unit, position))
            
        num_sents = end_sent - start_sent + 1

        num_paragraphs = 0
        for i in range(constituent.l_start, constituent.r_end):
#            print constituent.doc.edus[i]
            if constituent.doc.edus[i][-1] == '<P>':
                num_paragraphs += 1
        
        return num_sents, num_paragraphs

    def write_cue_phrase_features(self, constituent, unit = 1, position = 0):
        if not constituent.is_leaf():
            edus = [constituent.doc.edus[constituent.l_start], constituent.doc.edus[constituent.r_end - 1]]
        else:
            edus = [constituent.doc.edus[constituent.l_start]]
        
        candidates = []
        for edu in edus:
            candidates.append(' ' + ' '.join(edu).lower().replace('<s>', '').replace('<p>', '') + ' ')
                          
        for cue_phrase in self.cue_phrases:
            for (i, cand_span) in enumerate(candidates):
                cue_position = 'Beginning' if i == 0 else 'Ending'
                pos = cand_span.find(" " + cue_phrase + " ")
                if pos >= 0:
                    if i == 0 and pos < 3:
                        self.features.add('Unit%d_%s_Cue_Phrase=%s@%d' % (unit, cue_position, cue_phrase.replace(' ', '#'), position))
                    elif i == 1 and cand_span[pos : ].split(' ') <= 3:
                        self.features.add('Unit%d_%s_Cue_Phrase=%s@%d' % (unit, cue_position, cue_phrase.replace(' ', '#'), position))
                              
                              
 
    def write_features_for_constituents(self, constituents, positions, scope, labeling):
        self.features.clear()
 
        for (i, position) in enumerate(positions):
            L = constituents[i]
            R = constituents[i + 1]
            
            if L and R:
#                 print 'c1:', constituent1.print_span(), 'c2:', constituent2.print_span()
                l_subtree_height, l_num_edus = self.write_organization_features(L, scope, 1, position)
                r_subtree_height, r_num_edus = self.write_organization_features(R, scope, 2, position)
                
                if l_subtree_height < r_subtree_height:
                    self.features.add('L_Lower_Subtree_Height_Than_R@%d' % position)
                elif r_subtree_height < l_subtree_height:
                    self.features.add('R_Lower_Subtree_Height_Than_L@%d' % position)
                else:
                    self.features.add('L_R_Same_Subtree_Height@%d' % position)
                
                if l_num_edus < r_num_edus:
                    self.features.add('L_Fewer_EDUs_Than_R@%d' % position)
                elif r_num_edus < l_num_edus:
                    self.features.add('R_Fewer_EDUs_Than_L@%d' % position)
                else:
                    self.features.add('L_R_Same_Subtree_Height@%d' % position)
                    
                
                self.write_Ngram_features(L, 1, position)
                self.write_Ngram_features(R, 2, position)
                
                self.write_dominance_set_features(L, R, position)
                
                if not scope:
                    l_num_sents, l_num_paragraphs = self.write_text_structureal_features(L, 1, position)
                    r_num_sents, r_num_paragraphs = self.write_text_structureal_features(R, 2, position)
                    
                    if l_num_sents < r_num_sents:
                        self.features.add('L_Fewer_Num_Sentences_Than_R@%d' % position)
                    elif r_num_sents < l_num_sents:
                        self.features.add('R_Fewer_Num_Sentences_Than_L@%d' % position)
                    else:
                        self.features.add('L_R_Same_Num_Sentences@%d' % position)
                    
                    if l_num_paragraphs < r_num_paragraphs:
                        self.features.add('L_Fewer_Num_Paragraphs_Than_R@%d' % position)
                    elif r_num_paragraphs < l_num_paragraphs:
                        self.features.add('R_Fewer_Num_Paragraphs_Than_L@%d' % position)
                    else:
                        self.features.add('L_R_Same_Num_Paragraphs@%d' % position)
                    
                self.write_substructure_features(L, 1, position)
                self.write_substructure_features(R, 2, position)
                                   
                self.write_cue_phrase_features(L, 1, position)
                self.write_cue_phrase_features(R, 2, position)
                
                l_num_tokens = L.get_num_tokens()
                r_num_tokens = R.get_num_tokens()
                
                if l_num_tokens * 1.5 < r_num_tokens:
                    self.features.add('L_Fewer_Num_Tokens_Than_R@%d' % position)
                elif r_num_tokens * 1.5 < l_num_tokens:
                    self.features.add('R_Fewer_Num_Tokens_Than_L@%d' % position)
                else:
                    self.features.add('L_R_Same_Num_Tokens@%d' % position)
                
                if scope:
                    assert L.start_sent_id == L.end_sent_id
                    sent_num_edus = L.doc.sentences[L.start_sent_id].end_edu - L.doc.sentences[L.start_sent_id].start_edu
                    
                    if (L.get_num_edus() + R.get_num_edus()) == sent_num_edus:
                        self.features.add('Last_Pair@%d' % position)
                else:
                    if (L.get_num_edus() + R.get_num_edus()) == len(L.doc.edus):
                        self.features.add('Last_Pair@%d' % position)

        return self.features