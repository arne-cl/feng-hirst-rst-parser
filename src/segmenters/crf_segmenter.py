'''
Created on 2014-01-11

@author: Wei
'''
from features.segmenter_feature_writer import SegmenterFeatureWriter
from classifiers.crf_classifier import CRFClassifier
import paths
import utils.utils
from document.token import Token

class CRFSegmenter:
    def __init__(self, _name = 'crf_segmenter', verbose = False, global_features = False):
        self.name = _name
        self.verbose = verbose
        
        self.feature_writer = SegmenterFeatureWriter()
        
        self.global_features = global_features
        
        self.add_classifiers()
    
    def add_classifiers(self):
        self.classifiers = []
        
        classifier1 = CRFClassifier(name= self.name,
                                          model_type = 'segmenter',
                                          model_path = paths.SEGMENTER_MODEL_PATH,
                                          model_file = 'seg.crfsuite',
                                          verbose = self.verbose)
        self.add_classifier(classifier1, 'classifier1')
           
        if self.global_features:
            classifier2 = CRFClassifier(name= self.name + "_global_features",
                                              model_type = 'segmenter',
                                              model_path = paths.SEGMENTER_MODEL_PATH,
                                              model_file = 'seg_global_features.crfsuite',
                                              verbose = self.verbose)
        
        
        
            self.add_classifier(classifier2, 'classifier2')
        
        
#        classifier1 = MalletCRFClassifier(name= self.name,
#                                          model_type = 'segmenter',
#                                          model_path = paths.CRF_SEGMENTER_MODEL_PATH,
#                                          model_file = 'seg.mallet',
#                                          verbose = self.verbose)
#        self.add_classifier(classifier1, 'classifier1')
#           
#        if self.global_features:
#            classifier2 = MalletCRFClassifier(name= self.name + "_global_features",
#                                              model_type = 'segmenter',
#                                              model_path = paths.CRF_SEGMENTER_MODEL_PATH,
#                                              model_file = 'seg_global_features.mallet',
#                                              verbose = self.verbose)
#        
#        
#        
#            self.add_classifier(classifier2, 'classifier2')
#        


    def add_classifier(self, classifier, name):
        if name == 'classifier1':
            self.classifier = classifier
        elif name == 'classifier2':
            self.global_features_classifier = classifier
        else:
            raise Exception('Unknown classifier name', name)
        
        print 'Added classifier', name, 'to segmenter', self.name
        
        self.classifiers.append(classifier)
    
    
    def unload(self):
        for classifier in self.classifiers:
            classifier.unload()
        
    def write_features(self, sentence, input_edu_segmentation = None):
        features = []
        #print sentence.sent_id
#        edu_segmentation = sentence.doc.edu_word_segmentation[sentence.sent_id]
#        print edu_segmentation
            
        for i in range(len(sentence.tokens) - 1):
            token0 = None if i == 0 else sentence.tokens[i - 1]
            token1 = sentence.tokens[i]
            token2 = sentence.tokens[i + 1]
            token3 = None if i == len(sentence.tokens) - 2 else sentence.tokens[i + 2]
            
            edu_segmentation = input_edu_segmentation
#            print edu_segmentation
            
            inst_features = self.feature_writer.write_features([token0, token1, token2, token3], edu_segmentation) 
            feature_str = '\t'.join(list(inst_features))
#            print feature_str
            features.append('0\t%s' % feature_str)
            
#            feature_str = ' '.join(list(inst_features))
##            print feature_str
#            features.append('%s 0' % feature_str)
        
        return features
    
    def find_neighbouring_boundary(self, token_id, edu_segmentation, direction = 'L'):
        if direction == 'R':
            for j in range(len(edu_segmentation)):
#                print edu_segmentation[j]
                if edu_segmentation[j][1] > token_id:
                    return edu_segmentation[j][1]
                
        else:
            for j in range(len(edu_segmentation) - 1, -1, -1):
#                print edu_segmentation[j]
                if edu_segmentation[j][0] < token_id - 1:
                    return edu_segmentation[j][0]
                
    def segment_sentence(self, sentence, input_edu_segmentation = None):
        if len(sentence.tokens) == 1:
            edus = [[sentence.tokens[0].word, sentence.raw_text[-3 : ]]]
            
            sentence.doc.cuts.append((len(sentence.doc.edus), len(sentence.doc.edus) + len(edus)))
            sentence.start_edu = len(sentence.doc.edus)
            sentence.end_edu = len(sentence.doc.edus) + len(edus)
            sentence.doc.edu_word_segmentation.append([(0, 1)])
            sentence.doc.edus.extend(edus)
            return
        
#        print sentence.raw_text
        
        self.feature_writer.cached_subtrees = {}
        
        if input_edu_segmentation:
#            print input_edu_segmentation
            
            offset2neighbouring_boundaries = {}
            for (j, (start_word, end_word)) in enumerate(input_edu_segmentation):
                for offset in range(start_word, end_word):
                    if offset == start_word:
                        l_boundary = input_edu_segmentation[j - 1][0] if j > 0 else None
                    else:
                        l_boundary = start_word
                    
                    if offset == end_word - 1:
                        r_boundary = input_edu_segmentation[j + 1][1] if (j < len(input_edu_segmentation) - 1) else None
                    else:
                        r_boundary = end_word
                        
