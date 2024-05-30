'''
A package for convenience functions and classes
'''

#=======================================
#  $Revision: #2 $
#  $Change: 23052 $
#=======================================

import logging
import sys
import os, os.path
import re
import time
import inspect
import traceback
import shutil
import platform
import tempfile

from qb import convertpath, workerpathmap

#=======================================
# utils sub-packages
#=======================================
from . import files
from . import flags
import logging
from . import qbTokens
from . import regex
from .exceptions import *
from .enums import ENUMS


#===============================================================================
# misc helper functions
#===============================================================================
def addToSysPath(path, append=False):
    '''
    Add a path to the python module search path.
    
    @param path: The file path to add.
    
    @type path: C{str}
    
    @param append: Either insert the path at the head of sys.path, or append 
    to the end.
    
    @type append: C{bool} default: False
    '''
    if path:
        fullPath = os.path.abspath(path)
        if fullPath not in sys.path:
            if append:
                idx = len(sys.path) + 1
            else:
                idx = 0
            sys.path.insert(idx, fullPath)


def getModulePath():
    '''
    Get the path to the module that called this instance 
    
    @return: The file path to the backend's class module
    
    @rtype: C{str} 
    '''

    # original method (may break with Python 3.5+, since
    # inspect.getouterframes returns named tuples now; see
    # https://docs.python.org/3/library/inspect.html#the-interpreter-stack for
    # details):

    # frames = inspect.getouterframes(inspect.currentframe())
    # callingModulePath = frames[1][1]
    # modulePath = os.path.abspath(callingModulePath)
    
    # for frame in frames:
    #     del frame

    # new method (more compatible/future-proof)
    prev_frame = inspect.currentframe().f_back
    (filename, line_number, function_name, lines, index) = inspect.getframeinfo(prev_frame)
    modulePath = os.path.abspath(filename)

    # frame = inspect.currentframe()
    # while frame:
    #     print("frame: %s" % frame.f_code.co_filename)
    #     frame = frame.f_back

    return modulePath

def pyVerAsFloat():
    return float('%s.%s' % (sys.version_info[0], sys.version_info[1]))


def formatExc(limit=5):
    excAsStr = ''
    if pyVerAsFloat() > 2.3:
        excAsStr = traceback.format_exc(limit)
    else:
        excAsStr = traceback.print_exc()

    return excAsStr


def translateQbConvertPathStrings(cmd):
    """
    @param cmd: a python command to perform path translation on, according to the worker's
    worker_path_map.  The cmd is scanned for any string wrapped in C{QB_CONVERT_PATH()}
    @type cmd: C{str}

    @return: the cmd with any paths translated as necessary
    @rtype: C{str}
    """
    preTranslationCmd = cmd
    while cmd.count('QB_CONVERT_PATH'):
        # extract the path inside the first QB_CONVERT_PATH()
        unconvertedPath = regex.RGX_CONVERT_PATH_TOKEN.search(cmd).group(1).strip()

        # pass the path to qb.convertpath(), apply the worker_path_map
        convertedPath = convertpath(unconvertedPath)

        # trailing single backslashes cause the re module to throw a fit...
        if convertedPath.endswith('\\'):
            convertedPath += '\\'

        # double-quote the path if it contains spaces and is not already quoted
        if convertedPath.count(' ') and not re.search('^".*"$', convertedPath):
            convertedPath = '"%s"' % convertedPath

        # replace the original path with the converted one
        # encode the converted path so it makes it through re.sub() intact
        # cmd = regex.RGX_CONVERT_PATH_TOKEN.sub(convertedPath.encode('string_escape'), cmd, 1)
        cmd = regex.RGX_CONVERT_PATH_TOKEN.sub(convertedPath.encode('unicode_escape').decode(), cmd, 1)

    if cmd != preTranslationCmd:
        logging.info('Paths in the command have been translated as per this worker\'s worker_path_map')
        logging.info('%s %s' % (' '*4, preTranslationCmd))
        logging.info('%s -> %s' % (' '*1, cmd))

    return cmd


