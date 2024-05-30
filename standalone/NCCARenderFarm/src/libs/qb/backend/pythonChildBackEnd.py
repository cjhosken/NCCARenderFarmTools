'''
    Module defining the base class for Qube python jobTypes which communicate with a separate
    running python interpreter, usually running inside a 3rd-party application.

    Copyright: Pipelinefx L.L.C. 
'''

#======================================
#  $Revision: #2 $
#  $Change: 22906 $
#======================================

import sys
import os.path
import time
import pprint
import traceback as tb

import qb.utils
import qb.backend.utils as backendUtils
import qb.backend.pythonBackEnd
import qb.backend.pythonChildHandler


class PythonChildBackEnd(qb.backend.pythonBackEnd.PythonQubeBackEnd):
    """
    A python-based Qube backend that has a PyCmdDispatcher.  
    
    It will run another python interpreter of some sort (usually a 2D or 3D app) as a child process,
    and interact with it via the PyCmdDispatcher.
    """

    DEFAULT_PYTHON = sys.executable
    
    def __init__(self, job):
        """
        """
        super(PythonChildBackEnd, self).__init__(job)

        self.cmdDispatcher = None
        self.childBootstrapper = None
        self.pyExecutable = self.job['package'].get('pyExecutable', self.DEFAULT_PYTHON)

    def getSubprocessArgs(self, port):
        """
        Determine the arguments necessary to invoke the child process.

        This is the main method that differentiates derived classes, and is probably the only method
        that will need to be overridden.

        @param port: the port on which the PyCmdDispatcher's backchannel instance is listening, usually
        passed as a parameter to the child_bootstrapper.py script which starts up the pyCmdExecutor
        inside child process started by the PyCmdDispatcher

        @type port: C{int}

        @return: Return a tuple of a list of args to start the python interpreter, and a list of
        python commands to initialize the python working environment.
        
        @rtype: C{tuple} C{([childArgs], [pyInitCmds])}
        
        @raise NotImplementedError: Raised when this method is not overridden in a derived class.
        """
        raise NotImplementedError

    def generateChildBootstrapper(self, port):
        """
        This is only overridden if a 3rd-party application which will be started cannot use the standard
        child_bootstrapper.py script.  This can happen if the 3rd-party app doesn't support passing
        arguments to the bootstrapper.

        @param port: the port on which the PyCmdDispatcher's backchannel instance is listening, usually
        passed as a parameter to the child_bootstrapper.py script which starts up the pyCmdExecutor
        inside child process started by the PyCmdDispatcher

        @type port: C{int}
        """
        return os.path.join(os.path.dirname(backendUtils.getModulePath()), 'child_bootstrapper.py')

    def initPyCmdDispatcher(self):
        """
        Initialize a PyCmdDispatcher instance.
        
        The PyCmdDispatcher is this side of the bi-directional communication with a python
        interpeter running in a child process.  It is the mechanism to dispatch the commands to the
        interpreter and handle any return values or exceptions.
        
        @return: Return a pythonChildHandler.PyCmdDispatcher object, which will have a running
        python process of some sort (python, mayaPy, houdini, etc.) as a child attribute
        
        @rtype: pythonChildHandler.PyCmdDispatcher
        """
        initReturnCode = 0
        cmdDispatcher = None
        if os.path.exists(self.pyExecutable):
            #============================================================
            # redirect stderr -> stdout if the job package dictates
            # - this defines the "stderr" value for the subprocess.Popen constructor
            #============================================================
            mergeStderr = self.job['package'].get('redirectStderrToStdout', False)

            # create the Dispatcher instance, but don't yet start the child subprocess
            cmdDispatcher = qb.backend.pythonChildHandler.PyCmdDispatcher(logHandler=self.logHandler,
                                                                          mergeStderr=mergeStderr)

            self.childBootstrapper = self.generateChildBootstrapper(cmdDispatcher.backChannel.port)

            # inform the subprocess args of the port the PyCmdDispatcher is listening on
            childArgs, initCmds = self.getSubprocessArgs(cmdDispatcher.backChannel.port)

            # now actually start up the application that's going to do the work.
            cmdDispatcher.startChild(childArgs)

            # pump the cmdDispatcher for the app startup messages, pass them through the logHandler
            cmdDispatcher.execute('print()', self.job)

            # Load up the minimal set of standard modules
            initReturnCode += cmdDispatcher.execute('import sys')
            initReturnCode += cmdDispatcher.execute('import os')
            initReturnCode += cmdDispatcher.execute('import time')
            
            for cmd in initCmds:
                initReturnCode += cmdDispatcher.execute(cmd, self.job)
        else:
            initReturnCode = 1
            msg = 'Startup application not found: %s' % self.pyExecutable
            print('ERROR: %s' % msg)
            self.logging.error(msg)

        return (cmdDispatcher, initReturnCode)

    def jobSetup(self):
        """
        Perform any steps necessary to initialize the working environment prior to beginning any
        agendaItem-specific steps.
        """
        super(PythonChildBackEnd, self).jobSetup()
    
        backendUtils.bannerPrint('Starting Python initialization')
        (self.cmdDispatcher, initReturnCode) = self.initPyCmdDispatcher()

        if initReturnCode > 0:
            backendUtils.bannerPrint('ERROR: Python initialization failed', fhList=[sys.stdout, sys.stderr])
            self.logging.error('Unable to start application session.')
            self.job['status'] = 'failed'
            qb.reportjob(self.job)

            try:
                backendUtils.bannerPrint('Shutting down python session', fhList=[sys.stdout, sys.stderr])
                self.cmdDispatcher.close()
            except TypeError:
                pass
            
            sys.exit(initReturnCode)
        else:
            backendUtils.bannerPrint('Finished Python initialization')
            #=============================================
            # optional jobSetup commands
            #=============================================
            cmdRetCode = 0
            if 'jobSetupCmds' in self.job['package'] and self.job['package']['jobSetupCmds']:
                # execute the setup commands in the job package
                backendUtils.bannerPrint('Starting job setup commands')
                for cmd in self.job['package']['jobSetupCmds']:
                    cmd = qb.utils.translateQbConvertPathStrings(cmd)
                    cmdRetCode = self.cmdDispatcher.execute(cmd, self.job)
                    
                    if cmdRetCode != 0:
                        sys.stdout.write('ERROR: unable to successfully execute command "%s"\n' % cmd)
                        sys.stdout.write('WARNING: reporting job instance as failed\n')
                        qb.reportjob('failed')
                        sys.exit(cmdRetCode)
                backendUtils.bannerPrint('Finished job setup commands')

    def executeWork(self):
        """
        Request an agendaItem (work) from the supervisor and do any steps necessary to perform the
        work.
        """
        while True:
            work_status = 1

            backendUtils.bannerPrint('Requesting work', fhList=[sys.stdout, sys.stderr])
            work = qb.requestwork()

            if self.dev:
                print("DEBUG BEGIN:")
                print("WORK:")
                pprint.pprint(work)
                print("DEBUG END:")
            
            # Deal with the minimal set of work statuses
            if work['status'] == "failed":
                # preflights failed, so skip this agenda item and mark it failed
                print('preflights for work [%s:%s] failed' % (self.job['id'], work['name']))
                work['status'] = 'failed'
                qb.reportwork(work)
                continue
            if work['status'] == 'complete':
                work_status = 0
                break
            elif work['status'] == 'pending':
                # preempted -- bail out
                print('job %s has been preempted' % self.job['id'])
                work_status = 0
                qb.reportjob('pending')
                break
            elif work['status'] == 'blocked':
                # blocked -- perhaps part of a dependency chain
                print('job %s has been blocked' % self.job['id'])
                work_status = 0
                qb.reportjob('blocked')
                break
            elif work['status'] == 'waiting':
                # waiting -- rare, come back in 30s
                print('job %s will be back in %s seconds' % (self.job['id'], self.QB_WAITING_TIMEOUT))
                sys.stdout.flush()
                for i in range(self.QB_WAITING_TIMEOUT*100):
                    time.sleep(0.01)
                continue

            # Dispatch the commands to the python running in the child process
            # one at a time.  If any of the commands fail, set the agenda item
            # as failed.  If the subprocess dies, set the job instance as failed,
            # and requeue the work.
            backendUtils.bannerPrint('Executing work package commands for work: %s' % work['name'], fhList=[sys.stdout, sys.stderr])
            wrkCmdRetCode = 0
            try:
                for cmd in work['package']['commands']:

                    # Do the actual work.
                    wrkCmdRetCode = self.cmdDispatcher.execute(cmd, work)
                    
                    if wrkCmdRetCode != 0:
                        work_status = wrkCmdRetCode
                        break

                    elif self.cmdDispatcher.child.returncode:
                        # if the child process has died, mark the job instance and the work as failed... 
                        sys.stderr.write('subprocess seems to have died...\n')
                        self.status = self.cmdDispatcher.child.returncode
                        work_status = self.status
                        break
                    
                    else:
                        work_status = 0

            except Exception:
                sys.stderr.write(tb.format_exc())
            backendUtils.bannerPrint('Finished work package commands for work: %s' % work['name'])

            if work.get('resultpackage') is None:
                work['resultpackage'] = {}
            # -----------------------------------------------------------
            # set the work status, then report it back to the supervisor
            # so that it can update the server-side agenda
            # -----------------------------------------------------------
            if work_status != 0:
                # either the work or the job instance itself has failed
                work['status'] = 'failed'
            elif self.outputPaths_required and len(work.get('resultpackage', {}).get('outputPaths', '')) == 0:
                work['status'] = 'failed'
                backendUtils.flushPrint('WARNING: no "regex_outputPaths" match was found, setting agenda item status to "failed".', fhList=[sys.stdout, sys.stderr])
            else:
                # mark the work as complete, and reset both the failure counter and timer
                work['status'] = 'complete'

            backendUtils.bannerPrint('Reporting work as %(status)s: %(name)s ' % work, fhList=[sys.stderr])
            qb.reportwork(work)

            # don't do another requestwork() if the job instance status != 0
            # - child process has crashed
            if self.status != 0:
                print('ERROR: The child python process (mayapy, houdini, etc) has exited prematurely.')
                print('INFO: Will attempt to restart this job instance on another host, if its job instance retry limit has not been exceeded.')
                break

    def jobTeardown(self):
        """
        Perform any steps necessary to clean up the working enviroment prior to shutting down the
        job instance.
        """
        if 'jobTeardownCmds' in self.job['package'] and self.job['package']['jobTeardownCmds']:
            self.cmdDispatcher.execute(self.job['package']['jobTeardownCmds'])

        retCode = self.cmdDispatcher.close(self.status)
        
        print('Python session exited with code %s' % retCode)

        if self.status == 0:
            qb.reportjob('complete')
        else:
            qb.reportjob('failed')
        
        sys.stderr.flush()

