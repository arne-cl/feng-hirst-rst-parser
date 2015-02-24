
import sys
import cPickle
import paths
import os.path

save_suffix = ".dat"

def saveData(filename, myobject, where = paths.save_folder, suffix = save_suffix):
    fo = open(os.path.join(where, filename + suffix), "wb")
    #print 'Saved serialized file to %s' % os.path.join(where, filename + suffix)
    cPickle.dump(myobject, fo, protocol = cPickle.HIGHEST_PROTOCOL)
    fo.close()

def loadData(filename, where = paths.save_folder, suffix = save_suffix):
    data_file = os.path.join(where, filename + suffix)
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
