from __future__ import absolute_import

import os
from time import time

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User

from .models import SysUser
from .utils import createPasswdHash


ISSUE_SAMBA_COMMANDS = getattr(settings, 'ISSUE_SAMBA_COMMANDS', False)
DELETE_HOME_ON_DELETION = getattr(settings, 'DELETE_HOME_ON_DELETION', False)
HOMES_PATH = getattr(settings, 'HOMES_PATH', '/home')
PGINA_HACKS = getattr(settings, 'PGINA_HACKS', False)

_chsambapass = '(echo %s; echo %s) | smbpasswd -s %s'
_makesambauser = '(echo %s; echo %s) | smbpasswd -s -a %s'


@shared_task
def sync_user(uname, rawpwd):
    user = User.objects.get(username=uname)

    try:
        sysUser = SysUser.objects.get(user=uname)
        if rawpwd and ISSUE_SAMBA_COMMANDS:
            _run_command(_chsambapass % (rawpwd, rawpwd, uname))
        created = False
    except SysUser.DoesNotExist:
        sysUser = SysUser(user=uname)
        created = True

    _syncSysUser(user, sysUser, rawpwd)

    if created:
        time.sleep(2)   # wait all is done id DB
        _createHome(uname)
        if ISSUE_SAMBA_COMMANDS:
            _run_command(_makesambauser % (rawpwd, rawpwd, uname))


@shared_task
def remove_user(uname):
    _delSambaUserAndHome(uname)
    sysUser = _getSysUser(uname)
    sysUser.delete()


def _run_command(command):
    if settings.DEBUG:
        print command
    else:
        os.system(command)


def _syncSysUser(user, sysUser, rawpwd):
    """
    Make appropriate SysUser instance according user
    """
    if PGINA_HACKS:
        sysUser.user = user.username
        sysUser.hash_method = 'MD5'

    if rawpwd:
        sysUser.unixpwd = createPasswdHash(rawpwd)
        if PGINA_HACKS:
            from hashlib import md5
            sysUser.password = md5(rawpwd).hexdigest()

    sysUser.user_name = user.username
    sysUser.realname = '%s %s' % (user.first_name, user.last_name)
    sysUser.status = 'A'

    GID, otherGrs = _extractPrimaryGroup(user)
    if not GID:
        GID = getattr(settings, 'DEFAULT_GID', 'users')
    sysUser.gid = _getOrCreateSysGroup(GID)
    _syncGroups(otherGrs, sysUser)

    sysUser.save()


def _extractPrimaryGroup(user):
    GID, others = None, []
    for g in user.groups.all():
        if not GID:
            GID = g
        else:
            others.append(g)
    return GID, others


def _syncGroups(otherGrs, sysUser):
    from .models import SysMembership

    # delete all memberships
    userMships = SysMembership.objects.filter(user=sysUser.user_id)
    for g in userMships:
        g.delete()

    # create them all
    for g in otherGrs:
        sysgr = _getOrCreateSysGroup(g)
        ms = SysMembership(user=sysUser, group=sysgr)
        ms.save()


def _getOrCreateSysGroup(group):
    from .models import SysGroup
    try:
        g = SysGroup.objects.get(group_name=group.name)
    except SysGroup.DoesNotExist:
        g = SysGroup(group_name=group.name)
        g.save()
    return g


def _getSysUser(uname):
    try:
        sysUser = SysUser.objects.get(user=uname)
    except SysUser.DoesNotExist:
        sysUser = SysUser(user=uname)
    return sysUser


def _createHome(uname):
    """
    Create home dir and samba user on create
    or change samba pwd on change.
    """
    homedir = '%s/%s' % (HOMES_PATH, uname)
    exists = _run_command('test -d %s' % homedir)
    if exists == 0:
        _run_command('mv %s /tmp' % homedir)
    mkHome = 'cp -R /etc/skel %s && chown -R %s:adm %s && chmod 770 %s' %\
            (homedir, uname, homedir, homedir)
    _run_command(mkHome)


def _delSambaUserAndHome(uname):
    """
    Delete samba user and tar home dir to /tmp.
    """
    if DELETE_HOME_ON_DELETION:
        homedir = '%s/%s' % (HOMES_PATH, uname)
        c = 'tar -czf /tmp/%s.tgz %s && rm -rf %s' % (uname, homedir, homedir)
        _run_command(c)
    if ISSUE_SAMBA_COMMANDS:
        _run_command('smbpasswd -x %s' % uname)
