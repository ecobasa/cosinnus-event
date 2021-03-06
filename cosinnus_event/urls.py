# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


cosinnus_group_patterns = patterns('cosinnus_event.views',
    url(r'^$', 'index_view', name='index'),
    url(r'^list/$', 'list_view', name='list'),
    url(r'^list/(?P<tag>[^/]+)/$', 'list_view', name='list-filtered'),
    url(r'^export/$', 'export_view', name='export'),

    url(r'^add/$',
        'entry_add_view',
        {'form_view': 'add'},
        name='entry-add'),

    url(r'^(?P<slug>[^/]+)/$',
        'entry_detail_view',
        name='entry-detail'),

    url(r'^(?P<slug>[^/]+)/delete/$',
        'entry_delete_view',
        {'form_view': 'delete'},
        name='entry-delete'),

    url(r'^(?P<slug>[^/]+)/edit/$',
        'entry_edit_view',
        {'form_view': 'edit'},
        name='entry-edit'),

    url(r'^(?P<slug>[^/]+)/vote/$',
        'entry_vote_view',
        {'form_view': 'vote'},
        name='entry-vote'),
)


cosinnus_root_patterns = patterns(None)
urlpatterns = cosinnus_group_patterns + cosinnus_root_patterns
