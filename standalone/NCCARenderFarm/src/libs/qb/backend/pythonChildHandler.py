"""
    This module defines 2 tightly-coupled classes; PyCmdDispatcher and PyCmdExecutor, along with 3 other
    classes used as FIFO's, PfxUnixFIFO and PfxNamedPipeFIFO, which derive from PfxFIFO.

    They are used to spawn a python child process and send commands to that process.  The PyCmdDispatcher
    instance is the parent and dispatches commands to the child, which has a PyCmdExecutor instance.

    Commands are dispatched over the child's stdin.

    The success or failure of the PyCmdExecutor's ability to execute the command is communicated back to
    the PyCmdDispatcher over a FIFO-like object, which is an PfxFIFO instance.
"""
#======================================
#  $Revision: #3 $
#  $Change: 23201 $
#  $File: //depot/rel-7.5/qube/src/api/python/qb/backend/pythonChildHandler.py $
#======================================

import sys
import os
import time
import logging
import subprocess

import inspect
import traceback as tb

import socket
try:
    import socketserver
except ImportError:
    import SocketServer as socketserver
import threading
import xdrlib

from qb.utils import translateQbConvertPathStrings
from qb.backend.utils import PFXSimpleTimer, flushPrint


def getThisModulePath():
    frame = inspect.currentframe()
    thisModulePath = os.path.abspath(inspect.getfile(frame))
    jobtypeDir = os.path.dirname(thisModulePath)
    del frame
    return (thisModulePath, jobtypeDir)


# A global lock used to arbitrate access to the PFXSimpleServer buffer string - the PFXSimpleServer's
# requestHandler writes to the buffer, and the PyCmdDispatcher resets the buffer once it's read.
buffer_lock = threading.Lock()


