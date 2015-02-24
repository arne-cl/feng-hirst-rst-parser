from trees.lexicalized_tree import LexicalizedTree
import re

def replace_words(text, word_dic):
    """
    take a text and <strong class="highlight">replace</strong> <strong class="highlight">words</strong> that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, word_dic)))
    def translate(match):
        return word_dic[match.group(0)]
    return rc.sub(translate, text)

def get_parsed_trees_from_string(tree_strings):
    # tree_strings separated by "\n"
    parsed_trees = []
    for line in tree_strings:
        line = line.strip()
        #print line
        if line != '':
            parsed_trees.append(LexicalizedTree.parse(line, leaf_pattern = '(?<=\\s)[^\)\(]+'))
   
    return parsed_trees


def create_lexicalized_tree(unlexicalized_tree, heads):
    """
    Creates a lexicalized syntax tree given a MRG-style parse and a Penn2Malt style heads file. 
    """
    t = unlexicalized_tree.copy(True)    
    t.lexicalize(heads)
        
    return t