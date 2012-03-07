'''
Created on Mar 7, 2012

@author: vencax
'''
from django.conf import settings

HASH_METHOD = getattr(settings, 'HASH_METHOD', 'MD5')

def createHomeDir(uname):
    #TODO: create actual homedir
    pass
  
def moveHomeDir(uname):
    #TODO: move existing homedir
    pass
  
def createPasswdHash(passwd):
    if HASH_METHOD == 'MD5':
        import md5
        return md5.new(passwd).hexdigest()