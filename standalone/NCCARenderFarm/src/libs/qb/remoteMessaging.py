'''
A framework for socket-based client/server persistent remote messaging sessions.

Neither the server nor the client are bi-directional.  Each is intended to either receive messages
(the server) or send messages (the client).

The server functions as the receiver; it is multi-threaded and can receive from any number of
clients simultaneously.  The message content is not limited to strings.  It is possible to send
anything that can be serialzed, including traceback objects, classes, class instances, or code
objects.  Child threads of the main thread are created as needed to handle inbound messages, and are
shut down as soon as the message is deemed to have been received in full.  The message length is
sent in the first 4 bytes of the message; in this way, the message is not deemed to be completely
received until the number of bytes received matches the payload size.  This provides robustness on
congested or noisy networks that do not provide reliable transport.

The client functions as the sender.  It is single threaded and can communicate with only 1 server.
The server's INET socket address (ip address & port number) is an argument to the client's constructor
method.

Main concepts:
    
    * The central host in a messaging session communicates with multiple remote hosts.
    * Each remote host in a messaging session communicates with only 1 central host.
    * The central host runs 1 instance of a server.
    * Each remote host runs 1 instance of a client as well as 1 instance of a server.
    * The central host runs a client instance for each remote host.

Port assignment for the server in python versions 2.5 and above is dynamically assigned by the
kernel, and will be different for each instance.  In python versions 2.4 and below, the server port
is randomly assigned a port between 45000 and 60000. It is the responsibility of the developer to
inform the app instantiating the client of the server's host/port socket address.
    
The creation of a persistent messaging session between a local and remote host is a 4-step process:

    1.) create a server on a local host.  The INET socket address (ip & port) of the server is used when
    the clients are started up on remote machines.  This server instance running on the local host
    is the 'central' server and is expected to have sessions with clients on multiple remote hosts.

    2.) create a server on the remote host.
    
    3.) create a client on the remote host, passing the socket address of the 'central' server to
    the constructor. Send a 'hello' message back to the 'central' server informing it of the socket
    address on the server running on the same machine as the client (the "remote" host from the POV
    of the "central server).

    4.) when the 'central' server running on the local host receives the 'hello' message from the
    remote host, it creates a corresponding client for the server running on the remote host, using
    the socket address of the server running on the remote machine.  Since the local host is
    expected to have messaging sessions with multiple remote hosts, the client which is associated
    with the server on the remote host is stored in a dictionary so that it may be easily accessed
    at a later time.

Communication from a remote host back to the central host is accomplished by using the remote client
to send a message back to the central server.

Communcation from the central server to a remote host is accomplished by looking up the client which
corresponds to the remote host and using that client to send messages.

The app which utilizes the server and clients are meant to implement a heartbeat scheme such that the
server periodically sends heartbeats to the clients; if the clients do not receive heartbeats within
some interval past the timeout, they shut themselves down.

The app on the remote machine should also be written so that it inspects each message sent to the
server instance running on that machine, and if it receives a 'shutdown' message, will shutdown the
client and server and exit.
'''
#======================================
#  $Revision: #1 $
#  $Change: 22715 $
#======================================

import sys
import os
import time
import socket
import logging
import logging.handlers
import pickle
import socketserver
import struct
import threading

# Provide a method of finding the IP address bound to a NIC, even when the hostname resolves to the
# loopback addr when the host looks up itself.  This only works on linux, but linux is the only OS
# that typically exhibits this loopback behavior.
if os.name != 'nt':
    import fcntl
    import struct
    def getInterfaceIP(ifName):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifName[:15])
        )[20:24])

    
def getLanIP():
    # handle cases on some linux where gethostbyname returns loopback addr
    ip = socket.gethostbyname(socket.gethostname())

    if ip.startswith("127.") and os.name != "nt":
        for ifName in ["eth0","eth1","eth2"]:
            try:
                ip = getInterfaceIP(ifName)
                break
            except IOError:
                pass
    
    return ip

def pyVer():
    return float('%s.%s' % (sys.version_info[0], sys.version_info[1]))


class RemoteMessagingError(Exception):
    def __init__(self, value=''):
        self.value = value
    
    def __str__(self):
        return repr(self.value)


