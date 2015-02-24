'''
Created on 2013-02-17

@author: Vanessa Wei Feng
'''
import re
import os.path
import sys

ROOT_PATH = '/'.join(os.path.split(os.getcwd())[ : -1])

#if getattr(sys, 'frozen', None):
#  ROOT_PATH = sys._MEIPASS
#else:
#  ROOT_PATH = os.path.dirname(__file__)

STANFORD_PATH = os.path.join(ROOT_PATH, 'tools/stanford_parser/')
PENN2MALT_PATH = os.path.join(ROOT_PATH, 'tools/Penn2Malt/')
SVM_TOOLS = os.path.join(ROOT_PATH, 'tools/svm_tools/')

MODEL_PATH = os.path.join(ROOT_PATH, 'model/')
SEG_MODEL_PATH = os.path.join(ROOT_PATH, 'model/seg_set/')
TREE_BUILD_MODEL_PATH = os.path.join(ROOT_PATH, 'model/tree_build_set/')

save_folder = os.path.join(MODEL_PATH, 'serial_data/')