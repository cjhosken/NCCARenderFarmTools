## -----------------------------------------------------------------------------
##   
##      Module defining some convenience functions that are used by various backends.
##
##      Copyright: Pipelinefx L.L.C. 
##
## -----------------------------------------------------------------------------

#======================================
#  $Revision: #2 $
#  $Change: 23052 $
#======================================

import sys
import os, os.path
import re
import time
import socket
import inspect
import traceback
import logging
import datetime

import qb
from qb.backend import QubeBackEndError

# following used to replace python2 call for isinstance(fh, file) to python3 call, isinstance(fh, IOBase)
from io import IOBase

HOSTNAME = socket.gethostname()
try:
    HOSTNAME = HOSTNAME.split('.')[0]
except IndexError:
    pass

RGX_APP_TOKEN = re.compile('__([A-Z1-9]+)__')


def addToSysPath(path, insert=False):
    '''
    Add a path to the python module search path.
    
    @param path: The file path to add.
    
    @type path: C{str}
    
    @param insert: Either insert the path at the head of sys.path, or append 
    to the end.
    
    @type insert: C{bool} default: False
    '''
    if path:
        fullPath = os.path.abspath(path)
        if fullPath not in sys.path:
            if insert:
                idx = 0
            else:
                idx = len(sys.path) + 1
            sys.path.insert(idx, fullPath)

def getDevBoolean(job):
    '''
    Work around the various ways that objects get cast to strings in the qube job object.
    
    Add a package dict to the job if one is not found; this can occur when an empty dict
    is used as a mock job during unittesting.
    
    @param job: The job to run
    
    @type job: C{dict} or qb.Job 
    
    @return: Return a boolean value of the value the job package's 'dev' key; this can be
    either a string, int, or NoneType
    
    @rtype: C{bool}
    '''
    dev = job.get('package', {}).get('dev', False)

    if dev and isinstance(dev, str):
        if dev.lower().startswith('f'):
            dev = False
        else:
            try:
                dev = bool(int(dev))
            except ValueError:
                dev = bool(dev)

    return dev


def getJobBoolean(job_attr):
    """
    Work around the various ways that objects get cast to strings in the qube job object.

    Add a package dict to the job if one is not found; this can occur when an empty dict
    is used as a mock job during unittesting.

    @param job_attr: The job attribute to check
    @type job_attr: C{str}

    @return: Return a boolean value of the value; this can be either a string, int, or NoneType
    @rtype: C{bool}
    """
    if job_attr is None or job_attr == 0 or job_attr == '':
        job_attr = False
    elif job_attr and isinstance(job_attr, str):
        if job_attr.lower().startswith('f'):
            job_attr = False
        else:
            try:
                job_attr = bool(int(job_attr))
            except ValueError:
                job_attr = bool(job_attr)

    return job_attr


def getJobPackageBoolean(val):
    """
    Work around the various ways that objects get cast to strings in the qube job object.

    @param val: the val to test for T/F
    @type val: C{str} or C{int} or C{bool}

    @return: Return a boolean value of the value
    @rtype: C{bool}
    """
    if val and isinstance(val, str):
        if val.lower().startswith('f'):
            val = False
        else:
            try:
                val = bool(int(val))
            except ValueError:
                val = bool(val)

    return val

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

def getClassFromJobData(data):
    '''
    Import an abritrary module, and return a class object (not an instance) from that module.
    
    @param data: A dictionary describing the class object, must contain the following keys: libPath, modulePath, className
    @type data: C{dict}
    '''
    #assert data['libPath']
    assert data['modulePath']
    assert data['className']

    if 'libPath' in data:
        addToSysPath(data['libPath'], insert=True)
    
    moduleObj = __import__(str(data['modulePath']))

    for pkg in data['modulePath'].split('.')[1:]:
        moduleObj = getattr(moduleObj, pkg)
    
    klass = getattr(moduleObj, data['className'])
    return klass

def pyVerAsFloat():
    return float('%s.%s' % (sys.version_info[0], sys.version_info[1]))

def formatExc(limit=5):
    excAsStr = ''
    if pyVerAsFloat() > 2.3:
        excAsStr = traceback.format_exc(limit)
    else:
        excAsStr = traceback.print_exc()

    return excAsStr

def flushPrint(msg='', fhList=None):
    if not fhList:
        fhList = [sys.stdout]
    elif not isinstance(fhList, list):
        fhList = [fhList]
        
    for fh in fhList:
        fh.flush()
        fh.write('%s\n' % msg)
        fh.flush()

def bannerPrint(msg='', timeFormat=None, fhList=None):
    """
    Print a nicely-formatted message with a timestamp, easily readable in
    a job's stdout/stderr logs
    
        >>> bannerPrint( 'Finished work' )
        ================================================================================
         13:05:31        Finished work                                        render023
        ================================================================================

    @param msg: The message to be printed
    @type msg: string

    @param timeFormat: a format string suitable for time.strftime()
    @type timeFormat: string

    @param fhList: A list of file objects to print to.  Optionally supports
    being passed a single file object; eg. 'fhList=sys.stderr'.

    @type fhList: list
    """
    
    TIMEFMT = '%H:%M:%S'

    if not timeFormat:
        timeFormat = TIMEFMT
        
    if not fhList:
        fhList = [sys.stdout]
        
    if (sys.version_info[0] < 3 and isinstance(fhList, file)) or (isinstance(fhList, IOBase)):
        fhList = [ fhList ]

    LINELEN = 80 
    timestr = time.strftime(timeFormat, time.localtime())

    for fh in fhList:
        msgStr = ' %(time)s%(tab)s%(msg)s' % {'time':timestr, 'tab':' '*8, 'msg':msg}

        fh.write('%s\n' % ('='*LINELEN,))
        fh.write('%s %*s\n' % (msgStr, LINELEN-(len(msgStr)+2), HOSTNAME))
        fh.write('%s\n' % ('='*LINELEN,))
        fh.flush()

