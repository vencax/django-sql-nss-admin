'''
Created on Aug 30, 2012

@author: vencax
'''
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import SysUser
from .utils import createPasswdHash

class SysUserAdminForm(forms.ModelForm):
    
    password = forms.CharField(label=_('Password'), required=False,
        help_text=_('Input new password if desired'))
    
    def __init__(self, *args, **kwargs):
        super(SysUserAdminForm, self).__init__(*args, initial={'password': ''}, **kwargs)
    
    class Meta:
        model = SysUser
        
    def clean_password(self):
        pwd = self.cleaned_data['password']
        if pwd:
            try:
                createPasswdHash(pwd)
                return pwd
            except UnicodeEncodeError:
                raise forms.ValidationError(_('No diacritics in password allowed')) 
        else:
            self.DO_NOT_UPDATE_PWD = True
            return self.instance.password
        
    def save(self, commit=True):
        instance = super(SysUserAdminForm, self).save(commit)
        if hasattr(self, 'DO_NOT_UPDATE_PWD'):
            instance.DO_NOT_UPDATE_PWD = True
        return instance