#!/bin/env python
'''
A base class for any job that uses the qube qb.backend.pythonChildBackEnd modules
'''
#======================================
#  $Revision: #2 $
#  $Change: 22906 $
#======================================

import sys
import os
import logging

try:
    import qb
except:
    if 'QBDIR' in os.environ:
        QBDIR = os.environ['QBDIR']
    else:
        if os.name == 'posix':
            if os.uname()[0] == 'Darwin':
                QBDIR = '/Applications/pfx/qube'
            else:
                QBDIR = '/usr/local/pfx/qube'

    sys.path.append('%s/api/python' % QBDIR)
    import qb
        

try:
    from qb import frontend
except ImportError:
    from AppUI import frontend


class PythonChildJob(frontend.QubeJob):
    def __init__(self, prototype='', dev=False):
        '''
        @param dev: Set the 'dev' value for the Qube job, enables debug output on the farm.
        @type dev: bool
        '''
        super(PythonChildJob, self).__init__(prototype=prototype)

        pkg = self['package']

        pkg['dev'] = dev

        pkg['jobSetupCmds'] = []
        pkg['jobTeardownCmds'] = []

        pkg['pyExecutable'] = ''
    
    def addJobCmds(self, cmds=None, cmdType='setup'):
        '''
        Add commands to the job that will be run once every time a worker is
        started up or shut down.

        @param cmds: The list of cmds to run.
        @type cmds: list

        @param cmdType: Specify where the commands are run before or after
        the worker requests agenda items (work) from the supervisor.
           - B{setup} commands are run before any work is performed, and can
             be used to set up the job's work environment, load a file, create
             temp dirs, etc.
           - B{teardown} commands are run after all work has been processed.
             Common uses may be to clean up temp dirs, etc.
        @type cmdType: str

        @raise TypeError: Raised when an unknown value is passed in for cmdType parameter.
        '''
        if not cmds:
            cmds = []
        
        if cmdType not in ['setup', 'teardown']:
            raise TypeError('Unknown command type: {}'.format(cmdType))

        if isinstance(cmds, str):
            cmds = [cmds]
        
        self['package']['job%sCmds' % cmdType.capitalize()].extend(cmds)

        return []
