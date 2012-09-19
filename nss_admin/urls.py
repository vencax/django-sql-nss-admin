from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

from . import views

urlpatterns = patterns('',
    url(r'^$', views.change_passwd, name='nss_admin_pass_change'),
    url(r'^done/$', direct_to_template, {'template': 'nss_admin/passChanged.html'},
        name='nss_admin_pass_changed'),
)