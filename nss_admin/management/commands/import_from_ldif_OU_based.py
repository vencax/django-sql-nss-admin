import logging
from optparse import make_option
from django.core.management.base import BaseCommand
from nss_admin.models import SysGroup
from ldif import LDIFParser

from nss_admin.management.commands.base_importer import BaseImporter

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-f', '--file', action='store', type='string',
                    help=u'Input LDIF file'),
        make_option('-g', '--group', action='store', type='string',
                    help=u'primary group of imported users'),
    )
    help = u'Import from LDIF' #@ReservedAssignment

    class MyLDIF(BaseImporter, LDIFParser):
        def __init__(self, inputFile, group):
            LDIFParser.__init__(self, inputFile)
            self.group = SysGroup.objects.get(group_name=group)
            self.PROCESS_ONLY = 'CN=Users,DC=zsplana,DC=cz'

        def _shallBeProcessed(self, dn, entry):
            if 'person' not in entry['objectClass']:
                return False

            return True

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        parser = self.MyLDIF(open(args[0], 'r'), args[1])
        parser.parse()