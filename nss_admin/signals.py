from django.conf import settings
from command_runner import runCommand

from .utils import createPasswdHash

ISSUE_SAMBA_COMMANDS = getattr(settings, 'ISSUE_SAMBA_COOMANDS', False)
DELETE_HOME_ON_DELETION = getattr(settings, 'DELETE_HOME_ON_DELETION', False)
HOMES_PATH = getattr(settings, 'HOMES_PATH', '/home')

def sysUserSaved(sender, instance, **kwargs):
    """ Automatically handle home directory """
    instance._raw_pwd = instance.password
    instance.password = createPasswdHash(instance.password)
    return instance
            
def sysUserPostSaved(sender, instance, created, **kwargs):
    if created:
        homedir = '%s/%s' % (HOMES_PATH, instance.user_name)
        runCommand('''
        cp -R /etc/skel %s; 
        chown %s %s;
        chmod 700 %s''' % (homedir, instance.user_name, homedir, homedir))
        if ISSUE_SAMBA_COMMANDS:
            runCommand('(echo %s; echo %s) | smbpasswd -s -a %s' %\
                (instance._raw_pwd, instance._raw_pwd, instance.user_name))
    else:
        if ISSUE_SAMBA_COMMANDS:
            runCommand('(echo %s; echo %s) | smbpasswd -s %s' %\
                (instance._raw_pwd, instance._raw_pwd, instance.user_name))
        
    return instance
            
def sysUserDeleted(sender, instance, **kwargs):
    if ISSUE_SAMBA_COMMANDS:
        runCommand('smbpasswd -d %s' % instance.user_name)
    if DELETE_HOME_ON_DELETION:
        homedir = '%s/%s' % (HOMES_PATH, instance.user_name)
        runCommand('rm -rf %s' % homedir)
    