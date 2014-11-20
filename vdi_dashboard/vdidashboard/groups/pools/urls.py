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


import vdidashboard.pools.views as views
from saharadashboard.utils import importutils

urls = importutils.import_any('django.conf.urls.defaults',
                              'django.conf.urls')
patterns = urls.patterns
url = urls.url


urlpatterns = patterns('',
                       url(r'^$', views.PoolsIndexView.as_view(),
                           name='index'),
                       url(r'^$', views.PoolsIndexView.as_view(),
                           name='pools'),
                       url(r'^create-pool$',
                           views.CreateGroupView.as_view(),
                           name='create-pool'),
                       # url(r'^configure-cluster$',
                       #     views.ConfigureClusterView.as_view(),
                       #     name='configure-cluster'),
                       url(r'^(?P<pool_id>[^/]+)/%s$' % 'detail',
                           views.GroupDetailsView.as_view(),
                           name='detail'))
                       # url(r'^(?P<cluster_id>[^/]+)/scale$',
                       #     views.ScaleClusterView.as_view(),
                       #     name='scale'))
