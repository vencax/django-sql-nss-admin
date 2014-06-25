'''
Created on Mar 7, 2012

@author: vencax
'''
import string

from django.conf import settings

HASH_METHOD = getattr(settings, 'HASH_METHOD', 'MD5')


def createPasswdHash(passwd):
    if HASH_METHOD == 'MD5':
        from hashlib import md5
        return md5(passwd).hexdigest()
    if HASH_METHOD == 'CRYPT':
        import crypt, random

        def getsalt(chars=string.letters + string.digits):
            # generate a random 2-character 'salt'
            return random.choice(chars) + random.choice(chars)
        return crypt.crypt(passwd, getsalt())


def checkPasswd(rawpasswd, pwhash):
    try:
        if HASH_METHOD == 'MD5':
            from hashlib import md5
            return md5(rawpasswd).hexdigest() == pwhash
        if HASH_METHOD == 'CRYPT':
            import crypt
            return crypt.crypt(rawpasswd, pwhash) == pwhash
    except UnicodeEncodeError:
        return False


def checkPasswdValidity(pwd):
    for l in pwd:
        if l not in string.printable:
            return False
    return True
