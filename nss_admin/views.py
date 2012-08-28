from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .models import SysUser, PGINA_HACKS
from .utils import createPasswdHash, checkPasswd

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
    
    def clean_password(self):
        try:
            createPasswdHash(self.cleaned_data['new_password1'])
            return self.cleaned_data['new_password1']
        except UnicodeEncodeError:
            raise forms.ValidationError(_("No diacritics in password allowed"))
        
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

def change_passwd(request):
    """
    Allows user to change its password.
    """
    if request.method == 'POST':
        form = ChangePwdForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('nss_admin_pass_changed'))          
    else:
        form = ChangePwdForm()
        
    return render_to_response('nss_admin/passForm.html', {
        'form' : form
        }, RequestContext(request))