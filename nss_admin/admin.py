from django.contrib import admin

from models import SysGroup, SysUser, SysMembership, PGINA_HACKS

class MembershipInline(admin.TabularInline):
    model = SysMembership
    extra = 1
    
class SysGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'gid')
    search_fields = ['group_name']
    exclude = ('members', 'gid')
    
class SysUserAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
    ]
    list_display = ('user_name', 'realname', 'uid', 'homedir', 'shell')
    search_fields = ['user_name']
    exclude = ('uid', 'homedir', 'lastchange', 'inact')
    if PGINA_HACKS:
        exclude += ('user', 'hash_method')

admin.site.register(SysGroup, SysGroupAdmin)
admin.site.register(SysUser, SysUserAdmin)
