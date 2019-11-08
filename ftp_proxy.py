import socket
from ftplib import FTP
import io
import gzip
import time

socket.socket_formal = socket.socket

class ProxyException(Exception):
    """Proxy returned an error."""

# Class that wraps a real socket and changes it to a HTTP tunnel whenever a connection is asked via the "connect" method
class ProxySock :    
    #def __init__(self, socket, proxy_host, proxy_port) : 
    def __init__(self, socket, proxy_host, proxy_port) : 
        # First, use the socket, without any change
        self.socket = socket

        # Create socket (use real one)
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

        # Copy attributes
        self.family = socket.family
        self.type = socket.type
        self.proto = socket.proto

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
            raise socket.error, ms 
        
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

    # Wrap all methods of inner socket, without any change
    def accept(self) :
        return self.socket.accept()

    def bind(self, *args) :
        return self.socket.bind(*args)
    
    def close(self) :
        return self.socket.close()
    
    def fileno(self) :
        return self.socket.fileno()

    
    def getsockname(self) :
        return self.socket.getsockname()
    
    def getsockopt(self, *args) :
        return self.socket.getsockopt(*args)
    
    def listen(self, *args) :
        return self.socket.listen(*args)
    
    def makefile(self, *args) :
        return self.socket.makefile(*args)
    
    def recv(self, *args) :
        return self.socket.recv(*args)
    
    def recvfrom(self, *args) :
        return self.socket.recvfrom(*args)

    def recvfrom_into(self, *args) :
        return self.socket.recvfrom_into(*args)
    
    def recv_into(self, *args) :
        return self.socket.recv_into(buffer, *args)
    
    def send(self, *args) :
        return self.socket.send(*args)
    
    def sendall(self, *args) :
        return self.socket.sendall(*args)
    
    def sendto(self, *args) :
        return self.socket.sendto(*args)
    
    def setblocking(self, *args) :
        return self.socket.setblocking(*args)
    
    def settimeout(self, *args) :
        return self.socket.settimeout(*args)
    
    def gettimeout(self) :
        return self.socket.gettimeout()
    
    def setsockopt(self, *args):
        return self.socket.setsockopt(*args)
    
    def shutdown(self, *args):
        return self.socket.shutdown(*args)

    # Return the (host, port) of the actual target, not the proxy gateway
    def getpeername(self) :
        return (self.host, self.port)

    # Install a proxy, by changing the method socket.socket()
def setup_http_proxy(proxy_host, proxy_port) :

    # New socket constructor that returns a ProxySock, wrapping a real socket
    def socket_proxy(af, socktype, proto) :

        # Create a socket, old school :
        sock = socket.socket_formal(af, socktype, proto)

        # Wrap it within a proxy socket
        return ftp_proxy(sock, proxy_host, proxy_port) 

    # Replace the "socket" method by our custom one
    socket.socket = socket_proxy

def setup_ftp_connection(FTP_HOST, FTP_USER = "Anonymous", FTP_PASS = "Anonymous", debug = True, ProxyConnectionErrorRetries = 0, OtherErrorRetries = 20):
    passed = False
    OtherError = 0
    ProxyException = 0
    #print (passed, OtherError, OtherErrorRetries, ProxyException, ProxyConnectionErrorRetries)
    while (not passed and OtherError < OtherErrorRetries and (ProxyException < ProxyConnectionErrorRetries or ProxyConnectionErrorRetries == 0)):
        try:
            return FTP(FTP_HOST, FTP_USER, FTP_PASS)
            if debug:
                print "FTP Connection Established"
        except ProxyException as e:
            ProxyException += 1
            if debug:
                if ProxyException == 1:
                    if ProxyConnectionErrorRetries == 0:
                        print " Request failed, Proxy Error, will retry {0} times.".format(ProxyConnectionErrorRetries),
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
                print " Request failed, {0} tries left... ".format(OtherErrorRetries - OtherError)
                print e
            time.sleep(1)
    raise

def get_gzip_file_from_ftp(FTP_CONNECTION, FTP_FILE_PATH):
    mem = io.BytesIO()
    passed = False
    tries = 10
    tried = 0
    FTP_CONNECTION.retrbinary("RETR {0}".format(FTP_FILE_PATH), mem.write)
    mem.seek(0)
    gz = gzip.GzipFile(fileobj=mem, mode='rb')
    return gz.read()