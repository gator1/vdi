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
import saharavdidashboards.tabs as _tabs
import saharadasvdidashboardorkflows.create as create_flow
# import saharadashboard.groups.images.tables as image_tables


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


# class GroupDetailsView(tables.MultiTableView):
#     table_classes = (image_tables.ImagesTable, )
#     # tab_group_class = _tabs.GroupDetailsTabs
#     template_name = 'groups/details2.html'
#     failure_url = reverse_lazy('horizon:vdi:groups')
#
#     def get_images_data(self):
#         try:
#             group_id = self.kwargs['group_id']
#             vdi = vdiclient(self.request)
#             images_bak = vdi.groups.get_image(group_id)
#         except Exception:
#             images_bak = []
#             msg = _('Image list can not be retrieved.')
#             exceptions.handle(self.request, msg)
#         return images_bak
#
#     @memoized.memoized_method
#     def _get_data(self):
#         try:
#             group_id = self.kwargs['group_id']
#             vdi = vdiclient(self.request)
#             group = vdi.groups.get(group_id)
#         except Exception:
#             redirect = self.failure_url
#             exceptions.handle(self.request,
#                               _('Unable to retrieve details for '
#                                 'group "%s".') % group_id,
#                               redirect=redirect)
#         return group
#
#     def get_context_data(self, **kwargs):
#         context = super(GroupDetailsView, self).get_context_data(**kwargs)
#         context["group"] = self._get_data()
#         return context


class CreateGroupView(workflows.WorkflowView):
    workflow_class = create_flow.CreateGroup
    success_url = "horizon:vdi:groups:create-images_bak"
    classes = "ajax-modal"
    template_name = "groups/create.html"


# class ConfigureClusterView(workflows.WorkflowView):
#     workflow_class = create_flow.ConfigureCluster
#     success_url = "horizon:sahara:clusters"
#     template_name = "clusters/configure.html"
#
#
# class ScaleClusterView(workflows.WorkflowView):
#     workflow_class = scale_flow.ScaleCluster
#     success_url = "horizon:sahara:clusters"
#     classes = ("ajax-modal")
#     template_name = "clusters/scale.html"
#
#     def get_context_data(self, **kwargs):
#         context = super(ScaleClusterView, self)\
#             .get_context_data(**kwargs)
#
#         context["cluster_id"] = kwargs["cluster_id"]
#         return context
#
#     def get_object(self, *args, **kwargs):
#         if not hasattr(self, "_object"):
#             template_id = self.kwargs['cluster_id']
#             sahara = vdiclient(self.request)
#             template = sahara.cluster_templates.get(template_id)
#             self._object = template
#         return self._object
#
#     def get_initial(self):
#         initial = super(ScaleClusterView, self).get_initial()
#         initial.update({'cluster_id': self.kwargs['cluster_id']})
#         return initial
