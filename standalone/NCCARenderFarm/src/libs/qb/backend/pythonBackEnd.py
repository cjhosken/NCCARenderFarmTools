## -----------------------------------------------------------------------------
##   
##      Module defining the base class for Qube python jobTypes that communicate with a separate
##      running python interpreter, usually running inside a 3rd-party application.
##
##      It also contains some convenience functions that are used by various backends.
##
##      Copyright: Pipelinefx L.L.C. 
##
## -----------------------------------------------------------------------------

#======================================
#  $Revision: #1 $
#  $Change: 22715 $
#======================================


import sys
import os
import time
import pprint
import logging
import stat

import qb.backend.utils as backendUtils
import qb.backend.logParser


#============================================================
#       PythonQubeBackEnd class definition
#============================================================

class PythonQubeBackEnd(object):
    """
    The base class for PipelineFX's python back-end modules.

    @cvar LOGREAD_TIME_THRESHOLD: how often to parse the job log data for regex matches
    @type LOGREAD_TIME_THRESHOLD: C{int}
    """
    
    QB_WAITING_TIMEOUT = 5
    LOGREAD_TIME_THRESHOLD = 30

    def __init__(self, job):
        """
        Function to initialize class members.

        @param job: The qube job object passed to the worker, this represents a job instance.

        @type job: qb.Job
        """
        # submit the job with job['package']['dev'] = True to set the logging level to DEBUG
        self.logging = logging.getLogger('%s' % self.__class__.__name__)

        self.job = job
        self.status = 0

        self.dev = backendUtils.getDevBoolean(self.job)

        if hasattr(backendUtils, 'getJobBoolean'):
            self.outputPaths_required = backendUtils.getJobBoolean(self.job.get('package', {}).get('outputPaths_required', False))
        else:
            # ------------------------------------------------------------
            # backwards compatibility - remove in the main branch for 6.9
            # ------------------------------------------------------------
            try:
                self.outputPaths_required = bool(self.job.get('package', {}).get('outputPaths_required', False))
            except ValueError:
                self.outputPaths_required = False

        # set the time to wait in seconds if you've updated the work result package for a running job
        self.resultPkgUpdateThrottleTimeout = 5

        self.redirectingStdErr = backendUtils.getJobPackageBoolean(self.job['package'].get('redirectStderrToStdout', False))

        # track the file offsets for each job log stream
        self.jobLogs = dict(
            list(zip(['stdout', 'stderr'],
                backendUtils.getJobLogPaths(self.redirectingStdErr)))
        )
        # catch development case, no job logs present, reset the jobLogs dict to empty, this will
        # short-circuit the logHandler method
        if '' in list(self.jobLogs.values()):
            self.jobLogs = {}

        self.fhOffsets = {'stderr': 0, 'stdout': 0}

        # init the logParser, fall back to a default if one is not specified in the job.
        if self.job.get('package', {}).get('logParser', {}).get('className'):
            logParserClass = backendUtils.getClassFromJobData(self.job['package']['logParser'])
        else:
            logParserClass = qb.backend.logParser.LogParser
        self.logParser = logParserClass(self.job)

        if hasattr(qb, 'workerpathmap'):
            self.workerPathMap = qb.workerpathmap()
        else:
            self.workerPathMap = {}

    def printClassInfo(self):
        backendUtils.flushPrint('%16s: %s' % ('Backend class', self.__class__.__name__))
        backendUtils.flushPrint('%16s: %s' % ('Backend module', os.path.abspath(sys.modules[self.__class__.__module__].__file__)))
        backendUtils.flushPrint('%16s: %s' % ('LogParser class', self.logParser.__class__.__name__))
        backendUtils.flushPrint('%16s: %s' % ('LogParser module', os.path.abspath(sys.modules[self.logParser.__class__.__module__].__file__)))
        
    def jobSetup(self):
        """
        Perform any steps necessary to initialize the working enviroment prior to
        beginning any agendaItem-specific steps.
        """
        self.job['status'] = 'running'

        if self.dev:
            pp = pprint.PrettyPrinter(indent=2, width=1)
            print("DEBUG BEGIN:")
            print("JOB:")
            pp.pprint(self.job)
            print("DEBUG END:")

    def executeWork(self):
        """
        Request an agendaItem (work) from the supervisor and do any steps necessary to
        perform the work.

        @raise NotImplementedError: Raised when this method is not overridden in a derived class.
        """
        raise NotImplementedError
    
    def jobTeardown(self):
        """
        Perform any steps necessary to clean up the working enviroment prior to
        shutting down the job instance.
        """
        pass

    def hasJobPhaseCmds(self, phase):
        """
        Test for the existence of job setup/teardown cmds in the job package
        """
        if 'package' in self.job and phase in self.job['package']:
            hasCmds = True
        else:
            hasCmds = False
        return hasCmds

    def getLogData(self, logpath, iostream, offset=0):
        """
        seek fwd in a file, read to EOF, then record the file position, which will be the offset
        the next time we enter this function

        @param logpath: full path to a job log file to scan
        @type logpath: C{str}

        @param iostream: name of the iostream, usually "stderr" or "stdout"
        @type iostream: C{str}

        @param offset: position in file to begin to read data from
        @type offset: C{int}

        @ivar data: the section the the job log, usually multiple lines, as a single string
        @type data: C{str}

        @ivar fPos: the position in the file where reading stopped, length in bytes from BOF to EOF
        @type fPos: C{int}

        @return: a tuple containing the log data and the end position of the file
        @rtype: C{tuple}
        """
        data = ''

        fh = open(logpath)
        self.logging.debug('%s beginning offset: %s' % (iostream, offset))
        fh.seek(offset)

        data = fh.read()
        fPos = fh.tell()

        self.logging.debug('%s offset: %s' % (iostream, offset))
        self.logging.debug('%s ending fPos: %s' % (iostream, fPos))
        self.logging.debug('%s len data (expected): %s' % (iostream, fPos-offset))

        fh.close()
        return (data, fPos)

    def logHandler(self, work, qbTokens=None):
        """
        Parse a job log for regex matches (progress, errors, outputPaths, etc...), update the
        job or work packages with the logmatches, set the job status accordingly, and report
        back to the supervisor.

        @return: Return booleans for each error condition checked; error regex found a match, and
        whether a size check failed

        @rtype: C{tuple}

        @param qbTokens: a dictionary containing the various QB_FRAME* cmdrange tokens evaluated in the
        context of the current running work item to aid in calculating the in-chunk progress.

        @type qbTokens: C{dict}
        """
        errorMatched = False
        sizeCheckFailed = False

        logMatches = {}

        if self.jobLogs:
            for (iostream, logpath) in list(self.jobLogs.items()):

                self.logging.debug('%s %s %s' % ('-'*20, iostream, '-'*20))
                (logData, self.fhOffsets[iostream]) = self.getLogData(logpath, iostream, self.fhOffsets[iostream])

                if len(logData):
                    self.logging.debug('logData: %s' % len(logData))

                    # Cull lines where the backend code itself is reporting an error regex match,
                    # causes subsequent frames to be marked as failed, since the matched error
                    # string is reported back as part of the error message...
                    if iostream == 'stderr':
                        culledLogData = []
                        for l in logData.splitlines():
                            if l.startswith('ERROR') and l.count('regex_errors found match'):
                                continue
                            else:
                                culledLogData.append(l)
                        logData = '\n'.join(culledLogData)
                        del culledLogData

                    logMatches.update(
                        self.parseLogData(logData, qbTokens)
                    )

                self.logging.debug('%s\n' % ('-'*48))

        if logMatches:
            self.updateResultPackage(work, logMatches)
            sizeCheckFailed = not(self.validateOutputFileSize(work))

            if 'errors' in logMatches:
                errorMatched = True
                self.logging.error('regex_errors found match: "%s"' % ', '.join(logMatches['errors']))

            if not (sizeCheckFailed or errorMatched):
                # ------------------------------
                # TODO: get rid of these sleep()s as soon
                # as qb.updateresultpackage is available
                # ------------------------------
                if id(work) == id(self.job):
                    qb.reportjob(self.job)
                    time.sleep(5)
                else:
                    qb.reportwork(work)
                    time.sleep(5)

        return errorMatched, sizeCheckFailed

    def updateResultPackage(self, work, resultDict):
        """
        Update the Qube qb.Work object's resultpackage dictionary.
    
        The resultpackage is a dictionary that the Qube supervisor retrieves from
        the worker after processing work.  It can be used to update the job object
        with data that is determined at execution time.
    
        Any key/value pairs can be passed into the resultpackage as a dictionary; it's up to the
        developer to pass key/values that are meaningful to Qube.
    
        The most common use is to set the 'outputpaths' value for an agenda item.
        This value is used by the Qube GUI to display the image in the "Output"
        tab of the UI.
    
        @param work: The Qube qb.Work object whose resultpackage dictionary is to be updated

        @param resultDict: a dictionary containing key/value pairs to be inserted into the work's
        resultpackage dictionary.
    
        @type work: qb.Work
        """
        if 'resultpackage' not in work or not work['resultpackage']:
            work['resultpackage'] = {}
        
        rpkg = work['resultpackage']

        for k in resultDict:
            if k in rpkg:
                if k == 'outputPaths':
                    outputPaths = rpkg[k]
                    # avoid inserting duplicates
                    for imgPath in resultDict[k].split(','):
                        if imgPath not in outputPaths:
                            outputPaths += ',%s' % imgPath
                    rpkg[k] = outputPaths
                elif k == 'progress':
                    rpkg[k] = resultDict[k]
                elif isinstance(rpkg[k], list):
                    rpkg[k].extend(resultDict[k])
                elif isinstance(rpkg[k], dict):
                    rpkg[k].update(resultDict[k])
            else:
                rpkg[k] = resultDict[k]

    def parseLogData(self, data, *args):
        """
        Find any matches to the job's regular expressions.

        @param data: a portion of a job instance's job log
        @type data: string
        """
        if self.logParser:
            matches = self.logParser.parse(data, *args)
        else:
            backendUtils.flushPrint('WARNING: parseLogData method called, but %s instance has no logParser defined\n' % self.__class__.__name__, fhList=sys.stderr)

        self.logging.debug('Matches: %s' % len(matches))
        return matches
    
    def validateOutputFileSize(self, work):
        """
        Check the work/jobInstance's resultpackage for any files in the outputPaths, and ensure that
        their file size exceeds the job's minimum file size

        @param work: The work/job object whose resultpackage dictionary is to be scanned
        @type work: qb.Work or qb.Subjob

        @return: return False if the contents of the outputPaths contain a file path whose size does not
        exceed the job's validate_fileMinSize, otherwise return True for all other cases.

        @rtype: C{bool}
        """
        fileSizeOK = True

        if 'validate_fileMinSize' in self.job['package']:
            
            minFileSize = int(self.job['package']['validate_fileMinSize'])
            if minFileSize > 0:
                chunk_size = work.get('resultpackage', {}).get('outputPaths', '').count(',')

                # only check the file size for up to the first five frames in a chunk
                for f in work.get('resultpackage', {}).get('outputPaths', '').split(',')[:4]:
                    if f:
                        if os.path.isfile(f):
                            if chunk_size == 1:
                                # sleep to allow the filesystem to finish writing the file to disk,
                                # occasionally it sees it as 0 bytes
                                time.sleep(0.5)
                            sys.stdout.flush()
                            fSize = os.stat(f)[stat.ST_SIZE]

                            if fSize >= minFileSize:
                               #sys.stdout.flush()
                               backendUtils.flushPrint('INFO: file size check passed: %s > %s' % (fSize, minFileSize))
                            else:
                               fileSizeOK = False
                               backendUtils.flushPrint('ERROR: An output file has failed a size verification check, and is smaller than %s bytes.' % minFileSize, fhList=[sys.stdout, sys.stderr])
                               backendUtils.flushPrint('ERROR:   %s is %s bytes' % (f, fSize), fhList=[sys.stdout, sys.stderr])
                        else:
                            backendUtils.flushPrint('Warning: A value that matched the job\'s "outputPaths" regular expression is not a file.')
                            backendUtils.flushPrint('Warning:   The regular expression may need some refinement.')
                            backendUtils.flushPrint('Warning:   regex = "%s"' % self.job['package'].get('regex_outputPaths', '< regex_outputPaths is undefined>'))
                            backendUtils.flushPrint('Warning:   matched =  "%s"' % f)

        return fileSizeOK

