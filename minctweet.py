#!/usr/bin/python

"""
A simple program that will monitor a Minecraft server and tweet interesting
happenings.
"""

import csv
import sys 
import os
import os.path
import subprocess
import time

class FileMonitor(object):
    """
    Only lines added AFTER monitoring was initiated will be read.
    """
    
    def __init__( self, fpath ):
        #
        # Prep
        self.fpath = fpath
        
        #
        # Open monitoring via tail
        cmd = "tail -f -n0 %s" % fpath
        tailproc = subprocess.Popen( cmd, shell=True,
                        stdout=subprocess.PIPE )
        proc_stdout = tailproc.stdout
        
        self.tailproc = tailproc
        self.proc_stdout = proc_stdout
        
        #
        # Burn the first line
        #self.nextline()
    
    def nextline( self ):
        """
        Newline symbol is discarded.
        """
        self.tailproc.poll()
        if self.tailproc.returncode is not None:
            raise RuntimeError( "tail subprocess quit unexpectedly" )
        
        ln = self.proc_stdout.readline()     # if no more lines, this will wait
        ln = ln.rstrip( '\n' )
        return ln

def main():
    #
    # Load config
    if len(sys.argv) <= 1:
        print "Too few arguments: path to config file missing"
        exit()
    
    if len(sys.argv) >= 3:
        print "Too many arguments: only specify config file path"
        exit()
    
    config_fpath = sys.argv[1]
    
    if not os.path.exists( config_fpath ):
        print "%s: file does not exist" % (config_fpath)
    
    if not os.path.isfile( config_fpath ):
        print "%s: is not a file" % (config_fpath)
    
    config_dict = {}
    fin = open( config_fpath, 'r' )
    rdr = csv.reader( fin, delimiter='=' )
    for row in rdr:
        print row
        (field,val) = row
        config_dict[field] = val
    fin.close()
    
    #
    # Hook into log file
    mclog_fpath = config_dict['log']
    logmon = FileMonitor( mclog_fpath )

    while True:
        ln = logmon.nextline()
        print ln
        #Log monitoring quit unexpectedly
        
if __name__ == '__main__':
    main()