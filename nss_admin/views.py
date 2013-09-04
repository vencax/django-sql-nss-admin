import csv
import codecs
import random
import unicodedata
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib import messages
from django.utils.translation import ugettext as _

from .models import SysUser, PGINA_HACKS
from .utils import checkPasswd, checkPasswdValidity
from command_runner import runCommand
from django.db.transaction import commit_on_success


class ChangePwdForm(PasswordChangeForm):
    username = forms.CharField(label=_("Username"), )

    def __init__(self, *args, **kwargs):
        super(ChangePwdForm, self).__init__(None, *args, **kwargs)

    def save(self, commit=True):
        if commit:
            u = self.cleaned_data['u']
            u.password = self.cleaned_data['new_password1']
            u.save()
        return u

    def clean_new_password1(self):
        if not checkPasswdValidity(self.cleaned_data['new_password1']):
            raise forms.ValidationError(_("No diacritics in password allowed"))
        return self.cleaned_data['new_password1']

    def clean_username(self):
        try:
            SysUser.objects.get(user_name=self.cleaned_data['username'])
        except SysUser.DoesNotExist:
            raise forms.ValidationError(_("No user with given username"))
        return self.cleaned_data['username']

    def clean_old_password(self):
        try:
            u = SysUser.objects.get(user_name=self.cleaned_data['username'])
            if PGINA_HACKS:
                pwdForCheck = u.unixpwd
            else:
                pwdForCheck = u.password
            if not checkPasswd(self.cleaned_data['old_password'], pwdForCheck):
                raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
            self.cleaned_data['u'] = u
        except KeyError:
            pass

        return self.cleaned_data['old_password']

ChangePwdForm.base_fields.keyOrder = ['username', 'old_password', 'new_password1', 'new_password2']

class BatchForm(forms.Form):
    batch = forms.FileField()

def change_passwd(request):
    """
    Allows user to change its password.
    """
    if request.method == 'POST':
        form = ChangePwdForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, _('password changed'))
            form = ChangePwdForm()
    else:
        form = ChangePwdForm()

    return render_to_response('nss_admin/passForm.html', {
        'form' : form
        }, RequestContext(request))
    
def load_batch(request):
    """
    Allows send batch with users to be added. 
    """
    if request.method == 'POST':
        form = BatchForm(request.POST, request.FILES)
        if form.is_valid():
            added = _add_users_in_batch(form.files['batch'])
            m = '%i %s: %s' % (len(added), _('Users added'), ', '.join(added))
            messages.info(request, m)
            form = BatchForm()
    else:
        form = BatchForm()

    return render_to_response('nss_admin/batchForm.html', {
        'form' : form
        }, RequestContext(request))
    
@commit_on_success
def _add_user(firstname, lastname):
    realname = '%s %s' % (firstname, lastname)        
        
    def strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn')
    
    if not SysUser.objects.filter(realname=realname).exists():
        uname = strip_accents(firstname+lastname).lower()
        if SysUser.objects.filter(user_name=uname).exists():
            uname + str(random.randint(100))
        u = SysUser(user_name=uname, realname=realname)
        u.save()
        return u

def _add_users_in_batch(batch):
    reader = csv.reader(batch, delimiter=';')
    added = []
    for line in reader:
        line = [unicode(codecs.decode(f, 'windows-1250')) for f in line]
        firstname, lastname = line[0], line[1]
        newu = _add_user(firstname, lastname)
        if newu:
            if hasattr(newu, '_deferredCMDs'):
                for cmd in newu._deferredCMDs:
                    runCommand(cmd)
            added.append(newu.user_name)
    return added
        