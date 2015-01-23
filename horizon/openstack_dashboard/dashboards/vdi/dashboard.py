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

import logging

from django.utils.translation import ugettext as _
import horizon

from openstack_dashboard.dashboards.vdi.utils import compatibility

LOG = logging.getLogger(__name__)


class VDIDashboard(horizon.Dashboard):
    name = _("VDI")
    slug = "vdi"
    panels = ('groups',
              'pools',
              'users')
    default_panel = 'groups'
    nav = True
    supports_tenants = True
    # permissions = ('openstack.roles.vdi',)


horizon.register(VDIDashboard)

LOG.info('VDI recognizes Dashboard release as "%s"' %
         compatibility.get_dashboard_release())
