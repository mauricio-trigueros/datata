import sys
import src.helpers as helpers
import src.helpers_s3 as helpers_s3
import src.helpers_local as helpers_local
import src.helpers_server as helpers_server
import src.helpers_mysql as helpers_mysql

import commands

# To avoid errors like:
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xcc in position 56: ordinal not in range(128)
# When we process files that contains non standard characters
reload(sys)  
sys.setdefaultencoding('utf8')

print "   Reading parameters from terminal...."
raw_settings = helpers.read_raw_settings()
#print raw_settings
#print "   Parsing parameters...."
settings = helpers.parse_raw_settings(raw_settings)
#print settings

command = "{}(settings, {})".format(settings['command']['iterator'], settings['command']['command'])
print "   Executing command: command '{}'".format(command)
eval(command)