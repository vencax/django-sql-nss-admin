from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.signals import pre_save

from signals import sysUserSaved, sysGroupSaved
from nss_admin.utils import createPasswdHash


DEFAULT_SHELL = getattr(settings, 'DEFAULT_SHELL', '/bin/sh')
PGINA_HACKS = getattr(settings, 'PGINA_HACKS', False)

SHELL_CHOICES = (
    ('/bin/bash', 'Bash'),
    ('/bin/sh', 'Sh'),  
    ('/bin/false', 'No Shell')
)
USER_STATUS_CHOICES = (
    ('N', _('No problem?')),
)

class SysUser(models.Model):
    """
    Represent a system user.
    """
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(verbose_name=_('Username'), max_length=50, unique=True)
    realname = models.CharField(verbose_name=_('realname'), max_length=32)    
    shell = models.CharField(verbose_name=_('Login Shell'), max_length=20, 
                             choices=SHELL_CHOICES, default=DEFAULT_SHELL)    
    password = models.CharField(verbose_name=_('Password'), max_length=40, 
                                help_text='Password for shell logins')    
    status = models.CharField(verbose_name=_('status'), max_length=1, 
                              choices=USER_STATUS_CHOICES, default='N')
    uid = models.PositiveIntegerField('User ID')
    gid = models.PositiveIntegerField('User GID', default=1000)
    homedir = models.CharField(verbose_name=_('Home Directory'), max_length=32)
    lastchange = models.PositiveIntegerField(verbose_name=_('lastchange'), default=1)
    min = models.PositiveIntegerField(verbose_name=_('minchange'), default=0,
                                      help_text=_('Minimum password validity'))
    max = models.PositiveIntegerField(verbose_name=_('maxchange'), default=99999,
                                      help_text=_('Maximum password validity'))
    warn = models.PositiveIntegerField(verbose_name=_('warn days'), 
                                       help_text=_('Warning period'), default=0)
    inact = models.PositiveIntegerField(verbose_name=_('inact days'),
                                             help_text=_('Inactivity period'), default=0)
    expire = models.IntegerField(default=-1, verbose_name=_('expire days'))
    
    if PGINA_HACKS:
        # this is because PGina has username column name hardcoded
        user = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'user'
        verbose_name = _('system user')
        verbose_name_plural = _('system users')
        
    def save(self, *args, **kwargs):
        if PGINA_HACKS:
            self.user = self.user_names
        self.password = createPasswdHash(self.password)
        super(SysUser, self).save(*args, **kwargs)
        
    def __unicode__(self): return u'%s %s' % (_('system user'), self.user_name)
        
pre_save.connect(sysUserSaved, sender=SysUser, dispatch_uid='sysUser_pre_save')
# -----------------------------------------------------------------------------

GROUP_STATUS_CHOICES = (
    ('A', _('Active')),
)

class SysGroup(models.Model):
    """
    Represent group of system users.
    """ 
    group_id = models.AutoField(primary_key=True)
    group_name = models.CharField('Group Name', max_length=16, unique=True)
    status = models.CharField(verbose_name=_('status'), max_length=1, 
                              choices=GROUP_STATUS_CHOICES, default='A')
    group_password = models.CharField(max_length=34, default='x')
    gid = models.PositiveIntegerField('Group ID')
    members = models.ManyToManyField(SysUser, through='SysMembership')
    
    class Meta:
        db_table = 'groups'
        verbose_name = _('system group')
        verbose_name_plural = _('system groups')
        
    def __unicode__(self): return u'%s %s' % (_('system group'), self.group_name)
        
pre_save.connect(sysGroupSaved, sender=SysGroup, dispatch_uid='SysGroup_pre_save')
# -----------------------------------------------------------------------------

class SysMembership(models.Model):
    user_id = models.ForeignKey(SysUser)
    group_id = models.ForeignKey(SysGroup)
    
    class Meta:
        db_table = 'user_group'
        
# -----------------------------------------------------------------------------