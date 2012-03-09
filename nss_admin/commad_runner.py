'''
Created on Mar 9, 2012

@author: vencax 
'''
import os
import time
from django.conf import settings

class ParamikoRuner(object):
    """
    Base class for paramiko based runners.
    """
    def __init__(self):
        import paramiko
        self._server = getattr(settings, 'AUTH_SERVER', '127.0.0.1')
        self._serverUser = getattr(settings, 'AUTH_SERVER_USER', 'root')
        self._client = paramiko.SSHClient()
        self._client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def run(self, command):    
        self._client.connect(self._server, username=self._serverUser)
        self.runCommand(command)
      
class SudoBasedParamikoRuner(ParamikoRuner):
    """
    This is a bit problematic since there is many ways how to login as root.
    That's why this class.
    """
    def __init__(self):
        super(SudoBasedParamikoRuner, self).__init__()
        self._passwd = open('admin.pwd').read()
        
    def runCommand(self, command):
        shell = self._client.invoke_shell()
        shell.send('sudo -i\n')
        time.sleep(2)
        print shell.recv(9999)
        shell.send('%s\n' % self._passwd)
        time.sleep(2)
        shell.send('%s\n' % command)
        print shell.recv(9999)
        shell.close()
        
        
class SysRunner(object):
    """
    This issues the commands directly on the machine this app runs.
    NOTE: this shall be run under root.
    """
    def run(self, command):
        os.system(command)