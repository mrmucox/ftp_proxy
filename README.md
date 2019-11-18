# ftp_proxy
A Transparent HTTP Tunnel for Python Sockets to be used by ftplib

This script allows you to transparently install an HTTP proxy (proxy HTTP 1.1, using CONNECT command) on all outgoing sockets.

This is to bring TCP over HTTP to FTPlib, transparently. It should enable HTTP tunneling for all methods / modules that use the low-level socket API.

Declaration:

ftp_proxy.ftp_proxy returns ftp_proxy.ftp_connection

  ftp = ftp_proxy(proxy_host, proxy_port, FTP_HOST, FTP_USER, FTP_PASS, debug, ProxyConnectionErrorRetries, OtherErrorRetries)
  
  proxy_host - The address of the proxy server. (required)
  
  proxy_port - The port of the proxy server. (required)
  
  FTP_HOST - The address of the FTP server. (required)
  
  FTP_USER - The Username on the FTP server. (optional - default: anonymous)
  
  FTP_PASS - The Password on the FTP server. (optional - default: anonymous)
  
  debug - To turn on or off printing debug infromation. (option - default: True)
  
  ProxyConnectionErrorRetries - How many times to retry if there are proxy connection issues, 0 will try indefinitely. (optional - default: 1)
  
  OtherErrorRetries - How many times to retry if there are proxy connection issues. (optional - default: 1)
  
ftp_connection has two methods

  get_gz_file(FTP_FILE_PATH) - Returns the output of the decoded gz file.
  
  get_txt_file(FTP_FILE_PATH) - Return the output of a text file.
  
    FTP_FILE_PATH is the path from the root of the FTP server to the file. (required)
    

Initially found at:
http://code.activestate.com/recipes/577643-transparent-http-tunnel-for-python-sockets-to-be-u/
