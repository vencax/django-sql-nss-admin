from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete, post_save

from signals import userPostSaved, userPostDeleted


DEFAULT_SHELL = getattr(settings, 'DEFAULT_SHELL', '/bin/bash')
PGINA_HACKS = getattr(settings, 'PGINA_HACKS', False)


class SysUser(models.Model):
    """
    Represent a system user.
    """
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50, unique=True)
    realname = models.CharField(max_length=32)
    shell = models.CharField(max_length=20, default=DEFAULT_SHELL)
    password = models.CharField(max_length=40)
    status = models.CharField(max_length=1, default='A')
    gid = models.ForeignKey('SysGroup', default=1, null=True)

    if PGINA_HACKS:
        # this is because PGina has username column name hardcoded
        user = models.CharField(max_length=50, unique=True)
        hash_method = models.CharField(max_length=8)
        unixpwd = models.CharField(max_length=128)

    class Meta:
        db_table = 'user'

    def __unicode__(self):
        return self.user_name
# -----------------------------------------------------------------------------


class SysGroup(models.Model):
    """
    Represent group of system users.
    """
    group_id = models.AutoField(primary_key=True)
    group_name = models.CharField('Group Name', max_length=16, unique=True)
    status = models.CharField(max_length=1)
    members = models.ManyToManyField(SysUser, through='SysMembership')

    class Meta:
        db_table = 'groups'

    def __unicode__(self):
        return self.group_name
# -----------------------------------------------------------------------------


class SysMembership(models.Model):
    user = models.ForeignKey(SysUser)
    group = models.ForeignKey(SysGroup)

    class Meta:
        db_table = 'user_group'
# -----------------------------------------------------------------------------

# connect sysuser objects are synced according django users
post_save.connect(userPostSaved, sender=User, dispatch_uid='user_post_save')
post_delete.connect(userPostDeleted, sender=User, dispatch_uid='user_post_del')

orig_set_password = User.set_password


def new_set_password(self, raw_password):
    self.rawpwd = raw_password
    orig_set_password(self, raw_password)


User.set_password = new_set_password