class PyCmdDispatcher(object):
    """
    The PyCmdDispatcher class is used by qube python jobtypes to execute commands through an
    abstracted application or shell.

    The jobtype can have several sets of commands, defined as either a list of strings or a single
    string, for job setup, job teardown, and per-agendaItem commands.

    Command Execution
    =================
        Commands are sent as string to the child process via stdin.  The child is responsible for
        communicating the success/failure of the command over a FIFO-like object known as the backChannel.
        A successful command execution results in a zero being written to the backChannel by the
        child.  A non-zero indicates some sort of an error occurred attempting to execute the
        command.

        What Constitutes Command Failure
        --------------------------------
        In the case of a python child process, failure is defined as any command that raises an
        uncaught exception.  The traceback is passed as a string from the child to the parent to be
        printed to sys.stderr.

    @cvar BLOCKSIZE: Blocksize for reading from an i/o stream.
    @type BLOCKSIZE: int

    @cvar POLL_TIMEOUT: Timeout value in milliseconds for select.poll() objects.
    @type POLL_TIMEOUT: int

    @cvar CHILD_CHECK_INTERVAL: how long (in seconds) to sleep between checks to see if the child
    process is finsihed executing the command
    @type CHILD_CHECK_INTERVAL: C{int}

    @cvar LOG_PARSE_INTERVAL: how long (in seconds) to wait between parsing the logs for errors and
    other regex matches
    @type LOG_PARSE_INTERVAL: C{int}

    @ivar child: The running child process, which will contain a PyCmdExecutor instance.  
    @type child: U{subprocess.Popen<http://www.python.org/doc/2.5.2/lib/node532.html>}

    @ivar backChannel: The "out of band" pipe used to communicate success/failure from the
    PyCmdExecutor to the PyCmdDispatcher; distinct from the PyCmdExecutor's stdout/stderr, avoids
    having to parse the child's stdout/stderr for a sign that the last-sent command has completed
    executing.
    @type backChannel: L{PFXSimpleSocketServer}
    """
    CHILD_CHECK_INTERVAL = 0.2
    LOG_PARSE_INTERVAL = 5

    def __init__(self, logHandler=None, mergeStderr=False, debug=False):
        """
        init function to set up members of the class

        @param logHandler: a code object, it's the C{logHandler()} method of the backend class that's running the job
        that's instantiating this.

        @type logHandler: C{function}

        @param mergeStderr: whether to merge stderr->stdout

        @type mergeStderr: C{bool}
        """
        self.logging = logging.getLogger('%s' % self.__class__.__name__)

        loggingLevel = logging.INFO
        loggingFormat = logging.BASIC_FORMAT

        self.debug = debug
        if self.debug:
            loggingLevel  = logging.DEBUG
            loggingFormat = '%(name)20s : %(levelname)-8s : %(message)s (%(filename)s:%(lineno)d, %(threadName)s)'

            loggerHdlr = logging.StreamHandler(None)
            loggerHdlr.setFormatter(logging.Formatter(loggingFormat, None))
            self.logging.addHandler(loggerHdlr)

            self.logging.setLevel(loggingLevel)

        self.logHandler = logHandler
        self.mergeStderr = mergeStderr

        # startup the backChannel for out-of-band communication between this object and the child
        self.backChannel = self.__startupBackChannel()
        self.packer = xdrlib.Packer()
        self.simple_server_thread = None

        # a timer so that we only check the job logs every 5s or so
        self.timer = PFXSimpleTimer()

        # Start up the child which will instantiate a PyCmdExecutor object that we will talk to.
        self.child = None
        self.child_ready_for_cmd = False

    def __startupBackChannel(self):
        """
        Instantiate a L{PFXSimpleSocketServer} and start it in another thread
        """
        backChannel = PFXSimpleSocketServer()

        self.simple_server_thread = threading.Thread(target=backChannel.start, kwargs={'poll_interval': 0.1})
        self.simple_server_thread.setName('ChildHandlerBackChannel')
        self.simple_server_thread.setDaemon(True)
        self.simple_server_thread.start()

        while backChannel.port is None:
            self.logging.warning('looping waiting for backChannel SimpleServer to start')
            time.sleep(0.5)

        return backChannel

    def __send(self, msg):
        """
        Send a string to the child process's stdin.

        @param msg: string to send
        @type msg: C{string}
        
        @return: the message length, or -1 if the child is non-responsive
        @rtype: int
        """
        # ensure that the child is still alive
        if self.child.returncode is not None:
            self.logging.debug('child returncode is not None')
            return -1
        else:
            #=======================================================================================
            # Due to a Python2/Python3 Unicode incompatibility we can no longer encode an integer
            # greater than 127.  Now we break the int into chunks of 126 or less and add them up on
            # the other side.
            #
            # msglen of 127 means subtract 126 and send another chunk
            #=======================================================================================
            self.logging.debug('sending %s chars...' % len(msg))
            msglen = len(msg)
            while msglen > 126:
                msglen = msglen - 126
                self.packer.pack_int(127)
                msgLenPacked = self.packer.get_buffer()
                self.logging.debug('126 -> msgLenPacked: {}'.format(msgLenPacked))
                self.child.stdin.write(msgLenPacked)
                self.child.stdin.flush() # required each loop?
                self.packer.reset()
            self.packer.pack_int(msglen)
            msgLenPacked = self.packer.get_buffer()
            self.logging.debug('{} -> msgLenPacked: {}'.format(msglen, msgLenPacked))
            self.child.stdin.write(msgLenPacked)
            self.child.stdin.flush()
            self.packer.reset()
            self.logging.debug('sent %s in a packed format...' % len(msg))

            # now send the actual message
            self.logging.debug('sending msg: %s' % msg)
            self.child.stdin.write(msg.encode('utf-8'))
            self.logging.debug('sent msg: %s' % msg)
            self.child.stdin.flush()
            self.packer.reset()
            self.logging.debug('reset XDRLib packer')

            return len(msg)

    def __getBackChannelBuffer(self):
        """
        Read the first 4 bytes from the PFXSimpleServer's buffer; the first 4 bytes which are
        expected to contain the payload length as an integer in a packed format.  Retrieve the
        message

        @return: The message length and the message, message length is -1 if the pipe has closed.
        @rtype: C{tuple}
        """
        (msgLenPacked, msg) = self.backChannel.buffer

        if len(msgLenPacked) == 4:
            unpacker = xdrlib.Unpacker(msgLenPacked)
            msgLen = unpacker.unpack_int()
        else:
            # indicate that the pipe has closed
            msgLen = -1

        # reset the buffer
        buffer_lock.acquire()
        self.backChannel.buffer = ()
        buffer_lock.release()

        return msgLen, msg

    def startChild(self, subprocessArgs):
        """
        Start up a child process, which will actually do the work for the job.

        @param subprocessArgs: arg is a 3-element array, suitable for passing as the first parameter
        to U{subprocess.Popen<http://www.python.org/doc/2.5.2/lib/node528.html>}.

            1. full path the the shell eg:'/bin/tcsh'
            2. '-c'
            3. the entire command to run to launch the child process, as a single string

        @type subprocessArgs: list
        """
        def __printChildArgs():
            flushPrint('Subprocess initialization command:')
            flushPrint('%s' % '-'*50)
            if sys.platform == 'win32':
                flushPrint(subprocessArgs[0])
            else:
                flushPrint('%s %s' % tuple(subprocessArgs[0:2]))
                for x in subprocessArgs[2].split('; '):
                    flushPrint('%s%s' % (' '*4, x))
            flushPrint('%s' % '-'*50)

        __printChildArgs()

        #============================================================
        # redirect stderr -> stdout if desired, set at job submission
        #============================================================
        childStderr = None
        if self.mergeStderr:
            childStderr = subprocess.STDOUT

        if os.name == 'nt':
            childArgs = ''.join(subprocessArgs)
        else:
            childArgs = subprocessArgs

        ON_POSIX = 'posix' in sys.builtin_module_names

        self.child = subprocess.Popen(childArgs,
                                      stdin=subprocess.PIPE,
                                      stderr=childStderr,
                                      close_fds=ON_POSIX,
                                      env=os.environ)

        self.logging.debug('child started')
        self.logging.debug('child pid: %s' % self.child.pid)
        self.child_ready_for_cmd = True
        self.timer.startTimer()

    def execute(self, commands, work=None):
        """
        Pass the commands in a list to a child process one by one for execution by C{eval}.

        @param commands: A list (optionally a string for a single command) of commands to be
        executed by a child process.  If commands is a string, it will be re-cast as
        a single-element list. 

        @type commands: list

        The following two forms yield identical results::

            >>> cmds = ['import sys', 'print sys.version_info' ]
            >>> execute(cmds)

            >>> execute('import sys')
            >>> execute('print sys.version_info')

        @return: 0 for success, 1 for failure.
        @rtype: C{int}
        """
        if isinstance(commands, str):
            commands = [commands]

        self.logging.debug('commands: %s' % commands.__repr__())
        return_code = 0
        error_regex_matched = False
        file_size_check_failed = False

        #=======================================
        # setup to parse the logs
        #=======================================
        if not self.timer.timerIsRunning:
            self.timer.startTimer()

        while self.child.returncode is None and not (error_regex_matched or file_size_check_failed):
            if self.child_ready_for_cmd:
                # send the child the next command
                try:
                    cmd = commands.pop(0)
                    self.logging.debug('cmd: "%s"' % cmd)
                    cmd = translateQbConvertPathStrings(cmd)
                    self.logging.debug('cmd - post-Xlate: "%s"' % cmd)
                except IndexError:
                    break

                send_result = self.__send(cmd)
                if send_result > -1:
                    # this will be set True again when the child returns something on the backChannel
                    self.child_ready_for_cmd = False
                else:
                    self.logging.warning('child process seems to have died\n')
                    sys.stdout.write('child process seems to have died\n')
                    return_code = 1
                    break

            if len(self.backChannel.buffer) == 2:
                #===================================================================================
                # once the child executes the command and the command returns, this buffer will hold
                # a tuple of payloadSize and an optional message - the child returns a zero-length
                # message if the command executed does not raise an exception; if it does, the
                # message is the traceback itself
                #===================================================================================

                # the child responded, it's ready for the next command to be sent
                self.child_ready_for_cmd = True

                # get the payload size from the backChannel
                (msgLen, msg) = self.__getBackChannelBuffer()

                #===================================================================================
                #    a 0-length msg == successful command execution
                #===================================================================================
                # now deal with any message that was not zero bytes long,
                if msgLen != 0:  # an unnecessary conditional, added for visual clarity
                    if msgLen > 0:
                        #===========================================================================
                        # a non-zero msgLen indicates that a message has been passed back up from
                        # the child on the back-channel
                        #
                        # this only happens when there's been an error executing a command,the msg
                        # is the string representation of the traceback.
                        #===========================================================================
                        return_code = 1
                        flushPrint(msg, fhList=[sys.stderr])
                        break
                    elif msgLen < 0:
                        self.logging.debug('msgLen < 0')
                        self.logging.error('backChannel closed unexpectedly')
                        return_code = 1
                        break

            # parse any new data written to the job logs for errors, highlights, etc...
            if self.timer.elapsedTime() > self.LOG_PARSE_INTERVAL and self.logHandler:
                (error_regex_matched, file_size_check_failed) = self.logHandler(work)

                if (error_regex_matched or file_size_check_failed):
                    self.logging.warning('error_regex matched or file size check failed...')
                    break
                
                self.timer.startTimer()

            for fh in [sys.stdout, sys.stderr]:
                fh.flush()

            time.sleep(self.CHILD_CHECK_INTERVAL)

            # check to see if the cmd just executed shut down the child
            if self.child.poll():
                break

        if commands and (commands[0].count('sys.exit(0)') == 0):
            return_code = 1
            sys.stderr.write('%s' % '-'*60 + '\n')
            sys.stderr.write('ERROR: from %s.execute()\n' % self.__class__.__name__)
            sys.stderr.write('\tChild process has exited prematurely with commands remaining\n')
            sys.stderr.write('\tReturning a code of %i, indicating failure\n' % self.child.wait())
            sys.stderr.write('%s' % '-'*60 + '\n')
            sys.stderr.flush()

        # now check the job logs one last time
        if self.logHandler and not (error_regex_matched or file_size_check_failed):
            (error_regex_matched, file_size_check_failed) = self.logHandler(work)
            if (error_regex_matched or file_size_check_failed):
                self.logging.warning('error_regex matched or file size check failed...')

        if error_regex_matched or file_size_check_failed:
            return_code = 1

        return return_code

    def close(self, exitcode=0):
        """
        Signal the child process to shut down.

        @param exitcode: Suggested exit code of the child process.
        @type exitcode: int

        @return: Actual value the child exited with.
        @rtype: int
        """
        if not self.child.returncode:
            self.execute('sys.exit(%i)' % exitcode)
        else:
            sys.stderr.write('ERROR: from %s.close()\n' % self.__class__.__name__)
            sys.stderr.write('\tUnable to close child process, it seems to already be closed\n')

        # shut down the PFXSimpleServer
        self.backChannel.stop()

        if self.simple_server_thread:
            self.simple_server_thread.join(2.0)

        return self.child.wait()
    

