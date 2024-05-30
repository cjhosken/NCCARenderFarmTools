#!/bin/env python
"""
  A Python childHandler bootstrapper

  Starts a PyCmdExecutor instance, which is a running python interpreter whose stdin/stdout/stderr
  are hooked up to a subprocess.POpen() object that is running in a PyCmdDispatcher somewhere.
"""

#======================================
#  $Revision: #1 $
#  $Change: 22715 $
#======================================

import sys
from optparse import OptionParser
import os
import logging

apiPath = '%s/api/python' % os.environ.get('QBDIR',
                                           {'linux2': '/usr/local/pfx/qube',
                                            'darwin': '/Applications/pfx/qube',
                                            'win32': 'C:/Program Files/pfx/qube'}[sys.platform])
sys.path.insert(0, apiPath)
import qb.backend.pythonChildHandler


def parse_args():
    parser = OptionParser()
    parser.set_defaults(debug=False, kind='generic')

    parser.add_option('-p', '--port',
                        type=int,
                        help='port on which a PFXSimpleServer is running')

    parser.add_option('-k', '--kind',
                        help='short name of the application to be started, used for building the '
                             'python prompt')

    parser.add_option('-d', '--debug',
                        action='store_true')

    (opts, args) = parser.parse_args()

    return opts


def main(opts):

    logging.debug('childboot_strapper - port: %s' % opts.port)

    executor = qb.backend.pythonChildHandler.PyCmdExecutor(opts.port, promptType=opts.kind, debug=opts.debug)
    exit_code = executor.mainloop()

    del executor

    sys.stdout.write('child_bootstrapper: child process quit, exit code = %s\n' % exit_code)

    return exit_code


logging.basicConfig(level=logging.INFO)

opts = parse_args()
exit_code = main(opts)
sys.exit(exit_code)


