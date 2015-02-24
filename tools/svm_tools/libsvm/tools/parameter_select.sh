#!/bin/sh

# parameter_select.sh
# 
#
# Created by Boulot on 10/5/09.
# Copyright 2009 The University of Tokyo. All rights reserved.

python subset.py /Users/boulot/Documents/workspace/Alpha/features/libsvm/seg_training_penn.txt 5000 > training_sub

python easy.py training_sub /Users/boulot/Documents/workspace/Alpha/features/libsvm/seg_test_penn.txt
