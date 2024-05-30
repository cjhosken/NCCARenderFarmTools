#!/bin/env python
"""
A package for easily defining various Qube front ends
"""
#======================================
#  $Revision: #1 $
#  $Change: 22715 $
#======================================



class QubeJobError(Exception):
    """Base class for all exceptions raised by any of the Qube job frontends"""
    def __init__(self, value=''):
        self.value = value
    def __str__(self):
       return repr(self.value)
 

class QubeJob(dict):
    """
    A base class for the frontend of any Qube job whose backend jobtype uses the qube
    qb.backend.pythonBackEnd modules
    """
    def __init__(self, prototype='', dev=False):
        """
        @param dev: Set the 'dev' value for the Qube job, enables debug output on the farm.
        @type dev: bool
        """
        self['prototype'] = prototype
        self['name'] = ''

        self['package'] = {
            'dev': dev,
            'smartAgenda': False,
            'logParser': {
                'className': 'LogParser',
                'modulePath': 'qb.backend.logParser',
                'libPath': ''
            },
            'regex_errors': 'QubeBackEndError|AppVersionNotFoundError',
        }

        self['callbacks'] = []

    def setLogParser(self, className, modulePath='qb.backend.logParser', libPath=''):
        """
        Define the logParser class to use.

        @param className: the class name of the LogParser to use
        @type className: C{str}

        @param modulePath: the string would normally be in the "import" line
        @type modulePath: C{str}

        @libPath: the absolute filepath to be added to PYTHONPATH (sys.path).  This is not the file
        path to the module itself, but only what needs to be added to the sys.path in order for the
        import command with the modulePath to be effective.  In the default case of the modulePath
        being "qb.logParser", we only wish to add the parent directory of the qb module itself, so
        that "import qb.logParser" will find and correctly load the required module.

        @type libPath: C{str}

        """
        self['package']['logParser'] = {
            'className': className,
            'modulePath': modulePath,
            'libPath': libPath
        }
    
