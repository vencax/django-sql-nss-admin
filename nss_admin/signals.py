from django.conf import settings
from command_runner import runCommand

from .utils import createPasswdHash

ISSUE_SAMBA_COMMANDS = getattr(settings, 'ISSUE_SAMBA_COMMANDS', False)
DELETE_HOME_ON_DELETION = getattr(settings, 'DELETE_HOME_ON_DELETION', False)
HOMES_PATH = getattr(settings, 'HOMES_PATH', '/home')
PGINA_HACKS = getattr(settings, 'PGINA_HACKS', False)

def sysUserSaved(sender, instance, **kwargs):
    """
    Make appropriate pwd hash and save raw one for further processing.
    """
    instance._raw_pwd = instance.password
    if not hasattr(instance, 'DO_NOT_UPDATE_PWD'):
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
    """
    Create home dir and samba user on create
    or change samba pwd on change.
    """
    if created:
        homedir = '%s/%s' % (HOMES_PATH, instance.user_name)
        exists = runCommand('test -d %s' % homedir)
        if exists == 0:
            runCommand('mv %s /tmp' % homedir)
        mkHome = 'cp -R /etc/skel %s && chown -R %s:adm %s && chmod 770 %s' %\
                (homedir, instance.user_name, homedir, homedir)
        instance._deferredCMDs = (mkHome, )
        if ISSUE_SAMBA_COMMANDS:
            mkSmbUsr = '(echo %s; echo %s) | smbpasswd -s -a %s' %\
                (instance._raw_pwd, instance._raw_pwd, instance.user_name)
            instance._deferredCMDs += (mkSmbUsr, )
    else:
        if ISSUE_SAMBA_COMMANDS and not hasattr(instance, 'DO_NOT_UPDATE_PWD'):
            runCommand('(echo %s; echo %s) | smbpasswd -s %s' %\
                (instance._raw_pwd, instance._raw_pwd, instance.user_name))

    return instance


def sysUserDeleted(sender, instance, **kwargs):
    """
    Delete samba user and tar home dir to /tmp.
    """
    if ISSUE_SAMBA_COMMANDS:
        runCommand('smbpasswd -x %s' % instance.user_name)
    if DELETE_HOME_ON_DELETION:
        homedir = '%s/%s' % (HOMES_PATH, instance.user_name)
        runCommand('tar -czf /tmp/%s.tgz %s && rm -rf %s' % \
                   (instance.user_name, homedir, homedir))
