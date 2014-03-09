from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import transaction
from .signals import runDefferedCmds


class MyUserAdmin(UserAdmin):
    def response_change(self, request, new_object):
        res = super(MyUserAdmin, self).response_change(request, new_object)
        transaction.commit()
        runDefferedCmds(new_object)
        return res

    def response_add(self, request, obj, post_url_continue='../%s/'):
        res = UserAdmin.response_add(self, request, obj,
                                      post_url_continue=post_url_continue)
        transaction.commit()
        runDefferedCmds(obj)
        return res


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
