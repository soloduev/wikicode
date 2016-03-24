from django.conf.urls import url, include
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^create/$', views.create, name='create'),
    url(r'^edit/$', views.edit, name='edit'),
    url(r'^help/$', views.help, name='help'),
    url(r'^page/(?P<id>[0-9]+)/$', views.page, name='page'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^user/$', views.user, name='user'),
    url(r'^registration/$', views.registration, name='registration'),
    url(r'^tree_manager/$',views.tree_manager, name='tree_manager'),


    url(r'^create_page/$', views.create_page, name='create_page'),

    url(r'^testform/$', views.testform, name='testform'),


    url(r'^test/$', views.test, name='test'),

]