#                    l_boundary1 = self.find_neighbouring_boundary(offset + 1, input_edu_segmentation, 'L')
#                    r_boundary1 = self.find_neighbouring_boundary(offset + 1, input_edu_segmentation, 'R')
##                    
##                    print offset, l_boundary, r_boundary, l_boundary1, r_boundary1
#                    assert l_boundary1 == l_boundary and r_boundary1 == r_boundary
                    offset2neighbouring_boundaries[offset] = (l_boundary, r_boundary)
#            
#            for offset in offset2neighbouring_boundaries:
#                print 'sentence', j, offset, offset2neighbouring_boundaries[offset]
        else:
            offset2neighbouring_boundaries = None
             
        features = self.write_features(sentence, offset2neighbouring_boundaries)
        
#        print sentence.raw_text
#        print len(features)
#        for feat in features:
#            print feat
#        print 
        
        if input_edu_segmentation:
            seq_prob, predictions = self.global_features_classifier.classify(features)
        else:
            seq_prob, predictions = self.classifier.classify(features)
            
        edus = []
        edu_word_segmentations = []
        start = 0
        for i in range(len(predictions)):
            pred = int(predictions[i][0])
            if pred == 1:
#                print i, pred
                edu_word_segmentations.append((start, i + 1))
                start = i + 1
        
        edu_word_segmentations.append((start, len(sentence.tokens)))
        
        for (start_word, end_word) in edu_word_segmentations:
            edu = []
            for j in range(start_word, end_word):
                edu.extend(utils.utils.unescape_penn_special_word(sentence.tokens[j].word).split(' '))
            
            if end_word == len(sentence.tokens):
#                print sentence.raw_text
                edu.append(sentence.raw_text[-3 : ])
            edus.append(edu)
        
        sentence.doc.cuts.append((len(sentence.doc.edus), len(sentence.doc.edus) + len(edus)))
        sentence.start_edu = len(sentence.doc.edus)
        sentence.end_edu = len(sentence.doc.edus) + len(edus)
        sentence.doc.edu_word_segmentation.append(edu_word_segmentations)
        sentence.doc.edus.extend(edus)
        
#        print sentence.doc.edu_word_segmentation[-1]
                
    def segment_permutation(self, doc, canonical_doc):
        assert len(doc.sentences) == len(canonical_doc.sentences)
        
        doc.edu_word_segmentation = []
        doc.cuts = []
        doc.edus = []
        
        sentence_order = []
        for sent in doc.sentences:
            index = 0
#            print sent.sent_id, sent.raw_text
            while index < len(canonical_doc.sentences):
#                print 'canonical', index, canonical_doc.sentences[index].raw_text
                if canonical_doc.sentences[index].raw_text == sent.raw_text and index not in sentence_order:
#                    print index
#                    print canonical_doc.sentences[index].raw_text
#                    print sent.raw_text
#                    print
                    break
                 
                index += 1
                
#            if index == len(canonical_doc.sentences):
#                print sent.sent_id, sent.raw_text
#                print canonical_doc.sentences[index - 1].raw_text
#                print
                   
#            print
#            print sent.sent_id, index
            sentence_order.append(index)
        
#        print sentence_order
#        print sorted(sentence_order)
        assert sorted(sentence_order) == range(len(doc.sentences))
        
        for (i, index) in enumerate(sentence_order):
            sentence = doc.sentences[i]
            sentence.set_unlexicalized_tree(canonical_doc.sentences[index].unlexicalized_parse_tree)
            sentence.set_lexicalized_tree(canonical_doc.sentences[index].parse_tree)
            
            sentence.tokens = []
            
            for te in canonical_doc.sentences[index].tokens:
                token = Token(te.word, te.id, sentence)
                token.lemma = te.lemma
                sentence.add_token(token)
                
#            print i
#            print sentence.raw_text
#            print canonical_doc.sentences[index].raw_text
#            print
            
            (canonical_start_edu, canonical_end_edu) = canonical_doc.cuts[index]
            
            edus = canonical_doc.edus[canonical_start_edu : canonical_end_edu]
            sentence.start_edu = len(sentence.doc.edus)
            sentence.end_edu = len(sentence.doc.edus) + len(edus)
            doc.cuts.append((len(sentence.doc.edus), len(sentence.doc.edus) + len(edus)))
            doc.edus.extend(edus)
            doc.edu_word_segmentation.append(canonical_doc.edu_word_segmentation[index])
            
        doc.start_edu = 0
        doc.end_edu = len(doc.edus)
        
    def segment(self, doc):
        doc.edu_word_segmentation = []
        doc.cuts = []
        doc.edus = []
        
        for sentence in doc.sentences:
            self.segment_sentence(sentence)
        
        if self.global_features:
            init_edu_word_segmentation = doc.edu_word_segmentation
#            print init_edu_word_segmentation
            
            doc.edu_word_segmentation = []
            doc.cuts = []
            doc.edus = []
            
            for sentence in doc.sentences:
                self.segment_sentence(sentence, input_edu_segmentation = init_edu_word_segmentation[sentence.sent_id])
                
#                if init_edu_word_segmentation[sentence.sent_id] != doc.edu_word_segmentation[sentence.sent_id]:
#                    print sentence.sent_id
#                    print 'initial segmentation', init_edu_word_segmentation[sentence.sent_id]
#                    print 'new segmentation', doc.edu_word_segmentation[sentence.sent_id]
#                    print
            
        
        doc.start_edu = 0
        doc.end_edu = len(doc.edus) 