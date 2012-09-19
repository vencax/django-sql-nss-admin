from optparse import make_option
from django.core.management.base import BaseCommand
import os
import shutil

class Command(BaseCommand):
    """
    In case we already have old homes and want to move its content
    into new one run this.
    """
    option_list = BaseCommand.option_list + (
        make_option('--oldHomes', action='store_true', dest='all', default='~/import.ldif',
                    help=u'Input LDIF file'),
        make_option('--newHomes', action='store_true', dest='by-time', default=[],
                    help=u'DNs to skip'),
    )
    help = u'Copy old homes to new ones'

    def handle(self, *args, **options):
        oldHomes = args[0]
        newHomes = args[1]
        for d in os.listdir(oldHomes):
            newHome = os.path.join(newHomes, d)
            oldHome = os.path.join(oldHomes, d)
            if os.path.exists(newHome):
                print 'processing %s' % d
                try:
                    self._moveContent(oldHome, newHome)
                    shutil.rmtree(oldHome)
                except OSError, e:
                    print str(e)
                raw_input("Press Enter to continue...")

    def _moveContent(self, oldFolder, newFolder):
        for d in os.listdir(oldFolder):
            newFile = os.path.join(newFolder, d)
            oldFile = os.path.join(oldFolder, d)
            shutil.move(oldFile, newFile)






