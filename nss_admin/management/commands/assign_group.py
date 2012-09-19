from optparse import make_option

from django.core.management.base import BaseCommand
from nss_admin.models import SysUser, SysGroup, SysMembership

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--input', action='store_true', dest='all', default='~/import.ldif',
                    help=u'Input LDIF file'),
        make_option('--skip', action='store_true', dest='by-time', default=[],
                    help=u'DNs to skip'),
    )
    help = u'Import from LDIF'

    defaultGroup = 'zaci'
    extraGroups = {
        'ucitele' : ['blazkova', 'capakova', 'capakova', 'cervinkova', 'cidlikova',
'cizek', 'cizkova', 'dvorakova', 'dvorakovada', 'grenar', 'juzova',
'kolaci', 'kolaci', 'kopecka', 'kordinova', 'koukal', 'machanderova',
'matejova', 'nemeckova', 'novakova', 'novakovap', 'novakovapavla',
'stastna', 'sudova', 'svecova', 'volckova', 'votypkova', 'weinzettelova',
'zackova', 'zrustova']
    }


    def handle(self, *args, **options):
        notAssignedUsers = SysUser.objects.filter(sysmembership=None)
        for u in notAssignedUsers:
            self._assign(u)

    def _assign(self, user):
        for g, members in self.extraGroups.items():
            if user.user_name in members:
                self._add(g, user)
                return
        self._add(self.defaultGroup, user)

    def _add(self, group, user):
        gobj = SysGroup.objects.get(group_name=group)
        sm = SysMembership(user=user, group=gobj)
        sm.save()





