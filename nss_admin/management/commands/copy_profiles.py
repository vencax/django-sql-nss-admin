# coding=utf-8

from optparse import make_option
from django.core.management.base import BaseCommand
import os
import shutil

class Command(BaseCommand):
    """
    In case we have had roaming profiles and want to copy contents of some folders into
    home directory to allow access to the date via H:\ share of home in linux.
    """
    defaultCopiedFldrs = 'Desktop,Documents,Favorites'
    
    option_list = BaseCommand.option_list + (
        make_option('--profiles', action='store_true', dest='all', 
                    help=u'Input LDIF file'),
        make_option('--newHomes', action='store_true', dest='by-time', 
                    help=u'DNs to skip'),
        make_option('--copiedFolders', action='store_true', dest='by-time', 
                    default=[defaultCopiedFldrs], help=u'DNs to skip'),
        make_option('--mapping', action='store_true', default='',
                    help=u'Every folder needs user action'),
        make_option('--interactive', action='store_true', default=False,
                    help=u'Every folder needs user action')
    )
    help = u'Copy profile selected profile folders into home folder'

    def handle(self, *args, **options):
        profiles = args[0]
        newHomes = args[1]
        copiedFldrs = args[2].split(',')
        mappingParts = args[3].split(';')
        mapping = {}
        for p in mappingParts:
            k, v = p.split('=')
            mapping[unicode(k)] = v
        for d in os.listdir(profiles):
            if d.endswith('.V2'):
                newHome = os.path.join(newHomes, d.rstrip('.V2'))
            else:
                newHome = os.path.join(newHomes, d)
            profile = os.path.join(profiles, d)
            if os.path.exists(newHome):
                print 'processing %s' % d
                try:
                    self._moveContent(profile, newHome, copiedFldrs, mapping)
                    shutil.rmtree(profile)
                except OSError, e:
                    print str(e)
                if options['interactive']:
                    raw_input("Press Enter to continue...")
        
    def _moveContent(self, profile, newFolder, copiedFldrs, mapping):
        for d in copiedFldrs:
            newFolderDir = os.path.join(newFolder, mapping[unicode(d)])
            oldFolderDir = os.path.join(profile, unicode(d))
            if not os.path.exists(oldFolderDir):
                oldFolderDir = os.path.join(profile, mapping[unicode(d)])
            if not os.path.exists(newFolderDir):
                os.makedirs(newFolderDir)
            for f in os.listdir(oldFolderDir):
                oldFile = os.path.join(oldFolderDir, f)
                newFile = os.path.join(newFolderDir, f)
                if os.path.exists(newFile):
                    newFile = newFile + '.new'
                shutil.move(oldFile, newFile)
    
        




