import sys
import src.helpers as helpers

import src.server.iterators as server_iterators
import src.server.commands as server_commands

import src.local.iterators as local_iterators
import src.local.commands as local_commands

import src.s3.iterators as s3_iterators
import src.s3.commands as s3_commands

import src.mysql.commands as mysql_commands

from src import commands

# To avoid errors like:
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xcc in position 56: ordinal not in range(128)
# When we process files that contains non standard characters
# FOR PYTHON 2
#reload(sys)  
#sys.setdefaultencoding('utf8')

print ("   Reading parameters from terminal....")
raw_settings = helpers.read_raw_settings()
#print (raw_settings)
#print "   Parsing parameters...."
settings = helpers.parse_raw_settings(raw_settings)
#print settings

command = "{}(settings, {})".format(settings['command']['iterator'], settings['command']['command'])
print ("\n\n   Executing command: command '{}'".format(command))
eval(command)