import unicodedata

from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.db.transaction import commit_on_success
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
import unicodecsv

from .utils import checkPasswdValidity


badoldpwd = _("Your old password was entered incorrectly. Enter it again.")


class ChangePwdForm(PasswordChangeForm):
    username = forms.CharField(label=_("Username"), )

    def __init__(self, *args, **kwargs):
        super(ChangePwdForm, self).__init__(None, *args, **kwargs)

    def save(self, commit=True):
        if commit:
            u = self.cleaned_data['u']
            u.set_password(self.cleaned_data['new_password1'])
            u.save()
        return u

    def clean_new_password1(self):
        if not checkPasswdValidity(self.cleaned_data['new_password1']):
            raise forms.ValidationError(_("No diacritics in password allowed"))
        return self.cleaned_data['new_password1']

    def clean_username(self):
        try:
            User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("No user with given username"))
        return self.cleaned_data['username']

    def clean_old_password(self):
        try:
            u = User.objects.get(username=self.cleaned_data['username'])
            if not u.check_password(self.cleaned_data['old_password']):
                raise forms.ValidationError(badoldpwd)
            self.cleaned_data['u'] = u
        except KeyError:
            raise forms.ValidationError(_('old password is required'))

        return self.cleaned_data['old_password']

ChangePwdForm.base_fields.keyOrder = [
    'username', 'old_password', 'new_password1', 'new_password2'
]


@never_cache
def change_passwd(request):
    """
    Allows user to change its password.
    """
    if request.method == 'POST':
        form = ChangePwdForm(request.POST)
        if form.is_valid():
            form.save()
            return render_to_response('nss_admin/message.html', {
                'message': _('password changed')
            }, RequestContext(request))
    else:
        form = ChangePwdForm()

    return render_to_response('nss_admin/passForm.html', {
        'form': form
        }, RequestContext(request))


class BatchForm(forms.Form):
    batch = forms.FileField(label=_('batch file'))
    groups = forms.ModelMultipleChoiceField(Group.objects.all(),
                                            label=_('groups'))


@never_cache
@login_required
@user_passes_test(lambda u: u.is_superuser)
def load_batch(request):
    """
    Allows send batch with users to be added.
    """
    if request.method == 'POST':
        form = BatchForm(request.POST, request.FILES)

        if form.is_valid():
            added, skipped, m = [], [], None

            try:
                added, skipped = _process_batch(form.files['batch'],
                                                form.cleaned_data['groups'])
            except Exception, e:
                m = '%s, error: %s' % (_('Bad batch file'), str(e))

            return render_to_response('nss_admin/message.html', {
                'message': m,
                'added': added,
                'skipped': skipped
            }, RequestContext(request))
    else:
        form = BatchForm()

    return render_to_response('nss_admin/batchForm.html', {
        'form': form
        }, RequestContext(request))


def _strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn')


@commit_on_success
def _add_user(line, groups):
    firstname, lastname = line[0], line[1]
    if len(line) > 2:
        mail = line[2]
        uname = mail.split('@')[0]
    else:
        uname = _strip_accents(firstname + lastname).lower()
        mail = '%s@skola.local' % uname
    if len(line) > 3:
        passwd = line[3]
    else:
        passwd = uname

    if not User.objects.filter(username=uname).exists():
        u = User(username=uname,
                 first_name=firstname, last_name=lastname,
                 email=mail)
        u.rawpwd = passwd
        u.set_password(passwd)
        u.save()

        for g in groups:
            u.groups.add(g)
        u.save()
        return True
    else:
        return False


def _process_batch(batch, groups):
    reader = unicodecsv.reader(batch, encoding='utf-8')
    added, skipped = [], []
    for line in reader:
        if _add_user(line, groups):
            added.append(line)
        else:
            skipped.append(line)
    return added, skipped
