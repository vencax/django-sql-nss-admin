import logging

from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand

from nss_admin.models import SysUser


class Command(BaseCommand):
    """
    In case we already have old homes and want to move its content
    into new one run this.
    """

    help = u'Create auth.User objects according SysUser objects (migration)'

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)

        susers = SysUser.objects.all()

        for su in susers:
            if not User.objects.filter(username=su.user_name).exists():
                groups = list(su.sysgroup_set.all())
                self._add_gid(su, groups)

                parts = su.realname.split(' ')
                surename = parts[0]
                if len(parts) > 1:
                    forname = parts[1]
                else:
                    forname = ''
                new_user = User(username=su.user_name,
                                first_name=forname, last_name=surename)
                new_user.save()
                self._sync_groups(new_user, groups)

                logging.info('user %s processed' % new_user.username)

    def _add_gid(self, user, groups):
        for g in groups:
            if g.group_name == user.gid.group_name:
                return
        groups.append(user.gid)

    def _sync_groups(self, user, groups):
        for sg in groups:
            try:
                g = Group.objects.get(name=sg.group_name)
            except Group.DoesNotExist:
                g = Group(name=sg.group_name)
                g.save()
            user.groups.add(g)

        user.save()
