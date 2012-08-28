from django.conf import settings
from command_runner import runCommand

from .utils import createPasswdHash

ISSUE_SAMBA_COMMANDS = getattr(settings, 'ISSUE_SAMBA_COOMANDS', False)
DELETE_HOME_ON_DELETION = getattr(settings, 'DELETE_HOME_ON_DELETION', False)
HOMES_PATH = getattr(settings, 'HOMES_PATH', '/home')
PGINA_HACKS = getattr(settings, 'PGINA_HACKS', False)

def sysUserSaved(sender, instance, **kwargs):
    """ Automatically handle home directory """
    instance._raw_pwd = instance.password
    if PGINA_HACKS:
        instance.user = instance.user_name
        instance.hash_method = 'MD5'
        instance.unixpwd = createPasswdHash(instance.password)
        from hashlib import md5
        instance.password = md5(instance.password).hexdigest()
    else:
        instance.password = createPasswdHash(instance.password)
    return instance
            
def sysUserPostSaved(sender, instance, created, **kwargs):
    if created:
        homedir = '%s/%s' % (HOMES_PATH, instance.user_name)
        runCommand('cp -R /etc/skel %s && chown -R %s:adm %s && chmod 770 %s' %\
                   (homedir, instance.user_name, homedir, homedir))
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
        runCommand('tar -czf /tmp/%s.tgz %s && rm -rf %s' % \
                   (instance.user_name, homedir, homedir))
    