def configLogging(level):
    loggingLevel = logging.WARNING
    loggingFormat = logging.BASIC_FORMAT

    if level == 'debug':
        loggingLevel  = logging.DEBUG
        loggingFormat = '%(name)20s : %(levelname)-8s : %(message)s (%(filename)s:%(lineno)d, %(threadName)s)'
    elif level == 'warning':
        loggingLevel  = logging.INFO
        loggingFormat = '%(levelname)s:%(name)s: %(message)s'
        
    rootLogger = logging.getLogger()

    logHandler = logging.StreamHandler()
    logHandler.setFormatter(logging.Formatter(loggingFormat, None))
    rootLogger.addHandler(logHandler)
    rootLogger.setLevel(loggingLevel)

def scanConfForPaths(confPath, blockName):
    '''
    scan a job.conf for a multi-line block the is bound by [...], with the closing bracket at the beginning of a new line.

    valid OS names acting as keys in the job.conf are those returned by sys.platform

    example:

    HFS_PATHS = [
    darwin:"/Library/NotFoundHere/Houdini.framework/Versions/0.0.0/Resources"
    darwin: "/Library/Frameworks/Houdini.framework/Versions/0.0.0/Resources"
    linux2:"/opt/hfs0.0.0"
    win32: "C:/Program Files/Side Effect Software/Houdini 0.0.0"
    ]

    return a dictionary, keyed of sys.platform names, values are a list of paths 
    '''
    paths = {}
    osPathRGX = re.compile('^(\w+):\s*"(.*)"')

    fh = open(confPath)
    lines = fh.readlines()
    fh.close()

    blockFound = False
    for i in range(len(lines)):

        line = lines[i]

        if blockFound is False and line.startswith(blockName):
            blockFound = True
            continue

        if blockFound:
            if line.startswith('['):
                # reached the end of the HFS_PATH block
                break

            m = osPathRGX.search(line)
            if m:
                try:
                    (osName, path) = m.groups()
                    paths.setdefault(osName, []).append(path)
                except ValueError:
                    flushPrint('ERROR: %s contains an invalid %s definition line at line %s' % (confPath, blockName, i), fhlist=[sys.stderr])

    return paths

def getJobLogPaths(redirectingStdErr=False):
    jobStdoutLog = ''
    jobStderrLog = ''

    hostName = socket.gethostname()
    workerCfg = qb.workerconfig(hostName)

    logRoot = workerCfg.get('worker_logpath', '')
    if logRoot == '':
        logging.error('Unable to determine worker_logpath for host %s' % hostName)
    
    try:
        jobId = int(os.environ.get('QBJOBID'))
        instanceId = int(os.environ.get('QBSUBID', 0))
    except:
        logging.error('Unable to determine job log paths, either QBJOBID or QBSUBID environment variables are not set.')
        return ('','')

    jobLogBucketDir = jobId - (jobId % 1000)

    jobLogDir = '%s/job/%s/%s' % (logRoot, jobLogBucketDir, jobId)

    jobStdoutLog = '%s/%s_%s.out' % (jobLogDir, jobId, instanceId)
    if not os.path.exists(jobStdoutLog):
        logging.warning('stdout job log not found: %s' % os.path.normpath(jobStdoutLog))
        jobStdoutLog = ''

    if not redirectingStdErr:
        jobStderrLog = '%s/%s_%s.err' % (jobLogDir, jobId, instanceId)
        if not os.path.exists(jobStderrLog):
            logging.warning('stderr job log not found: %s' % os.path.normpath(jobStderrLog))
            jobStderrLog = ''

    return (jobStdoutLog, jobStderrLog)

def translateAppPath(cmd, appVersion):
    appToken = None

    m = RGX_APP_TOKEN.search(cmd)
    if m:
        try:
            appToken = m.group(1)
        except IndexError:
            logging.error('IndexError: no appToken found')
            pass
    else:
        logging.warning('translateAppPath: no appToken "%s" found, assuming explicit path to application executable' % RGX_APP_TOKEN.pattern)

    if appToken:
        from . import appDefaultPaths
        # this call to buildAppPath can raise an AppVersionNotFoundError, but we need to catch this
        # higher up, and fail the job instance, not the agenda item
        appPath = appDefaultPaths.buildAppPath(appToken, appVersion)
        # Python3 does not tolerate the '\P' in "C:\Program Files\..."
        appPath = appPath.replace('\\', '/')
        cmd = re.sub('__%s__' % appToken, appPath, cmd)

    return cmd

class PFXSimpleTimer(object):
    """
    A convenience class containing some simple timer-type methods
    """
    def __init__(self):
        self.startTime = 0
        self.endTime = 0
        self.timerIsRunning = False

    def startTimer(self):
        self.startTime = datetime.datetime.now()
        self.timerIsRunning = True

    def stopTimer(self):
        self.endTime = datetime.datetime.now()
        self.timerIsRunning = False

    def elapsedTime(self):
        if self.endTime == 0:
            endTime = datetime.datetime.now()
        else:
            endTime = self.endTime
        et = endTime - self.startTime
        eTime = et.seconds + (et.microseconds/1e6)
        return eTime
