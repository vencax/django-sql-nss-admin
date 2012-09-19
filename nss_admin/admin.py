from django.contrib import admin
from functools import partial
from django.forms.models import modelform_factory

from .models import SysGroup, SysUser, SysMembership, PGINA_HACKS
from .forms import SysUserAdminForm
from command_runner import runCommand

class MembershipInline(admin.TabularInline):
    model = SysMembership
    extra = 1
    
class SysGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name',)
    search_fields = ['group_name']
    exclude = ('members', 'status')
    
class SysUserAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
    ]
    list_display = ('user_name', 'realname', 'gid')
    search_fields = ['user_name', 'realname']
    exclude = ('status',)
    list_filter = ('gid',)
    chageform = SysUserAdminForm
    if PGINA_HACKS:
        exclude += ('user', 'hash_method')
        
    def save_model(self, request, obj, form, change):
        super(SysUserAdmin, self).save_model(request, obj, form, change)
        if hasattr(obj, '_deferredCMDs'):
            request.DEFERREDCMDS = obj._deferredCMDs
            del(obj._deferredCMDs)
        
    def add_view(self, request, form_url='', extra_context=None):
        rval = super(SysUserAdmin, self).add_view(request, form_url, extra_context)
        if hasattr(request, 'DEFERREDCMDS'):
            for cmd in request.DEFERREDCMDS:
                runCommand(cmd)
        return rval
        
    def get_form(self, request, obj=None, **kwargs):
        """
        Borrowed from admin.ModelAdmin because I want do differentiate between
        change and add form.  
        """
        if obj == None:
            form = self.form
        else:
            form = getattr(self, 'chageform', self.form)
            
        if self.declared_fieldsets:
            fields = admin.util.flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(self.get_readonly_fields(request, obj))
        if hasattr(form, '_meta') and form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(form._meta.exclude)
        # if exclude is an empty list we pass None to be consistant with the
        # default on modelform_factory
        exclude = exclude or None
        defaults = {
            "form": form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
        return modelform_factory(self.model, **defaults)

admin.site.register(SysGroup, SysGroupAdmin)
admin.site.register(SysUser, SysUserAdmin)
