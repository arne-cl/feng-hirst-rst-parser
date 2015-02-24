'''
Created on 2013-02-18

@author: Vanessa Wei Feng
'''
import sys
import os
import string
import time
import cPickle
import paths

save_suffix = ".dat"

def saveData(filename, myobject, where = paths.save_folder, suffix = save_suffix):
    fo = open(where + filename + suffix, "wb")
    cPickle.dump(myobject, fo, protocol = cPickle.HIGHEST_PROTOCOL)
    fo.close()

def loadData(filename, where = paths.save_folder, suffix = save_suffix):
    data_file = where + filename + suffix
    try:
        fo = open(data_file, "rb")
    except IOError:
        print "Couldn't open data file: %s" % data_file
        return
    try:
        myobject = cPickle.load(fo)
    except:
        fo.close()
        print "Unexpected error:", sys.exc_info()[0]
        raise
    fo.close()
    return myobject
