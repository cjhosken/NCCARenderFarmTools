"""
 Licensed Materials - Property of Pipelinefx L.L.C.

 (C) COPYRIGHT Pipelinefx Limited Liability Corporation.
 All Rights Reserved.

 US Government Users Restricted Rights - Use, duplication or
 disclosure restricted by GSA ADP Schedule Contract with
 Pipelinefx L.L.C.

 $DateTime: 2021/03/29 20:06:15 $
 $Revision: #1 $
 $Change: 23190 $
 $File: //depot/rel-7.5/qube/src/api/python/qb/backend/serverBackEnd.py $

"""

# vim: set foldcolumn=4 foldnestmax=3 :

import os
import sys
import time 
import logging
import socket
import platform
import subprocess

import qb.backend.pythonBackEnd
import qb.backend.utils as backendUtils

from qb.backend import QubeBackEndError
import qb.utils


class ServerBackEnd(qb.backend.pythonBackEnd.PythonQubeBackEnd):
    """
    A base class for server jobtypes written in Python.

    Similar to the commandBackEnd but no log parsing is done, instead the child
    process is passed back to the parent to poll directly.
    """

    def runServer(self, cmd, qbTokens=None):
        """
        @param cmd: the cmd for the child process
        @type cmd: C{str}

        @param qbTokens: a dictionary containing the various QB_FRAME* cmdrange tokens evaluated in the
        context of the current running work item to aid in calculating the in-chunk progress.

        @type qbTokens: C{dict}

        @return: the return the child process
        @rtype: C{}
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
        # application and OS, e.g, maya on macOS requires sourcing MayaEnv.sh
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
        process = self.runServerWithSubprocess(childArgs, qbTokens)

        return process

    def runServerWithSubprocess(self, childArgs, qbTokens=None):
        """
        Run via subprocess(), monitor child process and parse worker's job logs while the child is alive

        Log parsing is done while the child is alive, and once more after the job instance returns.

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
        process = subprocess.Popen(childArgs, stderr=childStderr, env=os.environ, cwd=childCwd, shell=shell)

        return process

    def executeWork(self):
        """
        This method must be defined for all derived classes.
        """
        raise NotImplementedError