class PyCmdExecutor(object):
    """
    The PyCmdExecutor class is used by qube loadOnce python jobtypes.  It is tightly coupled to the
    PyCmdDispatcher class; the 2 classes are server/client relations.

    A PyCmdExecutor object is instantiated by the child process and is responsible for executing
    commands sent from the PyCmdDispatcher over stdin.  It is normally instantiated inside a child
    bootstrapper script.

    Initialize 2 empty dicts to serve as the locals() and globals() for the C{exec} statement used
    to execute the command.

    B{Note}: The definition of failure is not a boolean result of the command executed, it is the
    inability of the PyCmdExecutor object to actually execute the command without raising an
    exception.
    """

    def __init__(self, buffer_port, promptType=None, debug=False):
        """
        Function to set up members of the class.
        
        @param buffer_port: The port on which a PFXSimpleServer instance is running on the localhost,
        used as a backChannel for communication between this instance and the pyCmdDispatcher
        instance sending it commands to be executed.

        @type buffer_port: C{int}

        @param promptType: Used to determine the string used as a prompt that precedes the command
        when echoing the command to stdout.

        @type promptType: C{str}
        """
        self.logging = logging.getLogger('%s' % self.__class__.__name__)

        loggingLevel = logging.WARNING
        loggingFormat = logging.BASIC_FORMAT
        
        if debug:
            loggingLevel  = logging.DEBUG
            loggingFormat = '%(name)20s : %(levelname)-8s : %(message)s (%(filename)s:%(lineno)d, %(threadName)s)'

        loggerHdlr = logging.StreamHandler(None)
        loggerHdlr.setFormatter(logging.Formatter(loggingFormat, None))

        self.logging.addHandler(loggerHdlr)
        self.logging.setLevel(loggingLevel)

        self.backChannel = PFXSimpleClient(int(buffer_port))

        self.exitCode = 0
        self.packer = xdrlib.Packer()
        self.ZERO_PACKED = self.__initPacker()

        self.globals = {}
        self.locals = {}

        self.cmdPrompt = self.__getCommandPrompt(promptType)

    def __initPacker(self):
        """
        Initialize an U{xdrlib.Packer<p://www.python.org/doc/2.5.2/lib/xdr-packer-objects.html>}
        instance for internal use by the class member.

        The packer instance is accessed via the self.packer attribute.

        @return: the integer 0 packed into 4 bytes.  This is the data most commonly sent back to the
        PyCmdDispatcher parent, so it's packed once and re-used.

        @rtype: C{str}
        """
        self.packer.pack_int(0)
        ZERO_PACKED = self.packer.get_buffer()
        self.packer.reset()

        return ZERO_PACKED

    def __getCommandPrompt(self, promptType='>>'):
        """
        Determine the string that is printed prior to echoing out to stdout the command about to be run.

        @return: The string to be used as a command prompt.

        @rtype: str
        """
        prompt = {
            'maya': 'mayaPy>',
            'houdini': 'houdiniPy>',
            'nuke': 'nukePy>',
        }
        
        return prompt.get(promptType, '%s>' % promptType)

    def _send(self, msg):
        """
        Write a message via a PFXSimpleClient to the pyCmdDispatcher sending this instance commands.

        Successful execution results in the integer 0, packed into 4 bytes, being sent with no other
        message behind it.  Failure, defined as any command which raises an uncaught exception,
        results in the traceback from the exception being sent, preceded by the packed messageLength.

        @param msg: The message to be sent, prepended with the payload size packed into 4 bytes.

        @type msg: C{string}
        """

        if msg == self.ZERO_PACKED:
            self.backChannel.send(msg)
            self.logging.debug('sent: ZERO_PACKED = %s' % self.ZERO_PACKED.__repr__())
        else:
            self.logging.debug('sending msg: %s' % msg)
            self.packer.pack_int(len(msg))
            msgLenPacked = self.packer.get_buffer()
            self.packer.reset()

            sent = 0
            while sent < len(msg):
                sent = self.backChannel.send(msg[sent:])

            self.logging.debug('bytes sent: %s' % sent)

    def execute(self, cmd):
        """
        C{exec} a string as a python command.

        Most exceptions raised by the failure of C{exec} will be caught and handled by
        L{PyCmdExecutor.mainloop}. The only exception caught here will be SystemExit.

        @param cmd: The command to be run.
        @type cmd: C{string}

        @return: C{None} on success or the exitcode passed to sys.exit()

        @rtype: NoneType or int
        """

        sys.stdout.write('%s %s\n' % (self.cmdPrompt, cmd))
        if hasattr(sys.stdout, 'flush'):
            sys.stdout.flush()

        try:
            exec(cmd, self.globals, self.locals)
            #=================================================================
            # definition of successful execution == no exception
            # send an int 0, which the Dispatcher will interpret as success
            #=================================================================
            self._send(self.ZERO_PACKED)
            return None

        except SystemExit as exitValue:
            self.logging.debug('SystemExit, returncode:%s' % exitValue)
            return exitValue

    def mainloop(self):
        """
        Main loop of the PyCmdExecutor.  Responsible solely for reading commands to execute over
        stdin.

        Successful execution results in a zero integer being passed back to the the PyCmdDispatcher
        via the PFXClient instance (the backChannel).  Unsuccessful commands result in an error
        message of some sort being returned via the backChannel.

        The traceback generated by the failure to execute the command is what gets written to the
        backChannel.

        @return: The exit code of the child process

        @rtype: int
        """

        while True:
            #=======================================================================================
            # Read a command over stdin.
            #
            # The commands are preceded by a 4-byte packed integer which describes the length of the
            # string to follow.
            #
            # The string is the command(s) to be executed.
            #=======================================================================================

            #=======================================================================================
            # Due to a Python2/Python3 Unicode incompatibility we can no longer encode an integer
            # greater than 127.  Now we break the int into chunks of 126 or less and add them up on
            # the other side.
            #
            # msglen of 127 means add 126 and take another chunk
            #=======================================================================================
            unpacker = xdrlib.Unpacker(sys.stdin.read(4).encode('utf-8'))
            val = unpacker.unpack_int()
            msglen = val
            unpacker.reset('')
            while val > 126:
                unpacker = xdrlib.Unpacker(sys.stdin.read(4).encode('utf-8'))
                val = unpacker.unpack_int() - 1
                msglen += val
                unpacker.reset('')
            cmd = sys.stdin.read(msglen)
            unpacker.reset('')

            try:
                self.logging.debug('executing: %s' % cmd)
                result = self.execute(cmd)
                self.logging.debug('result: %s' % result)
                if result is not None:
                    # if we're here, the command was sys.exit()
                    self.exitCode = result.code
                    break
            except Exception:
                # some sort of exception has occurred, 
                # so send the traceback up to the parent
                tback = '%s' % '-'*80 + '\n'
                try:
                    tback += '  ERROR: %s\n' % cmd.__str__()
                    tback += '%s' % '-'*80 + '\n'
                except Exception:
                    pass
                tback += tb.format_exc()
                tback += '%s' % '-'*80 + '\n'
                self._send(tback)

        return self.exitCode


