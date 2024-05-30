'''
A module containing any regex objects that could be used across more than 1 module
'''

#=======================================
#  $Revision: #1 $
#  $Change: 22715 $
#=======================================

import re


#===============================
# The QB_CONVERT_PATH token is used in the run-time path conversion
# - return the string inside the first found instance of QB_CONVERT_PATH(...)
#===============================
RGX_CONVERT_PATH_TOKEN = re.compile('QB_CONVERT_PATH\(((?<=\()(?:[^()]+|\([^)]+\))+(?=\)))\)')


