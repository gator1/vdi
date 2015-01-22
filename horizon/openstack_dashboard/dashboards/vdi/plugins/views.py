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


from horizon import tables
from horizon import tabs
import logging

from openstack_dashboard.dashboards.vdi.api.client import client as vdiclient
from openstack_dashboard.dashboards.vdi.plugins.tables import PluginsTable
from openstack_dashboard.dashboards.vdi.plugins.tabs import PluginDetailsTabs

LOG = logging.getLogger(__name__)


class PluginsView(tables.DataTableView):
    table_class = PluginsTable
    template_name = 'plugins/plugins.html'

    def get_data(self):
        vdi = vdiclient(self.request)
        return vdi.plugins.list()


class PluginDetailsView(tabs.TabView):
    tab_group_class = PluginDetailsTabs
    template_name = 'plugins/details.html'

    def get_context_data(self, **kwargs):
        context = super(PluginDetailsView, self).get_context_data(**kwargs)
        return context

    def get_data(self):
        pass