class PFXRequestHandler(socketserver.BaseRequestHandler):
    """
    """
    def __init__(self, request, client_address, server):
        self.logging = logging.getLogger(self.__class__.__name__)
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def handle(self):
        """
        Each request is expected to have the payload size packed by xdrlib.Packer encoded in the first
        4 bytes, optionally followed by a message.
        """
        payloadSize = self.request.recv(4)
        while len(payloadSize) < 4:
            payloadSize = self.request.recv(4-len(payloadSize))

        self.logging.debug('payloadSize: %s' % payloadSize.__repr__())

        if len(payloadSize) == 4:
            unpacker = xdrlib.Unpacker(payloadSize)
            msgLen = unpacker.unpack_int()
            unpacker.reset('')
            self.logging.debug('recvd: %s' % msgLen)
        else:
            raise Exception

        msg = ''
        while len(msg) < msgLen:
            msg = msg + self.request.recv(msgLen - len(msg))

        if len(msg):
            self.logging.debug('MSG: %s' % msg)

        buffer_lock.acquire()
        self.server.buffer = (payloadSize, msg)
        buffer_lock.release()


class PFXSimpleSocketServer(socketserver.TCPServer):
    """
    Listens for output from PFXSimpleClient on the same host, usually running in another python
    interpreter inside a 3rd-party application such as Maya.

    Uses a port auto-assigned by the OS if possible, doesn't seem to be available on python 2.4
    running on CentOS 5.x, otherwise use a port in the range 55000-56000

    @ivar buffer:  The requestHandler class will store any received messages as a tuple in the
    instance's buffer attribute; the tuple will contain the message length as a packed integer,
    and the message itself.

    @type buffer: C{tuple}
    """

    # only used for IPC on the same host
    # port 0 allows the OS to auto-assign the next available port
    SERVER_ADDRESS = ('127.0.0.1', 0)

    if sys.version_info[1] < 6:
        import random
        SERVER_ADDRESS = (SERVER_ADDRESS[0], 55000 + random.randrange(1, 1000))

    def __init__(self, handlerClass=PFXRequestHandler, timeout=1):
        socketserver.TCPServer.__init__(self, self.SERVER_ADDRESS, handlerClass)
        self.port = self.server_address[1]
        self.logging = logging.getLogger(' %s @ %i' % (self.__class__.__name__, self.port))

        self.buffer = tuple()

    def start(self, **kwargs):
        self.logging.debug('Starting mainloop')
        self.logging.debug(sys.version_info.__repr__())
        if sys.version_info[1] < 6:
            if kwargs:
                self.logging.warning('SocketServer.BaseServer.serve_forever takes no args in python versions < 2.6')
                self.logging.warning('Skipping args: %s' % list(kwargs.keys()))
            self.logging.debug('Starting serve_forever')
            self.serve_forever()
        else:
            self.logging.debug('Starting serve_forever with kwargs: %s' % kwargs.__repr__())
            self.serve_forever(**kwargs)

    def stop(self):
        if hasattr(self, 'shutdown'):
            # no shutdown() in SocketServer from python 2.4
            self.shutdown()
        self.server_close()


