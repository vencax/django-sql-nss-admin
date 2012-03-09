from django.conf import settings
from django.db.models.aggregates import Max
from command_runner import runCommand

from .utils import createPasswdHash


UID_RANGE_BEGIN = getattr(settings, 'UID_RANGE_BEGIN', 5000)
GID_RANGE_BEGIN = getattr(settings, 'GID_RANGE_BEGIN', 5000)
ISSUE_SAMBA_COOMANDS = getattr(settings, 'ISSUE_SAMBA_COOMANDS', False)
DELETE_HOME_ON_DELETION = getattr(settings, 'DELETE_HOME_ON_DELETION', False)
HOMES_PATH = getattr(settings, 'HOMES_PATH', '/home')

def sysUserSaved(sender, instance, **kwargs):
    """ Automatically assigns UID, handle home directory """
    if not instance.uid:
        maxuid = sender.objects.all().aggregate(Max('uid'))['uid__max']
        if maxuid: 
            instance.uid = maxuid + 1
        else:
            instance.uid = UID_RANGE_BEGIN
    if not instance.homedir:
        instance.homedir = '%s/%s' % (HOMES_PATH, instance.user_name)
    instance._raw_pwd = instance.password
    instance.password = createPasswdHash(instance.password)
    return instance
            
def sysUserPostSaved(sender, instance, created, **kwargs):
    if created:
        runCommand('''
        cp -R /etc/skel %s; 
        chown %s %s;
        chmod 700 %s''' % (instance.homedir, instance.user_name, 
                            instance.homedir, instance.homedir))
        if ISSUE_SAMBA_COOMANDS:
            runCommand('(echo %s; echo %s) | smbpasswd -s -a %s' %\
                (instance._raw_pwd, instance._raw_pwd, instance.user_name))
    else:
        if ISSUE_SAMBA_COOMANDS:
            runCommand('(echo %s; echo %s) | smbpasswd -s %s' %\
                (instance._raw_pwd, instance._raw_pwd, instance.user_name))
    return instance

def sysGroupSaved(sender, instance, **kwargs):
    """ Automatically assigns GID """
    if not instance.gid:
        maxgid = sender.objects.all().aggregate(Max('gid'))['gid__max']
        if maxgid: 
            instance.gid = maxgid + 1
        else:
            instance.gid = GID_RANGE_BEGIN
            
def sysUserDeleted(sender, instance, **kwargs):
    if ISSUE_SAMBA_COOMANDS:
          runCommand('smbpasswd -d %s' % instance.user_name)
    if DELETE_HOME_ON_DELETION:
          runCommand('rm -rf %s' % instance.homedir)