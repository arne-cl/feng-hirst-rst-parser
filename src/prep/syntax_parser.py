'''
Created on 2013-02-17

@author: Vanessa Wei Feng
'''

import subprocess

import paths
from utils.utils import get_heads
import re

class SyntaxParser:
    
    def __init__(self, path = paths.STANFORD_PATH, verbose = False, dependencies = False):
        
        self.path = path
        self.verbose = verbose
        self.dependencies = dependencies
        
        # -mx150m
        cmd = ""
        if not self.dependencies:
            cmd = "java -mx1500m -cp \"%s/stanford-parser.jar\" edu.stanford.nlp.parser.lexparser.LexicalizedParser -retainTMPSubcategories -outputFormat \"penn\" \"%s/englishPCFG.ser.gz\" -" % (self.path, self.path)
        else:
            #cmd = "java -mx1500m -cp \"%s/stanford-parser.jar\" edu.stanford.nlp.parser.lexparser.LexicalizedParser -retainTMPSubcategories -outputFormat \"wordsAndTags, penn, typedDependencies\" \"%s/englishPCFG.ser.gz\" -" % (self.path, self.path)
            cmd = "java -mx1500m -cp \"%s/stanford-parser.jar\" edu.stanford.nlp.parser.lexparser.LexicalizedParser -retainTMPSubcategories -outputFormat \"penn, typedDependencies\" \"%s/englishPCFG.ser.gz\" -" % (self.path, self.path)
            #cmd = "java -mx1500m -cp \"%s/*\"  edu.stanford.nlp.parser.lexparser.LexicalizedParser -sentences newline -retainTMPSubcategories -outputFormat \"penn, typedDependencies\" englishPCFG.ser.gz -" % (self.path)


        #print cmd
        self.syntax_parser = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    
        init = self.syntax_parser.stderr.readline()
        init = init + self.syntax_parser.stderr.readline()
        
        if self.verbose:
            print "Syntax parser loaded"
            print init
            
        if self.syntax_parser.poll():
            raise OSError('Could not create a syntax parser subprocess')

    
    
    def parse(self, l, outfname = None):
        """
        Parses a list of sentences, returns a list of (syntax tree, heads)
        """
        
        if not self.dependencies:
            parses = map(lambda x: self.parse_sentence(x), l)
            return (parses, get_heads("\n".join(parses), outfname), None)
        else:
            #words_tags_parses = []
            penn_parses = []
            dep_parses = []
            for sent in l:
                #(words_tags, penn_parse, dep_parse) = self.parse_sentence(sent)
                (penn_parse, dep_parse) = self.parse_sentence(sent)
                #words_tags_parses.append(words_tags)
                penn_parses.append(penn_parse)
                dep_parses.append(dep_parse)
            #return (words_tags_parses, penn_parses, get_heads("\n".join(penn_parses), outfname), dep_parses)
            return (penn_parses, get_heads("\n".join(penn_parses), outfname), dep_parses)
    
    
    def parse_sentence(self, s):
        """
        Parses a sentence s
        """
        #print "%s\n" % s.strip()
        self.syntax_parser.stdin.write("%s\n" % s.strip())
        self.syntax_parser.stdin.flush()
        
        # Read stderr anyway to avoid problems
        err = self.syntax_parser.stderr.readline()

        if self.verbose:
            print err
        
        result = ""
        cur_line = "debut"

        #need_to_fix = False
        #finished_tags = False
        finished_penn_parse = False
        penn_parse_result = ""
        dep_parse_results = []
        #words_tags = ""
        while cur_line != "":
            #cur_line = self.syntax_parser.stdout.readline().strip()
            cur_line = self.syntax_parser.stdout.readline()
            # Check for errors
            if cur_line.strip() == "SENTENCE_SKIPPED_OR_UNPARSABLE":
                raise Exception("Syntactic parsing of the following sentence failed:" + s + "--")
            
            #print cur_line
            #print finished_penn_parse
            if cur_line.strip() == '':
                if not self.dependencies:
                    break
                #if not finished_tags:
                    #finished_tags = True
                #elif not finished_penn_parse:
                if not finished_penn_parse:
                    finished_penn_parse = True
                else: break
            else:
                #if not finished_tags:
                    #words_tags = words_tags + cur_line.strip()
                if finished_penn_parse:
                    dep_parse_results.append(cur_line.strip())
                else:
                    penn_parse_result = penn_parse_result + cur_line.strip()
            '''result = result + cur_line.strip()'''
        
        #print penn_parse_result
        if self.dependencies:
            #return (words_tags, penn_parse_result, '\n'.join(dep_parse_results))
            return (penn_parse_result, '\n'.join(dep_parse_results))
        else:
            return penn_parse_result
    
    
    def poll(self):
        """
        Checks that the parser process is still alive
        """
        if self.syntax_parser is None:
            return True
        else:
            return self.syntax_parser.poll() != None
        
        
    def unload(self):
        if not self.syntax_parser.poll():
            if self.verbose:
                print "Unloading syntax parser."
            #self.syntax_parser.kill() # Only in Python 2.6+
            self.syntax_parser.stdin.close()
            self.syntax_parser.stdout.close()
            self.syntax_parser.stderr.close()