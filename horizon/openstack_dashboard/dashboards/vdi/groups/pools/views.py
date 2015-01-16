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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon import tabs
from horizon import workflows
from horizon.utils import memoized
from horizon import exceptions

LOG = logging.getLogger(__name__)

from openstack_dashboard import api

from vdidashboard.api.client import client as vdiclient
from sahvdidashboardols import tables as pool_tables
import vdidashboards.tabs as _tabs
import vdidashboardorkflows.create as create_flow


class PoolsIndexView(tables.DataTableView):
    table_class = pool_tables.PoolsTable
    template_name = 'pools/pools.html'

    def get_data(self):
        try:
            vdi = vdiclient(self.request)
            pools = vdi.pools.list()
        except Exception:
            pools = []
            exceptions.handle(self.request,
                              _('Unable to retrieve pools.'))
        if pools:
            for pool in pools:
                # LOG.info("image-ref = %s", group.image_ref)
                try:
                    image = api.glance.image_get(self.request, pool.image_ref)
                except Exception:
                    image = []
                    msg = _('Unable to retrieve image for the group.')
                    exceptions.handle(self.request, msg)
                if image:
                    pool.image_name = image.name
                else:
                    pool.image_name = '-'
        return pools


class PoolDetailsView(tabs.TabView):
    tab_group_class = _tabs.PoolDetailsTabs
    template_name = 'pools/details.html'
    failure_url = reverse_lazy('horizon:vdi:pools')

    def get_context_data(self, **kwargs):
        context = super(PoolDetailsView, self).get_context_data(**kwargs)
        # context["images_bak"] = self._get_data()
        return context

    @memoized.memoized_method
    def _get_data(self):
        pass




class CreateGroupView(workflows.WorkflowView):
    workflow_class = create_flow.CreateGroup
    success_url = "horizon:vdi:groups:create-images_bak"
    classes = "ajax-modal"
    template_name = "groups/create.html"

