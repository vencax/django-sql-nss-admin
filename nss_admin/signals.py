from django.conf import settings
from command_runner import runCommand

from .utils import createPasswdHash

ISSUE_SAMBA_COMMANDS = getattr(settings, 'ISSUE_SAMBA_COMMANDS', False)
DELETE_HOME_ON_DELETION = getattr(settings, 'DELETE_HOME_ON_DELETION', False)
HOMES_PATH = getattr(settings, 'HOMES_PATH', '/home')
PGINA_HACKS = getattr(settings, 'PGINA_HACKS', False)


def userPostSaved(sender, instance, created, **kwargs):
    _syncSysUser(instance, **kwargs)
    if created:
        _createHome(instance)
        if ISSUE_SAMBA_COMMANDS:
            mkSmbUsr = '(echo %s; echo %s) | smbpasswd -s -a %s' %\
                (instance.rawpwd, instance.rawpwd, instance.username)
            instance._deferredCMDs += (lambda: runCommand(mkSmbUsr), )
    else:
        # change
        if hasattr(instance, 'rawpwd') and ISSUE_SAMBA_COMMANDS:
            runCommand('(echo %s; echo %s) | smbpasswd -s %s' %\
                (instance.rawpwd, instance.rawpwd, instance.username))


def userPostDeleted(sender, instance, **kwargs):
    _delSambaUserAndHome(sender, instance, **kwargs)
    sysUser = _getSysUser(instance.username)
    sysUser.delete()


def runDefferedCmds(obj):
    if hasattr(obj, '_deferredCMDs'):
        for cmd in obj._deferredCMDs:
            cmd()


def _syncSysUser(user, **kwargs):
    """
    Make appropriate SysUser instance according user
    """
    sysUser = _getSysUser(user.username)
    if PGINA_HACKS:
        sysUser.user = user.username
        sysUser.hash_method = 'MD5'

    if hasattr(user, 'rawpwd'):
        sysUser.unixpwd = createPasswdHash(user.rawpwd)
        if PGINA_HACKS:
            from hashlib import md5
            sysUser.password = md5(user.rawpwd).hexdigest()

    sysUser.user_name = user.username
    sysUser.realname = '%s %s' % (user.first_name, user.last_name)
    sysUser.status = 'A'

    sysUser.save()

    user._deferredCMDs = (lambda: _syncGroups(user, sysUser), )

    return sysUser


def _syncGroups(user, sysUser):
    from .models import SysMembership

    # delete all memberships
    userMships = SysMembership.objects.filter(user=sysUser)
    for g in userMships:
        g.delete()

    # create them all
    GID = True
    for g in user.groups.all():
        sysgr = _getGroup(g)

        if GID:
            sysUser.gid = sysgr
            sysUser.save()
            GID = False
        else:
            ms = SysMembership(user=sysUser, group=sysgr)
            ms.save()


def _getGroup(group):
    from .models import SysGroup
    try:
        g = SysGroup.objects.get(group_name=group.name)
    except SysGroup.DoesNotExist:
        g = SysGroup(group_name=group.name)
        g.save()
    return g


def _getSysUser(uname):
    from .models import SysUser
    try:
        sysUser = SysUser.objects.get(user=uname)
    except SysUser.DoesNotExist:
        sysUser = SysUser(user=uname)
    return sysUser


def _createHome(user):
    """
    Create home dir and samba user on create
    or change samba pwd on change.
    """
    homedir = '%s/%s' % (HOMES_PATH, user.username)
    exists = runCommand('test -d %s' % homedir)
    if exists == 0:
        runCommand('mv %s /tmp' % homedir)
    mkHome = 'cp -R /etc/skel %s && chown -R %s:adm %s && chmod 770 %s' %\
            (homedir, user.username, homedir, homedir)
    user._deferredCMDs += (lambda: runCommand(mkHome), )


def _delSambaUserAndHome(sender, instance, **kwargs):
    """
    Delete samba user and tar home dir to /tmp.
    """
    if DELETE_HOME_ON_DELETION:
        homedir = '%s/%s' % (HOMES_PATH, instance.username)
        runCommand('tar -czf /tmp/%s.tgz %s && rm -rf %s' % \
                   (instance.username, homedir, homedir))
    if ISSUE_SAMBA_COMMANDS:
        runCommand('smbpasswd -x %s' % instance.username)
