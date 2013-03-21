# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.


from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns(
    'apps.console.views',
    url(r'^$', 'main'),
    url(r'^reload$', 'reload'),
    url(r'(?P<script_id>[0-9]+)$', 'detail'),
    url(r'(?P<script_id>[0-9]+)/run$', 'run'),
    url(r'(?P<script_id>[0-9]+)/status$', 'status'),
    url(r'^upload$', 'upload'),
)
