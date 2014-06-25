from django.conf.urls.defaults import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.change_passwd, name='nss_admin_pass_change'),
    url(r'^load_batch/$', views.load_batch, name='load_batch'),
)
