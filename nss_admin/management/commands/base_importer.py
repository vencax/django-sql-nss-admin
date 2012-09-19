'''
Created on Sep 19, 2012

@author: vencax
'''
from nss_admin.models import SysUser
from django.db.transaction import commit_on_success
from command_runner import runCommand
import logging

class BaseImporter(object):
    def handle(self, dn, entry):
        if not self._shallBeProcessed(dn):
            return
        try:
            username = entry['sAMAccountName'][0].lower()
            logging.info('Processing %s' % username)
            if SysUser.objects.filter(user_name=username).exists():
                return
            self.save_new(username, entry['name'][0].decode('utf-8'))
        except Exception, e:
            print e

    def save_new(self, uname, realname):
        su = SysUser(user_name=uname, password=uname, realname=realname)

        @commit_on_success
        def _saveInner():
            su.save()

        _saveInner()
        for cmd in getattr(su, '_deferredCMDs', []):
            runCommand(cmd)