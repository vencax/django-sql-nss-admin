'''
Created on Mar 7, 2012

@author: vencax
'''
from django.conf import settings

HASH_METHOD = getattr(settings, 'HASH_METHOD', 'MD5')
  
def createPasswdHash(passwd):
    if HASH_METHOD == 'MD5':
        from hashlib import md5
        return md5(passwd).hexdigest()