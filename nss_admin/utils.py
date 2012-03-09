'''
Created on Mar 7, 2012

@author: vencax
'''
from django.conf import settings

HASH_METHOD = getattr(settings, 'HASH_METHOD', 'MD5')
RUN_COMMAND_FACILITY = getattr(settings, 'RUN_COMMAND_FACILITY', 'SudoBasedParamikoRuner')
mod = __import__('nss_admin.commad_runner', globals(), locals(), [RUN_COMMAND_FACILITY])
runnerClass = getattr(mod, RUN_COMMAND_FACILITY)
runner = runnerClass()
  
def createPasswdHash(passwd):
    if HASH_METHOD == 'MD5':
        from hashlib import md5
        return md5(passwd).hexdigest()
      
def runCommand(command):
    """ Runs command on remote machine """
    runner.run(command)