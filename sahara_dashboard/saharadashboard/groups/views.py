# Copyright (c) 2013 Mirantis Inc.
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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon import forms
from horizon import tabs
from horizon import workflows
from horizon.utils import memoized
from horizon import exceptions

LOG = logging.getLogger(__name__)

from openstack_dashboard import api

from saharadashboard.api.client import client as vdiclient
from saharadashboard.groups import tables as group_tables
import saharadashboard.groups.tabs as _tabs
import saharadashboard.groups.forms as project_forms
import saharadashboard.groups.workflows.create as create_flow
# import saharadashboard.groups.workflows.scale as scale_flow
import saharadashboard.groups.images.tables as image_tables
import saharadashboard.groups.pools.tables as pool_tables
import saharadashboard.groups.users.tables as user_tables


class GroupsView(tables.DataTableView):
    table_class = group_tables.GroupsTable
    template_name = 'groups/groups.html'

    def get_data(self):
        try:
            vdi = vdiclient(self.request)
            groups = vdi.groups.list()
            # pools = vdi.pools.list_group_pools(groups[8].id)
            # groups = vdi.groups.list_user_groups('1')

            # import pdb; pdb.set_trace()

        except Exception:
            groups = []
            exceptions.handle(self.request, _('Unable to retrieve groups.'))
        # if groups:
        #     for group in groups:
        #         # LOG.info("image-ref = %s", group.image_ref)
        #         try:
        #             image = api.glance.image_get(self.request, group.image_ref)
        #         except Exception:
        #             image = []
        #             msg = _('Unable to retrieve image for the group.')
        #             exceptions.handle(self.request, msg)
        #         if image:
        #             group.image_name = image.name
        #         else:
        #             group.image_name = '-'
                # group.image_name = 'Test'
                # group.image_name = api.glance.image_get(self.request, group.image_ref)
                # # print 'group=', group.image_name
                # raw_input('group pause')
        return sorted(groups, key=lambda x: x.name)


# class GroupDetailsView(tabs.TabView):
#     tab_group_class = _tabs.GroupDetailsTabs
#     template_name = 'groups/details.html'
#     failure_url = reverse_lazy('horizon:vdi:groups')
#
#     def get_context_data(self, **kwargs):
#         context = super(GroupDetailsView, self).get_context_data(**kwargs)
#         # context["images_bak"] = self._get_data()
#
#         LOG.info("context = %s", context)
#
#         return context
#
#     @memoized.memoized_method
#     def _get_data(self):
#         pass


class GroupDetailsView(tables.MultiTableView):
    # table_classes = (image_tables.ImagesTable, )
    table_classes = (pool_tables.PoolsTable, user_tables.UsersTable)
    template_name = 'groups/details2.html'
    # failure_url = reverse_lazy('horizon:vdi:groups')

    def get_images_data(self):
        try:
            group_id = self.kwargs['group_id']
            vdi = vdiclient(self.request)
            images = vdi.groups.get_images(group_id)
        except Exception:
            images = []
            msg = _('Image list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return images

    def get_pools_data(self):
        try:
            group_id = self.kwargs['group_id']
            vdi = vdiclient(self.request)
            pools = vdi.pools.list()
            pool_list = []
            for pool in pools:
                if group_id in pool.vdi_group:
                    pool_list.append(pool)
        except Exception:
            pool_list = []
            msg = _('Pool list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return pool_list

    def get_users_data(self):
        try:
            group_id = self.kwargs['group_id']
            domain_context = self.request.session.get('domain_context', None)
            user = self.request.user
            users = api.keystone.user_list(self.request,
                                           domain=domain_context,
                                           project=user.tenant_id)
            user_list = []
            for user in users:
                if hasattr(user, "vdi_group"):
                    if group_id in user.vdi_group:
                        user_list.append(user)
        except Exception:
            user_list = []
            msg = _('User list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return sorted(user_list, key=lambda x: x.name)

    @memoized.memoized_method
    def _get_data(self):
        try:
            group_id = self.kwargs['group_id']
            vdi = vdiclient(self.request)
            group = vdi.groups.get(group_id)
        except Exception:
            redirect = self.failure_url
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'group "%s".') % group_id,
                              redirect=redirect)
        return group

    def get_context_data(self, **kwargs):
        context = super(GroupDetailsView, self).get_context_data(**kwargs)
        context["group"] = self._get_data()
        return context


# class CreateGroupView(workflows.WorkflowView):
#     workflow_class = create_flow.CreateGroup
#     success_url = "horizon:vdi:groups:create-images_bak"
#     classes = "ajax-modal"
#     template_name = "groups/create.html"


class CreateGroupView(forms.ModalFormView):
    form_class = project_forms.CreateGroupForm
    template_name = "groups/create.html"
    success_url = reverse_lazy("horizon:vdi:groups:index")

    # def dispatch(self, *args, **kwargs):
    #     return super(CreateGroupView, self).dispatch(*args, **kwargs)


class UpdateGroupView(forms.ModalFormView):
    form_class = project_forms.UpdateGroupForm
    template_name = 'groups/update.html'
    success_url = reverse_lazy('horizon:vdi:groups:index')

    @memoized.memoized_method
    def get_object(self):
        try:
            vdi = vdiclient(self.request)
            return vdi.groups.get(self.kwargs['group_id'])
        except Exception:
            msg = _('Unable to update group.')
            url = reverse("horizon:vdi:groups:index")
            exceptions.handle(self.request, msg, redirect=url)

    def get_context_data(self, **kwargs):
        context = super(UpdateGroupView, self).get_context_data(**kwargs)
        context['group'] = self.get_object()
        return context

    def get_initial(self):
        group = self.get_object()
        return {'id': group.id,
                'description': group.description,
                'name': group.name}