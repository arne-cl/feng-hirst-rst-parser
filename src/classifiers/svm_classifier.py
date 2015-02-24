'''
Created on 2013-02-17

@author: Vanessa Wei Feng
'''

import subprocess

import paths
import random
import os

class SVMClassifier:
                 
    def __init__(self, class_type = 'bin', 
                 model_path = paths.MODEL_PATH, 
                 bin_model_file = None,
                 bin_scale_model_file = None,
                 mc_model_file = None,
                 mc_scale_model_file = None,
                 software = 'svm-light',
                 output_filter = None, 
                 name = 'default',
                 verbose = False):
        self.verbose = verbose
        self.name = name
        self.class_type = class_type
        
        self.output_filter = output_filter or (lambda x: x)
        
        self.svm_classifier_cmd = None
        self.svm_classifier = None
        self.svm_scale_cmd = None
        
        self.tmp_test_fname = None
        self.tmp_predictions_fname = None
        
        if class_type == 'bin':
            if bin_scale_model_file:
                self.svm_scale_cmd = '%s/svm-scale -r %s' % (paths.SVM_TOOLS, model_path + bin_scale_model_file)
                
            if software == 'libsvm':
                #self.svm_classifier_cmd = 'java -cp "%s" %s %s' % (paths.SVM_TOOLS + 'libsvm', 'svm_predict_stdin', model_path + bin_model_file)
                self.svm_classifier_cmd = paths.SVM_TOOLS + 'libsvm/svm-predict-stdin ' + model_path + bin_model_file
            elif software == 'liblinear':
                self.svm_classifier_cmd = paths.SVM_TOOLS + 'liblinear/predict_stdin -b 1 ' + model_path + bin_model_file
            else:
                self.svm_classifier_cmd = paths.SVM_TOOLS + 'svm_perf_classify ' + model_path + bin_model_file
                
#                signature = 'bin_' + str(random.getrandbits(64))
#                self.tmp_test_fname = paths.MODEL_PATH + 'tmp_test_' + signature
#                self.tmp_predictions_fname = paths.MODEL_PATH + 'tmp_predictions_' + signature
#            
#                self.bin_model_file = model_path + bin_model_file
        else:
            if mc_scale_model_file:
                self.svm_scale_cmd = '%s/svm-scale -r %s' % (paths.SVM_TOOLS, model_path + mc_scale_model_file)
                
            if software == 'libsvm':
                self.svm_classifier_cmd = paths.SVM_TOOLS + 'libsvm/svm-predict-stdin -b 1 ' + model_path + mc_model_file
            else:
#                signature = 'mc_' + str(random.getrandbits(64))
#                self.tmp_test_fname = paths.MODEL_PATH + 'tmp_test_' + signature
#                self.tmp_predictions_fname = paths.MODEL_PATH + 'tmp_predictions_' + signature
#            
#                self.mc_model_file = model_path + mc_model_file
                
                self.svm_classifier_cmd = paths.SVM_TOOLS + 'svm_multiclass_classify ' + model_path + mc_model_file

        #print self.svm_scale_cmd
        if self.svm_scale_cmd:
            self.svm_scale = subprocess.Popen(self.svm_scale_cmd, shell=True,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)

            if self.verbose:
                print "Loading scale utility... (%s): %s" % (class_type, self.svm_scale_cmd)
            self.svm_scale.stdout.readline() # Wait for initialization
        else:
            self.svm_scale = None

        if self.svm_classifier_cmd:
            #print self.svm_classifier_cmd
            self.svm_classifier = subprocess.Popen(self.svm_classifier_cmd, shell=True,
                                          stdin=subprocess.PIPE, stdout=subprocess.PIPE)

            if self.verbose:
                print "Loading classifier model... (%s): %s" % (class_type, self.svm_classifier_cmd)
    
            self.svm_classifier.stdout.readline() # Wait for initialization
            #print init # uncomment if you want to see failure/success
            
            if self.verbose:
                print "Finished loading" 
            
            if self.svm_scale and self.svm_scale.poll():
                raise OSError('Could not create svm_scale subprocess')
            if self.svm_classifier and self.svm_classifier.poll():
                raise OSError('Could not create svm_classifier subprocess')
    
    
    def classify(self, vector, model_file = None):
        if self.svm_classifier:
            if self.svm_scale:
                self.svm_scale.stdin.write(vector.strip() + "\n")
                scaled_vector = self.svm_scale.stdout.readline()
            else:
                scaled_vector = vector
        
            self.svm_classifier.stdin.write(scaled_vector.strip() + "\n")
            #self.svm_classifier.stdin.write(vector.strip() + "\n")
            result = self.svm_classifier.stdout.readline()
            #print 'result', result
            #result = self.svm_classifier.communicate(scaled_vector.strip() + "\n")
    
            if self.svm_scale and self.svm_scale.poll():
                #print vector.strip()
                #print scaled_vector
                raise OSError('svm_scale subprocess died')
            if self.svm_classifier.poll():
                #print result
                raise OSError('svm_classifier subprocess died')
        else:
            fout = open(self.tmp_test_fname, 'w')
            #fout.write(scaled_vector)
            fout.write(' '.join(vector.strip().split('\t')) + '\n')
            fout.flush()
            fout.close()
            
            svm_software = 'svm_multiclass_classify' if self.class_type == 'mc' else 'svm_perf_classify'
            if model_file is None:
                model_file = self.mc_model_file if self.class_type == 'mc' else self.bin_model_file
            svm_classifier_cmd = '%s/%s %s %s %s' % (paths.SVM_TOOLS,
                                                     svm_software,
                                                     self.tmp_test_fname,
                                                     model_file,
                                                     self.tmp_predictions_fname)
            #print svm_classifier_cmd
            p = subprocess.Popen(svm_classifier_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            p.stdout.readlines()
            p.wait()
            
            result = open(self.tmp_predictions_fname).readline()
            
            
        return self.output_filter(result.strip())
    
    def classify_all(self, vectors, model_file = None):
        fout = open(self.tmp_test_fname, 'w')
        #fout.write(scaled_vector)
        fout.write('\n'.join(vectors) + '\n')
        fout.flush()
        fout.close()
        
        svm_software = 'svm_multiclass_classify' if self.class_type == 'mc' else 'svm_perf_classify'
        if model_file is None:
            model_file = self.mc_model_file if self.class_type == 'mc' else self.bin_model_file
        svm_classifier_cmd = '%s/%s %s %s %s' % (paths.SVM_TOOLS,
                                                 svm_software,
                                                 self.tmp_test_fname,
                                                 model_file,
                                                 self.tmp_predictions_fname)
        #print svm_classifier_cmd
        p = subprocess.Popen(svm_classifier_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        p.stdout.readlines()
        p.wait()
        
        results = []
        fin = open(self.tmp_predictions_fname)
        for line in fin:
            results.append(self.output_filter(line.strip()))
        fin.close()
            
            
        return results
    
    
    def poll(self):
        """
        Checks that the classifier processes are still alive
        """
        if self.svm_scale is None or self.svm_classifier is None:
            return True
        else:
            return self.svm_scale.poll() != None or self.svm_classifier.poll() != None
        
    
    def unload(self):
        if self.verbose:
        #if True:
            print "Unloading classifier (%s)" % self.name
        
        if self.svm_scale:
            self.svm_scale.stdin.write("\n\n")
        
        if self.svm_classifier:
            self.svm_classifier.stdin.write("\n\n")

        if self.tmp_test_fname:
            os.remove(self.tmp_test_fname)
        
        if self.tmp_predictions_fname:
            os.remove(self.tmp_predictions_fname)
