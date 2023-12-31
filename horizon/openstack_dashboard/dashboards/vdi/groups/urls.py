# Copyright (c) 2014 Huawei Technologies.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import openstack_dashboard.dashboards.vdi.groups.views as views
from openstack_dashboard.dashboards.vdi.utils import importutils

urls = importutils.import_any('django.conf.urls.defaults',
                              'django.conf.urls')
patterns = urls.patterns
url = urls.url


urlpatterns = patterns('',
                       url(r'^$', views.GroupsView.as_view(),
                           name='index'),
                       url(r'^$', views.GroupsView.as_view(),
                           name='groups'),
                       url(r'^create-group$',
                           views.CreateGroupView.as_view(),
                           name='create-group'),
                       url(r'^(?P<group_id>[^/]+)/%s$' % 'detail',
                           views.GroupDetailsView.as_view(),
                           name='detail'),
                       url(r'^(?P<group_id>[^/]+)/update/$',
                           views.UpdateGroupView.as_view(),
                           name='update'))
