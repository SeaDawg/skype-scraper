#!/usr/bin/python

__description__ = 'skype-scraper, use it to dump URLs recently shared in your Skype conversations'
__author__ = 'SeaDawg'
__version__ = '0.2.0'
__date__ = '2014-09-30'

# Use at your own risk. Should be okay though. :)

import os
import re
import sys
import sqlite3
import getpass
import shutil
import platform
from optparse import OptionParser

options = OptionParser(usage='usage: %prog [options]', description='Desc: '+__description__, version='%prog ' + __version__)
options.add_option('-t', '--time', dest='time', type='int', default=24, help='Time in hours to search backwards')

def main():
   opts, args = options.parse_args()

   # Set number of hours to look back in Skype history
   numHours = opts.time

   if numHours > 0:
      # ID host OS
      host_os = platform.system()

      # ID current user
      sys_user = getpass.getuser()

      # Set Skype user doc location
      skype_doc = ''
      if host_os == 'Windows':
         skype_doc = 'C:\\Documents and Settings\\'+sys_user+'\\Application Data\\Skype\\shared.xml'
      elif host_os == 'Darwin':   
         skype_doc = '/Users/'+sys_user+'/Library/Application Support/Skype/shared.xml'
      elif host_os == 'Linux':
         skype_doc = '/home/'+sys_user+'/.Skype/shared.xml'
      else:
         print('Host OS UNKNOWN! Exiting...')
         sys.exit()

      # Retrieve Skype username & adjust for Skype's encoding
      skype_user = ''
      with open(skype_doc,'r') as f:
         items = re.findall("<Default>(.+?)<",f.read(),re.MULTILINE)
         for i in items:
            skype_user = i.replace(':','#3a')
         if skype_user == '':
            print("Could not determine your Default Skype username. Exiting...")
            sys.exit()
      # Copy skype db to current dir to avoid db lock if Skype is currently running
      if host_os == 'Windows':
         shutil.copyfile('C:\\Documents and Settings\\'+sys_user+'\\Application Data\\Skype\\'+skype_user+'\\main.db','skype.db')
      elif host_os == 'Darwin':
         shutil.copyfile('/Users/'+sys_user+'/Library/Application Support/Skype/'+skype_user+'/main.db','skype.db')
      elif host_os == 'Linux':
         shutil.copyfile('/home/'+sys_user+'/.Skype/'+skype_user+'/main.db','skype.db')

      # Open the skype db to access chat history
      conn = sqlite3.connect('skype.db')
      c = conn.cursor()

      # Query for default skype user's recent chat history and extract URLs
      for row in c.execute("SELECT timestamp,body_xml FROM messages WHERE timestamp>=strftime('%s','now')-3600*?",(str(numHours),)):
         try:
            url = re.search('href="(.+?)">',str(row)).group(1) 
            print str(url)
         except AttributeError:
            url = ''
            continue

      # Close db connection and delete copy of db
      conn.close()
      os.remove('skype.db')

   else:
      options.print_help()
      return
      
if __name__ == '__main__':
    main()