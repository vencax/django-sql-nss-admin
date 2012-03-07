from django.conf import settings
from django.db.models.aggregates import Max

from .utils import createHomeDir, moveHomeDir

UID_RANGE_BEGIN = getattr(settings, 'UID_RANGE_BEGIN', 5000)
GID_RANGE_BEGIN = getattr(settings, 'GID_RANGE_BEGIN', 5000)

def sysUserSaved(sender, instance, **kwargs):
    """ Automatically assigns UID, handle home directory """
    if not instance.uid:
        maxuid = sender.objects.all().aggregate(Max('uid'))['uid__max']
        if maxuid: 
            instance.uid = maxuid + 1
        else:
            instance.uid = UID_RANGE_BEGIN
    if not instance.homedir:
        instance.homedir = '/home/%s' % instance.user_name
        createHomeDir(instance.user_name)
    else:
        moveHomeDir(instance.user_name)

def sysGroupSaved(sender, instance, **kwargs):
    """ Automatically assigns GID """
    if not instance.gid:
        maxgid = sender.objects.all().aggregate(Max('gid'))['gid__max']
        if maxgid: 
            instance.gid = maxgid + 1
        else:
            instance.gid = GID_RANGE_BEGIN
