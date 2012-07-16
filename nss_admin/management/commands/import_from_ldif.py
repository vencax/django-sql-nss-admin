from optparse import make_option

from django.core.management.base import BaseCommand
from nss_admin.models import SysUser
from ldif import LDIFParser

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--input', action='store_true', dest='all', default='~/import.ldif', 
                    help=u'Input LDIF file'),
        make_option('--skip', action='store_true', dest='by-time', default=[], 
                    help=u'DNs to skip'),
    )
    help = u'Import from LDIF'
    
    class MyLDIF(LDIFParser):
        def __init__(self, inputFile, skip):
            LDIFParser.__init__(self, inputFile)
            self.SKIP_DN = skip
            self.PROCESS_ONLY = 'CN=Users,DC=zsplana,DC=cz'
        
        def handle(self, dn, entry):
            if not self._shallBeProcessed(dn):
                return
            try:
                username = entry['sAMAccountName'][0]
                if SysUser.objects.filter(user_name=username).exists():
                    return
                su = SysUser(user_name=username,
                             password=username,
                             realname=entry['name'][0])
                su.save()
            except Exception, e:
                print e
            
        def _shallBeProcessed(self, dn):
            if dn.endswith(self.PROCESS_ONLY):
                return True
            if self.PROCESS_ONLY:
                return False
            for s in self.SKIP_DN:
                if dn.endswith(s):
                    return False
            return True

    def handle(self, *args, **options):
        parser = self.MyLDIF(open(args[0], 'r'), args[1].split(';'))
        parser.parse()

        




