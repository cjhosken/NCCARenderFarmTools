'''
    A base class for command-line and command range jobtypes written in Python
'''
#======================================
#  $Revision: #1 $
#  $Change: 22715 $
#======================================

# vim: set foldcolumn=4 foldnestmax=3 :

import sys
import os
import re
import time 
import pprint
import logging
import socket
import platform

import qb.backend.pythonBackEnd
import qb.backend.logParser
import qb.backend.utils as backendUtils

from qb.backend import QubeBackEndError
import qb.utils


try:
    import subprocess
except ImportError:
    if os.name == 'posix':
        import popen2


class CommandBackEnd(qb.backend.pythonBackEnd.PythonQubeBackEnd):
    """
    A base class for command-line and command range jobtypes written in Python.

    The basic runtime log parsing functionality is defined here.
    """

    def runCmd(self, work, cmd, qbTokens=None):
        """
        Determine which module we can use to run the command:

        * subprocess if we're on python >= 2.4
        * popen2 if we're on an older python on linux

        @param work: either a Qube job instance or an agenda item
        @type work: C{dict}

        @param cmd: the cmd for the child process
        @type cmd: C{str}

        @param qbTokens: a dictionary containing the various QB_FRAME* cmdrange tokens evaluated in the
        context of the current running work item to aid in calculating the in-chunk progress.

        @type qbTokens: C{dict}

        @return: the return code of the child process' command
        @rtype: C{int}
        """

        #=============================================================
        # do run-time path translation by applying any worker-side 
        # path mappings to the entire cmd string
        #=============================================================
        preTranslationCmd = cmd

        #===============================================
        # Do worker-side path translation if available
        #===============================================
        if qb.utils.flags.isFlagSet('job_flags', 'convert_path', self.job['flags']):
            # ============================================================
            # if convert_path job flag is set, apply the path conversion
            # to the entire cmdline
            # ============================================================
            cmd = qb.convertpath(cmd)
        else:
            # ============================================================
            # convert any paths wrapped in QB_CONVERT_PATH()
            # ============================================================
            cmd = qb.utils.translateQbConvertPathStrings(cmd)

        #=============================================================
        # do the 'auto-pathing' for the job's application executable
        #=============================================================
        if 'appVersion' in self.job['package']:
            self.logging.info('Scanning for 3rd-party application...')
            try:
            
                cmd = backendUtils.translateAppPath(cmd, self.job['package']['appVersion'])

            except QubeBackEndError as e:
                #=====================================================
                # BAIL out here with an error condition,
                # since the application can't be found
                #=====================================================

                # print an appropriate error message
                hostname = socket.gethostname()
                errMsg = backendUtils.formatExc(limit=1)
                backendUtils.flushPrint('ERROR: %s -  %s' % (hostname, errMsg), fhList=[sys.stdout, sys.stderr])

                #=====================================================
                # update the job's resultpackage, then reportjob(), so that the errors show up in
                # the highlights panel
                #=====================================================
                errors = self.job.get('resultpackage', {}).get('errors', [])
                errors.append(e.value)
                self.job.setdefault('resultpackage', {})['errors'] = errors

                self.job['status'] = 'failed'
                qb.reportjob(self.job)

                # sleep, wait for supervisor to update the job resultpackage before this backend
                # exits, so that the resultpackage is not tossed before it gets written to the db
                time.sleep(5)

                return 1

        else:
            self.logging.debug('not attempting 3rd-party application auto-pathing')

        if cmd != preTranslationCmd:
            self.logging.info('Paths in the command have been translated as per this worker\'s worker_path_map')
            self.logging.info(r'%s %s' % (' '*4, preTranslationCmd))
            self.logging.info(r'%s -> %s' % (' '*1, cmd))

        #======================================================================================
        # CommandHandler instances provide the opportunity to setup the command for a specific
        # application and OS, e.g, maya on OS X requires sourcing MayaEnv.sh
        #
        # For now, only appFinder jobs have a commandHandler in their job package, and it's added to
        # the job by the appFinder's execute.py backend.  But we're running the
        # handler.prepareCommand() here so that in the future, other jobs have commandHandlers as
        # well.
        #======================================================================================
        preTranslationCmd = cmd

        if 'commandHandler' in self.job['package']:
            try:
                cmd = self.job['package']['commandHandler'].prepareCommand(self.job, cmd)
                if cmd != preTranslationCmd:
                    self.logging.info('The command has been modified via a application-specific commandHandler')
                    self.logging.info(r'%s %s' % (' '*4, preTranslationCmd))
                    self.logging.info(r'%s -> %s' % (' '*1, cmd))
            except:
                logging.error(backendUtils.formatExc())

        elif os.name == 'nt' and backendUtils.pyVerAsFloat() < 2.7:
            # ============================================================
            # The default commandHandler for Windows already does this,
            # but if there isn't one, then quote the cmd here
            #-------------------------------------------------------------
            #   Why pre-python 2.7 ?
            # Because subprocess.list2cmdline() behaves differently < 2.7
            # ============================================================
            cmd = '"%s"' % cmd

        #==============================================================
        # build the argument list to start the child process
        #==============================================================
        try:
            if os.name == 'posix':
                if 'shell' in self.job['package']:
                    shell = self.job['package']['shell']
                else:
                    shell = '/bin/sh'
            
                childArgs = [shell, '-c', r'%s' % cmd]
                backendUtils.flushPrint('COMMAND: %s' % ' '.join(childArgs))

            else:
                # Windows takes a single string, cast it as a raw string to avoid having to escape
                # any potential esc-chars
                childArgs = r'%s' % cmd
                backendUtils.flushPrint('COMMAND: %s' % childArgs)

            #==================================
            #   Actually run the command
            #==================================
            retCode = self.runCmdWithSubprocess(work, childArgs, qbTokens)

        except:
            retCode = 1
            backendUtils.flushPrint(backendUtils.formatExc(), fhList=[sys.stderr])

        return retCode

    def runCmdWithSubprocess(self, work, childArgs, qbTokens=None):
        """
        Run via subprocess(), monitor child process and parse worker's job logs while the child is alive

        Log parsing is done while the child is alive, and once more after the job instance returns.

        @param work: either a Qube job instance or an agenda item
        @type work: C{dict}

        @param childArgs: the arguments for the child process, the first element is the shell
        @type childArgs: C{list}

        @param qbTokens: a dictionary containing the various QB_FRAME* cmdrange tokens evaluated in the
        context of the current running work item to aid in calculating the in-chunk progress.

        @type qbTokens: C{dict}

        @return: the return code of the child process' command
        @rtype: C{int}
        """

        #===========================================================================
        # scan the job for anything that will customize the execution environment
        #===========================================================================
        childCwd = None
        if self.job['cwd']:
            if os.path.isdir(self.job['cwd']):
                self.logging.debug('Running job from directory: %s' % self.job['cwd'])
                childCwd = self.job['cwd']
            else:
                self.logging.debug('The working directory specified in the job is invalid: %s' % self.job['cwd'])
                self.logging.debug('Will use the following working directory: %s' % os.getcwd())

        if self.job['env']:
            os.environ.update(self.job['env'])

        # run-time OS environment variables
        if 'env_runTimeOS' in self.job['package']:
            runTimeOSEnv = self.job['package']['env_runTimeOS'].get(platform.system(), {})
            os.environ.update(runTimeOSEnv)

        childStderr = None
        if self.redirectingStdErr:
            childStderr = subprocess.STDOUT

        if os.name == 'nt':
            shell = True
        else:
            shell = False
        #===========================
        # actually fire up the job
        #===========================
        child = subprocess.Popen(childArgs, stderr=childStderr, env=os.environ, cwd=childCwd, shell=shell)

        #===========================
        # setup to parse the logs 
        #===========================
        errorRegexMatched = False
        fileSizeCheckFailed = False

        stdoutLog, stderrLog = backendUtils.getJobLogPaths(self.redirectingStdErr)

        if len(stdoutLog) and \
                (self.redirectingStdErr or (
                    not(self.redirectingStdErr) and len(stderrLog))):
            self.jobLogs = {'stdout': stdoutLog}

            if not self.redirectingStdErr:
                self.jobLogs['stderr'] = stderrLog

            #===========================
            # now parse the logs 
            #===========================
            while child.poll() is None and not (errorRegexMatched or fileSizeCheckFailed):
                
                backendUtils.flushPrint('INFO: Scanning logs for errors, outputPaths, etc...', fhList=sys.stderr)
                errorRegexMatched, fileSizeCheckFailed = self.logHandler(work, qbTokens)
                if errorRegexMatched or fileSizeCheckFailed:
                    work['status'] = 'failed'
                    break

                for i in range(1, self.LOGREAD_TIME_THRESHOLD+1):
                    # don't get caught waiting for up to 5s if the child has just exited)
                    if child.poll() is None:
                        time.sleep(1)

            #================================================================
            # now that the child has exited, check the logs one more time
            #================================================================
            errorRegexMatched, fileSizeCheckFailed = self.logHandler(work, qbTokens)
            if errorRegexMatched or fileSizeCheckFailed:
                work['status'] = 'failed'
        else:
            self.logging.warning('Unable to find job logs, no log parsing will occur during job instance execution')
            child.wait()

        sys.stdout.flush()

        #===========================================================================================
        # the job instance may have had its status set as a result of an error found during the log
        # parsing, so even if the cmd returns 0, there may still be an error condition
        #===========================================================================================
        if self.job['status'] == 'failed' or work['status'] == 'failed':
            retCode = 1
        else:
            retCode = child.returncode

        return retCode

    def executeWork(self):
        """
        This method must be defined for all derived classes.
        """
        raise NotImplementedError
