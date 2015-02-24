
from trees.parse_tree import ParseTree
import paths

from parsers.intra_sentential_parser import IntraSententialParser
from parsers.multi_sentential_parser import MultiSententialParser
from features.tree_feature_writer import CRFTreeFeatureWriter

from classifiers.crf_classifier import CRFClassifier

class CRFTreeBuilder:
    def __init__(self, _name = "gCRF", verbose = False):
        self.name = _name
        self.verbose = verbose
        self.window_size = 3
        
        self.intra_parser = IntraSententialParser(verbose = self.verbose, window_size = self.window_size)
        self.multi_parser = MultiSententialParser(verbose = self.verbose, window_size = self.window_size)
        
        self.add_feature_writer()
        
        self.add_classifiers()
    
    
    def add_classifiers(self):
        self.classifiers = []
        
        bin_classifier1 = CRFClassifier(name= self.name + "_intra_bin",
                                        model_type = 'treebuilder',
                                        model_path = paths.TREE_BUILD_MODEL_PATH,
                                        model_file = 'struct/intra.crfsuite',
                                        verbose = self.verbose)
            
        bin_classifier2 = CRFClassifier(name= self.name + "_multi_bin",
                                        model_type = 'treebuilder',
                                        model_path = paths.TREE_BUILD_MODEL_PATH,
                                        model_file = 'struct/multi.crfsuite',
                                        verbose = self.verbose)
        
        mc_classifier1 = CRFClassifier(name= self.name + "_intra_mc",
                                       model_type = 'treebuilder',
                                       model_path = paths.TREE_BUILD_MODEL_PATH,
                                       model_file = 'label/intra.crfsuite',
                                       verbose = self.verbose)
        
        mc_classifier2 = CRFClassifier(name= self.name + "_multi_mc",
                                       model_type = 'treebuilder',
                                       model_path = paths.TREE_BUILD_MODEL_PATH,
                                       model_file = 'label/multi.crfsuite',
                                       verbose = self.verbose)
        
        self.add_classifier(bin_classifier1, 'bin1')
        self.add_classifier(mc_classifier1, 'mc1')
        self.add_classifier(bin_classifier2, 'bin2')
        self.add_classifier(mc_classifier2, 'mc2')
        

    def add_classifier(self, classifier, name):
        if name == 'bin1':
            self.intra_parser.bin_classifier = classifier
        elif name == 'bin2':
            self.multi_parser.bin_classifier = classifier
        elif name == 'mc1':
            self.intra_parser.mc_classifier = classifier
        elif name == 'mc2':
            self.multi_parser.mc_classifier = classifier
        else:
            raise Exception('Unknown classifier name', name)
        
        print 'Added classifier', name, 'to treebuilder', self.name
        
        self.classifiers.append(classifier)
        
        
    def add_feature_writer(self):
        feature_writer = CRFTreeFeatureWriter(self.verbose)
        
        self.intra_parser.feature_writer = feature_writer
        self.multi_parser.feature_writer = feature_writer
        
        print 'Added feature writer to treebuilder'
        
        
    def build_tree(self, doc):
#        print self.use_contextual_features 
        # Check if only one EDU
        if len(doc.edus) == 1:
            return [ParseTree("n/a", [doc.edus[0]])]
        
        for i in range(len(doc.sentences)):
            sentence = doc.sentences[i]
            (start_edu, end_edu) = doc.cuts[i]
            
            if self.verbose:
                print 'sentence %d' % i
                print 'start_edu', start_edu, 'end_edu', end_edu
            
            self.intra_parser.parse_each_sentence(sentence)

        self.multi_parser.parse_document(doc)
    
        return doc.discourse_tree

    
    def unload(self):
        self.intra_parser.unload()
        self.multi_parser.unload()
        
        for classifier in self.classifiers:
            classifier.unload()