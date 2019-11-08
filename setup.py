from setuptools import setup, find_packages

setup(name='ftp_proxy',
      version='0.0.1',
      author_email='mrmucox@gmail.com',
      description='A Transparent HTTP Tunnel for Python Sockets to be used by ftplib',
      author='MrMucox',
      url='https://github.com/mrmucox/ftp_proxy',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      py_modules=['ftp_proxy'])