class RemoteMessagingStreamRequestHandler(socketserver.StreamRequestHandler):
    """
    Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    
    G{classtree RemoteMessagingStreamRequestHandler}
    """
    def handle(self):
        """
        Handle multiple requests - each expected to be encode the payload size in the first 4-bytes,
        followed by the LogRecord in pickle format. Logs the record according to whatever policy is
        configured locally.
        """
        while True:
            payloadSize = self.connection.recv(4)
            if len(payloadSize) < 4:
                # TODO: handle the case when the client can't even receive 4 bytes
                break
            
            msgLen = struct.unpack(">L", payloadSize)[0]
            msg = self.connection.recv(msgLen)
            while len(msg) < msgLen:
                msg = msg + self.connection.recv(msgLen - len(msg))
            
            obj = pickle.loads(msg)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def handleLogRecord(self, record):
        '''
        Pass a LogRecord to the appropriate logging.Handler.
        
        @param record: The logRecord received over the socket.
        @type record: logging.LogRecord
        '''
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            logger = logging.getLogger(self.server.logname)
        else:
            logger = logging.getLogger(record.name)
            if not logger.handlers:
                logger.setLevel(logging.INFO)
                logger.addHandler(logging.StreamHandler(sys.stdout))
        
        logger.handle(record)


class RemoteMessagingReceiver(socketserver.ThreadingTCPServer):
    """
    A simple TCP socket-based logging receiver.
    
    G{classtree RemoteMessagingReceiver}
    """
    allow_reuse_address = 1
    def __init__(self,
            host='localhost', 
            port=logging.handlers.DEFAULT_TCP_LOGGING_PORT, 
            loggerName=None, 
            handler=RemoteMessagingStreamRequestHandler):
        '''
        @param host: The name of the host running the socket server.
        @type host: C{str}
        
        @param port: The port number for the INET socket on the listening host.
        @type port: C{int}
        
        @param loggerName: The name of the logging.Logger object which is to 
        receive the logRecords sent over the socket. 
        @type loggerName: C{str} 
        
        @param handler: The request handler for the SocketServer
        @type handler: L{RemoteMessagingStreamRequestHandler}
        '''
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = False
        self.timeout = 3
        self.logname = loggerName

    def serveUntilStopped(self):
        '''
        Handle incoming requests until told to shut down.
        '''
        import select
        while not self.abort:
            rd = select.select([self.socket.fileno()], [], [], self.timeout)[0]
            if rd:
                self.handle_request()

            
class RemoteMessagingServer(object):
    '''
    Create and manage a logger running in a thread.
    
    G{classtree RemoteMessagingServer}
    '''
    if pyVer() > 2.4:
        DEFAULT_LOGGER_PORT = 0  # let the kernel assign the port dynamically, doesn't work in 2.4 or below
    else:
        import random
        DEFAULT_LOGGER_PORT = random.randint(45000,60000)

    loggerIP = getLanIP()

    THREADNAME = 'remoteMessagingServerMainThead'
    
    def __init__(self, verbose=False, port=None):
        '''
        Create a logging object and L{RemoteMessagingReceiver} which will send logRecords to it.
        
        @param verbose: Print out open/close messages or not
        @type verbose: C{bool}
        '''
        self.serverThread = None
        self.receiver = None

        if port:
            self.loggerPort = port
        else:
            self.loggerPort = self.DEFAULT_LOGGER_PORT
            
        self.verbose = verbose

    def getServerAddr(self):
        '''
        @return: Return the IP address and port number of the host running the socket server.
        @rtype: C{tuple} (ip, port)
        '''
        return self.receiver.server_address
    serverAddress = property(getServerAddr)

    def getServerIP(self):
        '''
        @return: Return the IP address of the host running the socket server.
        @rtype: C{str} An IP address in dotted notation: n.n.n.n
        '''
        return self.receiver.server_address[0]
    serverIP = property(getServerIP)

    def getServerPort(self):
        '''
        @return: Return the port number of the host running the socket server.
        @rtype: C{int} A port number for an INET socket. 
        '''
        return self.receiver.server_address[1]
    serverPort =  property(getServerPort)
    
    def start(self):
        '''
        Start the socket server in a thread.
        '''
        self.receiver = RemoteMessagingReceiver(host=self.loggerIP, port=self.loggerPort)
        if self.verbose:
            print('\n%s: started on %s:%s\n' % (self.__class__.__name__, self.serverIP, self.serverPort))

        self.serverThread = threading.Thread(target=self.receiver.serveUntilStopped, name=self.THREADNAME)
        self.serverThread.setDaemon(True)
        self.serverThread.start()

    def stop(self):
        '''
        Shut down the socket server
        '''
        self.receiver.abort = True
        # give the server time to loop once more through the select() loop in serveUntilStopped()
        time.sleep(self.receiver.timeout + 0.1)

        self.receiver.server_close()
        # wait for all the threads from the server to finish up
        self.serverThread.join()
        
        if self.verbose:
            print('%s: server shut down at %s:%s' % (self.__class__.__name__, self.serverIP, self.serverPort))
        

