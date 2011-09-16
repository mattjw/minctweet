#!/usr/bin/python
#
# Copyright 2011 Matthew J Williams
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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

import tweepy

class FileMonitor(object):
    """
    A monitor that reads additions to a text file. Lines existing before 
    monitoring was initiated are ignored.
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
        self.nextline()
    
    def nextline( self ):
        """
        Return the next line in the file. The newline symbol is discarded. 
        This method will block until a new line is added to the file.
        """
        self.tailproc.poll()
        if self.tailproc.returncode is not None:
            raise RuntimeError( "tail subprocess quit unexpectedly" )
        
        ln = self.proc_stdout.readline()     # if no more lines, this will wait
        ln = ln.rstrip( '\n' )
        return ln

def handle_log_entry( log_line, tweepy_api ):
    """
    This method responds to new log entries.
    """
    f = open('tweet.log', 'a')
    f.write(log_line+"\n")
    f.close()
    splitString = log_line.split()
    
    # Check for server coming online
    if(len(splitString) > 2):
    	if(splitString[3] == "Done"):
    		tweepy_api.update_status("Server has been launched and is now online.")
    		print "Done"
    		
    # Check for user tweeting to account from config
    if(len(splitString) > 4):		
		if(splitString[4] == "tweet"): 
			tweetText = ""
			for x in range(5,len(splitString)):
				tweetText += splitString[x]+" "
			tweepy_api.update_status(tweetText)
			print tweetText
	
	# Check for user login and get the name
    if(len(splitString) > 5):
    	if(splitString[5] == "logged"):
    	 	tweepy_api.update_status("User "+splitString[3]+" joined the game.")
    		print "User ",splitString[3]," joined the game"
    
    # Check for user logout and get the name
    if(len(splitString) > 6):
    	if((splitString[4] == "lost") & (splitString[5] == "connection:")):
    		tweepy_api.update_status("User "+splitString[3]+" left the game.")
    		print "User ",splitString[3]," left the game"
    
    # Check for server going down
    if(len(splitString) > 10):
    	if((splitString[5] == "server") & (splitString[10] == "down.")):
    		tweepy_api.update_status("Server has been taken offline. All connections will be lost.")
    		print "Server has been taken offline. All connections will be lost."
	

def main():
    
    config_fpath = "/home/minecraft/minctweet/server.config"
    
    if not os.path.exists( config_fpath ):
        print "%s: file does not exist" % (config_fpath)
        exit()
    
    if not os.path.isfile( config_fpath ):
        print "%s: is not a file" % (config_fpath)
        exit()
    
    config_dict = {}
    fin = open( config_fpath, 'r' )
    rdr = csv.reader( fin, delimiter='=' )
    for row in rdr:
        (field,val) = row
        config_dict[field] = val
    fin.close()
    
    #
    # Auth twitter
    consumer_key = config_dict['consumer_key']
    consumer_secret = config_dict['consumer_secret']
    access_key = config_dict['access_key']
    access_secret = config_dict['access_secret']
    
    #~ to do: connect to twitter
    auth = tweepy.OAuthHandler( consumer_key, consumer_secret )
    auth.set_access_token( access_key, access_secret )
    api = tweepy.API( auth )
    
    #
    # Hook into log file
    mclog_fpath = config_dict['log']
    
    if not os.path.exists( mclog_fpath ):
        print "%s: file does not exist" % (mclog_fpath)
        exit()
    
    if not os.path.isfile( mclog_fpath ):
        print "%s: is not a file" % (mclog_fpath)
        exit()
    
    logmon = FileMonitor( mclog_fpath )
    
    print "minctweet: making your Minecraft server tweet"
    print "monitoring log file:", mclog_fpath
    
    while True:
        ln = logmon.nextline()
        handle_log_entry( ln, api )
        
if __name__ == '__main__':
    main()
