#!/usr/bin/python

__description__ = 'skype-scraper, use it to dump URLs recently shared in your Skype conversations'
__author__ = 'SeaDawg'
__version__ = '0.1.1'
__date__ = '2014-09-30'

# Use at your own risk. :)

import os
import re
import sqlite3
import getpass
import shutil

from optparse import OptionParser

options = OptionParser(usage='usage: %prog [options]', description='Desc: '+__description__, version='%prog ' + __version__)
options.add_option('-t', '--time', dest='time', type='int', default=24, help='Time in hours to search backwards')

def main():
   opts, args = options.parse_args()

   numHours = opts.time

   if numHours > 0:
      # Retrieve system user
      sys_user = getpass.getuser()

      # Retrieve Skype username & urlencode to remove potential colon in username
      with open('/Users/'+sys_user+'/Library/Application Support/Skype/shared.xml','r') as f:
         items = re.findall("<Default>(.+?)<",f.read(),re.MULTILINE)
         for i in items:
            skype_user = i.replace(':','#3a')
   
      # Copy skype db to current dir to avoid db lock if Skype is currently running
      shutil.copyfile('/Users/'+sys_user+'/Library/Application Support/Skype/'+skype_user+'/main.db','skype.db')

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
