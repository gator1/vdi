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


from openstack_dashboard.dashboards.vdi.image_registry.views import EditTagsView
from openstack_dashboard.dashboards.vdi.image_registry.views import ImageRegistryView
from openstack_dashboard.dashboards.vdi.image_registry.views import RegisterImageView
from openstack_dashboard.dashboards.vdi.utils import importutils

urls = importutils.import_any('django.conf.urls.defaults',
                              'django.conf.urls')
patterns = urls.patterns
url = urls.url


urlpatterns = patterns('',
                       url(r'^$', ImageRegistryView.as_view(),
                           name='index'),
                       url(r'^$', ImageRegistryView.as_view(),
                           name='image_registry'),
                       url(r'^edit_tags/(?P<image_id>[^/]+)/$',
                           EditTagsView.as_view(),
                           name='edit_tags'),
                       url(r'^register/$',
                           RegisterImageView.as_view(),
                           name='register'),
                       )