#===============================================================================
# file read/write utility functions
#===============================================================================
def sudoCopy(src, dst):
    '''
    Attempt to perform an authenticated copy.  An existing destination file will be overwritten.

    Prompt for authentication on OS X, otherwise just return an error message on other OS's upon failure.

    @param src: copy source file
    @type src: C{str}

    @param dst: copy destination file
    @type src: C{str}

    @return: Return an error message; a null-string indicates success
    @rtype: C{str}
    '''
    errMsg = ''

    # capture original timestamp of destination file, to test for success
    # also save file mode, so we can set new file to same mode
    try:
        dstStat = os.stat(dst)
        origMode = dstStat.st_mode
        origTimeStamp = dstStat.st_mtime
    except OSError:
        # dstFile doesn't exist
        origMode = None
        origTimeStamp = 0

    if not os.path.exists(src):
        # bail if src file specified, but does not exist
        errMsg = 'Source file %s does not exist.' % src
        logging.error(errMsg)

    if os.path.exists(dst):
        logging.log(logging.WARNING+5, 'Destination file exists, will be over-written: %s' % dst)
    else:
        logging.log(logging.INFO+5, 'Destination file does not exist, will be created: %s' % dst)

    if platform.system() == 'Darwin':
        # use 'authopen' on OS X
        result = os.system('cat %s | /usr/libexec/authopen -w -c %s' % (src, dst))
        if result != 0:
            errMsg = 'Unable to write to "%s".  Permission denied.' % dst
            logging.error(errMsg)
    else:
        if os.path.isfile(dst) and not os.access(dst, os.W_OK):
            # attempt to make the destination file writeable
            try:
                origMode = os.stat(dst).st_mode
                os.chmod(dst, origMode|stat.S_IWRITE|stat.S_IWGRP|stat.S_IWOTH)
            except OSError:
                errMsg = 'Unable to make existing destination file "%s" overwritable.' % dst
                logging.error(errMsg)

        if not errMsg:
            try:
                #=================================
                # finally - do the file copy...
                #=================================
                shutil.copy(src, dst)
                logging.info('Copied %s  -->  %s' % (src, dst))                   
            except IOError:
                errMsg = 'Unable to copy %s  -->  %s.  Permission denied.' % (src, dst)
                logging.error(errMsg)

            if not errMsg:
                try:
                    os.chmod(dst, origMode)
                    pass
                except:
                    logging.warning('Failed to re-set file mode for %s' % dst)
                    pass

                if origTimeStamp >= os.stat(dst).st_mtime:
                    errMsg = 'File copy failed somehow, destination timestamp is not later than source file timestamp'
                    logging.error(errMsg)

    return errMsg

 
def sudoWrite(data, dst, concat=False):
    '''
    Attempt to perform a file write that is expected to require authentication.

    @param data: data to write to the destination file
    @type data: C{str}

    @param dst: destination file
    @type dst: C{str}

    @param concat: if true, concat the data to the destination, otherwise overwrite destination
    @type concat: C{boolean}

    @return: Return an error message; a null-string indicates success
    @rtype: C{str}
    '''
    errMsg = ''

    if not data:
        errMsg = 'No data supplied to write to file %s.' % dst

    if not errMsg:
        if not os.path.isfile(dst) and platform.system() != 'Darwin':
            #================================================================
            # test ability to create destination file if it does not exist
            #================================================================
            logging.log(logging.WARNING+5, 'Destination file %s does not exist, will be created.' % dst)
            try:
                fh = open(dst, 'w')
                fh.write('')
                fh.close()
            except IOError as e:
                errMsg = 'Unable to create file: %s' % dst
                logging.error(errMsg)

        elif os.path.isfile(dst):
            #=================================================================================
            # backup file exists and will not be concatenated to, save a backup copy before
            # overwriting it
            #=================================================================================
            logging.log(logging.WARNING+5, 'Destination file %s will be overwritten, creating a backup copy.' % dst)

            backupFname = getTimestampedFileName(dst)
            errMsg = sudoCopy(dst, backupFname)
            if not errMsg:
                logging.info('Backup file created: %s' % backupFname)
            else:
                logging.error(errMsg)
                logging.warning('Unable to create a backup file: %s' % backupFname)

    if not errMsg:
        #==============================================================
        # destination file setup went OK, and we have data to write 
        #==============================================================
        if platform.system() == 'Darwin':
            
            (fd, tmpFile) = tempfile.mkstemp()
            fh = open(tmpFile, 'w')
            fh.writelines(data)
            fh.close()

            if concat and os.path.isfile(dst):
                result = os.system('cat %(dst)s %(src)s | /usr/libexec/authopen -w -c %(dst)s' % {'src':tmpFile, 'dst':dst})
            else:
                result = os.system('cat %s | /usr/libexec/authopen -w -c %s' % (tmpFile, dst))

            os.unlink(tmpFile)

            if result != 0:
                errMsg = 'Unable to write to destination file: %s' % dst
                logging.error(errMsg)
        
        else:
            if concat:
                fOpenMode = 'w+'
            else:
                fOpenMode = 'w'

            try:
                fh = open(dst, fOpenMode)
                fh.writelines(data)
                fh.close()
            except IOError as e:
                errMsg = e
                logging.error(errMsg)


    return errMsg


def getTimestampedFileName(fName):
    '''
    Generate a time-stamped backup file name:
        qb.conf -> qb.20121231_235959.conf

    @param fName: A file name
    @type fName: C{str}

    @return: A filename with a timestamp embedded in front of the file extension
    @rtype: C{str}
    '''
    timeFmt = '%Y_%m%d_%H%M%S'
    timestamp = time.strftime(timeFmt, time.localtime())
    
    (fRoot, fExt) = os.path.splitext(fName)
    newName = '%s.%s' % (fRoot, timestamp)
    if fExt:
        newName += '%s' % fExt

    return newName