class RemoteMessagingSocketHandler(logging.handlers.SocketHandler):
    def send(self, s):
        """
        Send a pickled string to the socket.

        This function allows for partial sends which can happen when the
        network is busy.
        """
        if self.sock is None:
            self.createSocket()
        #self.sock can be None either because we haven't reached the retry
        #time yet, or because we have reached the retry time and retried,
        #but are still unable to connect.
        if self.sock:
            try:
                if hasattr(self.sock, "sendall"):
                    self.sock.sendall(s)
                else:
                    sentsofar = 0
                    left = len(s)
                    while left > 0:
                        sent = self.sock.send(s[sentsofar:])
                        sentsofar = sentsofar + sent
                        left = left - sent
            except socket.error:
                self.sock.close()
                self.sock = None  # so we can call createSocket next time
        else:
            raise RemoteMessagingError
           
    def handleError(self, record):
        raise RemoteMessagingError
        

class RemoteMessagingSender(logging.Logger):
    '''
    Create a logging object which will send messages over a socket to a logger running on a remote host.

    G{classtree RemoteMessagingSender}
    '''
    def __init__(self, name, host, port=logging.handlers.DEFAULT_TCP_LOGGING_PORT, logLevel=logging.DEBUG):
        '''
        @param name: The logger name
        @type name: C{str}
        
        @param host: The host which is listening to this sender.
        @type host: C{str}
        
        @param port: The INET socket port number on the listening host.
        @type port: C{int}
        
        @param logLevel: The level for the logging object.
        @type logLevel: C{int}
        '''
        logging.Logger.__init__(self, name)
        
        self.setLevel(logLevel)
        
        self.socketHandler = RemoteMessagingSocketHandler(host, int(port))
        self.addHandler(self.socketHandler)

    def close(self):
        '''
        Close the socket in use by the SocketHandler
        '''
        self.socketHandler.close()


if __name__ == '__main__':
    ''' A hello world example '''
    LOGNAME = 'helloWorld'
    
    from optparse import OptionParser
    parser = OptionParser()
    
    parser.set_defaults(
        server=False,
        verbose=False,
        runtime=0,
        ip=socket.gethostbyname(socket.gethostname()),
        port=logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    
    parser.add_option('-s', '--server', action='store_true', dest='server')
    parser.add_option('-c', '--client', action='store_false', dest='server')
    parser.add_option('-i', '--ip')
    parser.add_option('-p', '--port', type='int', help='try a value of 0 to allow the kernel to dynamically allocate a port')
    parser.add_option('-r', '--runtime', type='int')
    parser.add_option('-v', '--verbose', action='store_true')
    
    if len(sys.argv) == 0:
        parser.print_help()
        sys.exit(2)
    
    (opts, args) = parser.parse_args()

    if opts.server: # configure the server (receiving side)
        logger = logging.getLogger(LOGNAME)
        logger.setLevel(logging.DEBUG)
        
        logFormatter = logging.Formatter('%(asctime)s - %(levelname)8s : loop %(message)s', '[%x %X]')
        
        logHandler = logging.StreamHandler()
        logHandler.setFormatter(logFormatter)
        
        logger.addHandler(logHandler)
        
        # now start up the receiver, which will use the locally configured logger by default
        server = RemoteMessagingServer(port=opts.port, verbose=opts.verbose)
        server.start()

        # normally at this point the app using the server would start doing something, and shut down
        # the server once it was finished.  We'll just go to sleep instead and let the server thread
        # run.
        if opts.runtime > 0:
            print('server started - will run for %ss' % opts.runtime)
            time.sleep(opts.runtime)       
            server.stop()
        else:
            # just loop through once a minute, we'll exit when the user hits <CTRL>-c to kill the
            # running script
            while True:
                time.sleep(60)

    else: # configure the client (sending side)
        sndr = RemoteMessagingSender(host=opts.ip, port=opts.port, name=LOGNAME)
        
        for i in range(5):
            print('loop: %s' % i)
            extra = (i, socket.gethostname().split('.')[0], getLanIP())

            sndr.info('%s : %s %s some sort of informational message', *extra)
            #sndr.warning('a warning message', extra)
            #sndr.debug('a debug message', extra)
            
            time.sleep(1)

        sndr.info('Done\n')
        sndr.close()
            

