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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon import tabs
from horizon import forms
from horizon import workflows
from horizon.utils import memoized
from horizon import exceptions

LOG = logging.getLogger(__name__)

from openstack_dashboard import api
import openstack_dashboard.api.keystone as keystone

from openstack_dashboard.dashboards.vdi.api.client import client as vdiclient
from openstack_dashboard.dashboards.vdi.pools import tables as pool_tables
# import openstack_dashboard.dashboards.vdi.pools.tabs as _tabs
import openstack_dashboard.dashboards.vdi.pools.forms as project_forms
import openstack_dashboard.dashboards.vdi.pools.instances.tables as instance_table


class PoolsIndexView(tables.DataTableView):
    table_class = pool_tables.PoolsTable
    template_name = 'pools/pools.html'

    def get_data(self):
        domain_context = self.request.session.get('domain_context', None)
        user = self.request.user
        try:
            vdi = vdiclient(self.request)
            if domain_context:
                domain = domain_context
            else:
                domain = user.user_domain_id
            pools = vdi.pools.list_domain_pools(domain)
            if not user.is_superuser:
                pools = [pool for pool in pools if user.project_id in pool.vdi_group]
        except Exception:
            pools = []
            exceptions.handle(self.request, _('Unable to retrieve pools.'))
        if pools:
            for pool in pools:
                try:
                    image = api.glance.image_get(self.request, pool.image_ref)
                except Exception:
                    image = []
                    msg = _('Unable to retrieve image for the pool.')
                    exceptions.handle(self.request, msg)
                if image:
                    pool.image_name = image.name
                else:
                    pool.image_name = '-'
        return sorted(pools, key=lambda x: x.name)


# class PoolDetailsView(tabs.TabView):
#     tab_group_class = _tabs.PoolDetailsTabs
#     template_name = 'pools/details.html'
#     failure_url = reverse_lazy('horizon:vdi:pools')
#
#     def get_context_data(self, **kwargs):
#         context = super(PoolDetailsView, self).get_context_data(**kwargs)
#         # context["pool"] = self._get_data()
#         return context
#
#     @memoized.memoized_method
#     def _get_data(self):
#         pass


class PoolDetailsView(tables.MultiTableView):
    # table_classes = (image_tables.ImagesTable, )
    table_classes = (instance_table.InstancesTable,)
    template_name = 'pools/details2.html'
    failure_url = reverse_lazy('horizon:vdi:pools')

    def get_instances_data(self):
        user_id = self.request.user.id
        try:
            # pool = self._get_data()
            servers = api.nova.server_list(self.request)
            instances = servers[0]
            instance_list = []
            for instance in instances:
                # if hasattr(instance, "name"):
                #     if pool.name in instance.name:
                #         instance_list.append(instance)
                if user_id in instance.user_id:
                    instance_list.append(instance)
        except Exception:
            instance_list = []
            msg = _('Instance list can not be retrieved.')
            exceptions.handle(self.request, msg)
        # return sorted(user_list, key=lambda x: x.name)
        # import pdb; pdb.set_trace()
        return sorted(instance_list, key=lambda x: x.name)

    @memoized.memoized_method
    def _get_data(self):
        try:
            pool_id = self.kwargs['pool_id']
            vdi = vdiclient(self.request)
            pool = vdi.pools.get(pool_id)
        except Exception:
            redirect = self.failure_url
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'pool "%s".') % pool_id,
                              redirect=redirect)
        if pool:
            try:
                image = api.glance.image_get(self.request, pool.image_ref)
            except Exception:
                image = []
                msg = _('Unable to retrieve image for the pool.')
                exceptions.handle(self.request, msg)
            if image:
                pool.image_name = image.name
            else:
                pool.image_name = '-'
        return pool

    def get_context_data(self, **kwargs):
        context = super(PoolDetailsView, self).get_context_data(**kwargs)
        context["pool"] = self._get_data()
        return context


class CreatePoolView(forms.ModalFormView):
    form_class = project_forms.CreatePoolForm
    template_name = "pools/create.html"
    success_url = reverse_lazy("horizon:vdi:pools:index")

    # def dispatch(self, *args, **kwargs):
    #     return super(CreatePoolView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        domain_context = self.request.session.get('domain_context', None)
        if domain_context:
            domain = domain_context
        else:
            domain = self.request.user.user_domain_id
        domain = keystone.domain_get(self.request, domain)
        return {'domain_id': domain.id,
                'domain_name': domain.name}


class UpdatePoolView(forms.ModalFormView):
    form_class = project_forms.UpdatePoolForm
    template_name = 'pools/update.html'
    success_url = reverse_lazy('horizon:vdi:pools:index')

    @memoized.memoized_method
    def get_object(self):
        try:
            vdi = vdiclient(self.request)
            return vdi.pools.get(self.kwargs['pool_id'])
        except Exception:
            msg = _('Unable to update pool.')
            url = reverse("horizon:vdi:pools:index")
            exceptions.handle(self.request, msg, redirect=url)

    def get_context_data(self, **kwargs):
        context = super(UpdatePoolView, self).get_context_data(**kwargs)
        context['pool'] = self.get_object()
        return context

    def get_initial(self):
        pool = self.get_object()
        return {'domain_id': pool.domain_id,
                'domain_name': keystone.domain_get(self.request, pool.domain_id).name if pool.domain_id else '',
                'id': pool.id,
                'description': pool.description,
                'name': pool.name,
                'image_ref': pool.image_ref,
                'vdi_group': pool.vdi_group}
