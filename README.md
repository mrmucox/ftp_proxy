# ftp_proxy
A Transparent HTTP Tunnel for Python Sockets to be used by ftplib

This script allows how to transparently install an HTTP proxy (proxy HTTP 1.1, using CONNECT command) on all outgoing sockets.

This is to bring TCP over HTTP to FTPlib, transparently. It should enable HTTP tunneling for all methods / modules that use the low-level socket API.