class PFXSimpleClient(object):
    """
    """
    def __init__(self, server_port):
        self.logging = logging.getLogger(self.__class__.__name__)

        self.server_address = ('127.0.0.1', server_port)
        self.logging.debug('server address: %s' % self.server_address.__repr__())

        self.packer = xdrlib.Packer()
        self.ZERO_PACKED = self.__initPacker()

    def __initPacker(self):
        """
        Initialize an U{xdrlib.Packer<p://www.python.org/doc/2.5.2/lib/xdr-packer-objects.html>}
        object for internal use by the class member.

        The packer object is accessed via the self.packer attribute.

        @return: the integer 0 packed into 4 bytes.  This is the data most commonly sent back to the
        PyCmdDispatcher parent, so it's packed once and re-used.

        @rtype: C{str}
        """
        self.packer.pack_int(0)
        ZERO_PACKED = self.packer.get_buffer()
        self.packer.reset()

        return ZERO_PACKED

    def send(self, msg):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.connect(self.server_address)

        if msg == self.ZERO_PACKED:
            sent = skt.send(msg)
        else:
            self.packer.pack_int(len(msg))
            msgLenPacked = self.packer.get_buffer()
            self.packer.reset()

            skt.send(msgLenPacked)

            sent = 0
            while sent < len(msg):
                sent += skt.send(msg[sent:])

            self.logging.debug('sent: %s' % sent)

        skt.close()

        return sent

