'''
Created on 2014-01-17

@author: Wei
'''
class LogWriter:
    def __init__(self, writer):
        self.writer = writer
    
    def write(self, text):
        if self.writer:
            self.writer.write(text + '\n')
            
    def close(self):
        if self.writer:
            self.writer.flush()
            self.writer.close()