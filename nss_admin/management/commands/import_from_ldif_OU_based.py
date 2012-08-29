from optparse import make_option

from django.core.management.base import BaseCommand
from nss_admin.models import SysUser, SysGroup
from ldif import LDIFParser
import logging

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-f', '--file', action='store', type='string',
                    help=u'Input LDIF file'),
        make_option('-g', '--group', action='store', type='string',
                    help=u'primary group of imported users'),
    )
    help = u'Import from LDIF' #@ReservedAssignment
    
    class MyLDIF(LDIFParser):
        def __init__(self, inputFile, group):
            LDIFParser.__init__(self, inputFile)
            self.group = SysGroup.objects.get(group_name=group)
            self.PROCESS_ONLY = 'CN=Users,DC=zsplana,DC=cz'
        
        def handle(self, dn, entry):
            if not self._shallBeProcessed(dn, entry):
                return
            try:
                username = entry['sAMAccountName'][0]
                logging.info('Processing %s' % username)
                if SysUser.objects.filter(user_name=username).exists():
                    return
                
                realname = entry['name'][0].decode('utf-8')
                su = SysUser(user_name=username,
                             password=username,
                             gid=self.group,
                             realname=realname)
                su.save()
            except Exception, e:
                print e
            
        def _shallBeProcessed(self, dn, entry):
            if 'person' not in entry['objectClass']:
                return False
            
            return True

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        parser = self.MyLDIF(open(args[0], 'r'), args[1])
        parser.parse()