if False: # __name__ == '__main__': #or os.environ.get('PFX_DEV'):
    logging.basicConfig(level=logging.INFO)
    thisDir = getThisModulePath()[1]

    childBootStrapper = os.path.join(thisDir, 'child_bootstrapper.py')
    pyCmdLine = '%s -u "%s" --port __PORT__' % (sys.executable, os.path.normpath(childBootStrapper))

    if sys.platform == 'win32':
        childArgs = [pyCmdLine]
    else:
        childArgs = ['/bin/tcsh', '-c', pyCmdLine]
    cd = PyCmdDispatcher(childArgs, debug=False)

    cd.execute('print "Hello World"')
    cd.execute('import sys')
    cd.execute('import os')
    cd.execute('print "%s" % "+"*16*1024')
    cd.execute('print "that was a 16K string, check the length.."')
    cd.execute(('1/0'))
    cd.execute("""import time
for i in range(10):
    print 'sleeping, %s' % i
    time.sleep(1)""")
    cd.execute('pid = os.getpid()')
    cd.execute('pgid = os.getpgid(pid)')
    cd.execute('print "from child - pgid:%s" % pgid')

    try:
        print('__main__: Parent pid: %s' % os.getpid())
        print('__main__: Child pid: %s' % cd.child.pid)
        if hasattr(os, 'getpgid'):
            print('__main__: Child pgrp: %s' % os.getpgid(cd.child.pid))
    except:
        print('child process died')

    exit_code = cd.close()
    logging.info('PyCmdDispatcher closed with exitCode: %s' % exit_code)
    sys.exit(exit_code)
