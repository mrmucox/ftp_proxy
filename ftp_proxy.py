import socket
from ftplib import FTP
import io
import gzip
import time
import sys

socket.socket_formal = socket.socket

class ProxyException(Exception):
    """Proxy returned an error."""

# Class that wraps a real socket and changes it to a HTTP tunnel whenever a connection is asked via the "connect" method
class ftp_proxy :    
    #def __init__(self, socket, proxy_host, proxy_port) : 
    def __init__(self, socket, proxy_host, proxy_port, FTP_HOST, FTP_USER = "anonymous", FTP_PASS = "anonymous", debug = True, ProxyConnectionErrorRetries = 0, OtherErrorRetries = 20) : 
        # First, use the socket, without any change
        self.socket = socket

        # Create socket (use real one)
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

        # FTP Host Parameters
        self.FTP_HOST = FTP_HOST
        self.FTP_USER = FTP_USER
        self.FTP_PASS = FTP_PASS

        # Options
        self.debug = debug
        self.ProxyConnectionErrorRetries = ProxyConnectionErrorRetries
        self.OtherErrorRetries = OtherErrorRetries

        # Copy attributes
        self.family = socket.family
        self.type = socket.type
        self.proto = socket.proto

        def socket_proxy(af, socktype, proto) :

            # Create a socket, old school :
            sock = socket.socket_formal(af, socktype, proto)

            # Wrap it within a proxy socket
            return ftp_proxy(sock, self.proxy_host, self.proxy_port) 

        # Replace the "socket" method by our custom one
        socket.socket = socket_proxy

        passed = False
        OtherError = 0
        ProxyException = 0
        #print (passed, OtherError, OtherErrorRetries, ProxyException, ProxyConnectionErrorRetries)
        while (not passed and OtherError < self.OtherErrorRetries and (ProxyException < self.ProxyConnectionErrorRetries or self.ProxyConnectionErrorRetries == 0)):
            try:
                self.ftp = FTP(self.FTP_HOST, self.FTP_USER, self.FTP_PASS)
                if debug:
                    print "FTP Connection Established"
                passed = True
            except ProxyException as e:
                ProxyException += 1
                if debug:
                    if ProxyException == 1:
                        if self.ProxyConnectionErrorRetries == 0:
                            print " Request failed, Proxy Error, will retry {0} times.".format(self.ProxyConnectionErrorRetries),
                        else:
                            print " Request failed, Proxy Error, will retry until proxy available.",
                        sys.stdout.softspace=0
                    else:
                        print ".",
                        sys.stdout.softspace=0
                time.sleep(1)
                passed = False
            except Exception as e:
                passed = False
                lastException = str(e)[0:4000]
                OtherError += 1
                if(ProxyException > 0):
                    ProxyException = 0
                    if debug:
                        print ""
                if debug:
                    print " Request failed, {0} tries left... ".format(self.OtherErrorRetries - OtherError)
                    print sys.exc_info()[0]
                time.sleep(1)
                passed = False
        if not passed:
            raise

    def __getattr__(self, name):
        '''Automatically wrap methods and attributes for socket object.'''
        return getattr(self.socket, name)

    def connect(self, address) :

        # Store the real remote adress
        (self.host, self.port) = address
       
        # Try to connect to the proxy 
        for (family, socktype, proto, canonname, sockaddr) in socket.getaddrinfo(
            self.proxy_host, 
            self.proxy_port,
            0, 0, socket.SOL_TCP) :
            try:
                
                # Replace the socket by a connection to the proxy
                self.socket = socket.socket_formal(family, socktype, proto)
                self.socket.connect(sockaddr)
                    
            except socket.error, msg:
                if self.socket:
                    self.socket.close()
                self.socket = None
                continue
            break
        if not self.socket :
            raise socket.error, msg
        
        # Ask him to create a tunnel connection to the target host/port
        self.socket.send(
                ("CONNECT %s:%d HTTP/1.1\r\n" + 
                "Host: %s:%d\r\n\r\n") % (self.host, self.port, self.host, self.port));

        # Get the response
        resp = self.socket.recv(4096)

        # Parse the response
        parts = resp.split()
        
        # Not 200 ?
        if parts[1] != "200" :
            raise ProxyException("Error response from Proxy server : %s" % resp)

    def get_gzip_file_from_ftp(self, FTP_FILE_PATH):
        mem = io.BytesIO()
        passed = False
        OtherError = 0
        ProxyException = 0
        
        while (not passed and OtherError < self.OtherErrorRetries and (ProxyException < self.ProxyConnectionErrorRetries or self.ProxyConnectionErrorRetries == 0)):
            try:
                self.retrbinary("RETR {0}".format(FTP_FILE_PATH), mem.write)
                mem.seek(0)
                gz = gzip.GzipFile(fileobj=mem, mode='rb')
                return gz.read()
            except ProxyException as e:
                ProxyException += 1
                if debug:
                    if ProxyException == 1:
                        if self.ProxyConnectionErrorRetries == 0:
                            print " Request failed, Proxy Error, will retry {0} times.".format(self.ProxyConnectionErrorRetries),
                        else:
                            print " Request failed, Proxy Error, will retry until proxy available.",
                        sys.stdout.softspace=0
                    else:
                        print ".",
                        sys.stdout.softspace=0
                time.sleep(1)
                passed = False
            except Exception as e:
                passed = False
                lastException = str(e)[0:4000]
                OtherError += 1
                if(ProxyException > 0):
                    ProxyException = 0
                    if debug:
                        print ""
                if debug:
                    print " Request failed, {0} tries left... ".format(self.OtherErrorRetries - OtherError)
                    print sys.exc_info()[0]
                time.sleep(1)
                passed = False
            raise