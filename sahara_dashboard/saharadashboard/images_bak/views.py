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

from horizon import tables
from horizon import tabs
from horizon import exceptions
from horizon import workflows

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

# from saharadashboard.api.client import client as saharaclient
from saharadashboard.api.client import client as vdiclient

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.images.images import views

from openstack_dashboard.dashboards.admin.images import forms
from openstack_dashboard.dashboards.admin.images \
    import tables as project_tables

from saharadashboard.images_bak.tables import ImagesTable, AdminImagesTable
import saharadashboard.images_bak.tabs as _tabs
# import saharadashboard.images_bak.workflows.create as create_flow
# import saharadashboard.images_bak.workflows.scale as scale_flow

LOG = logging.getLogger(__name__)


class ImagesView(tables.DataTableView):
    # table_class = ImagesTable
    table_class = AdminImagesTable
    template_name = 'images_bak/images_bak.html'

    def get_data(self):
        vdi = vdiclient(self.request)
        images = vdi.groups.list()
        return images


class ImageDetailsView(tabs.TabView):
    tab_group_class = _tabs.ImageDetailsTabs
    template_name = 'images_bak/details.html'

    def get_context_data(self, **kwargs):
        context = super(ImageDetailsView, self)\
            .get_context_data(**kwargs)
        return context

    def get_data(self):
        pass


class IndexView(tables.DataTableView):
    table_class = project_tables.AdminImagesTable
    # template_name = 'admin/images_bak/index.html'
    template_name = 'images_bak/images_bak.html'

    def has_more_data(self, table):
        return self._more

    def get_data(self):
        images = []
        filters = {'is_public': None}
        marker = self.request.GET.get(
            project_tables.AdminImagesTable._meta.pagination_param, None)
        try:
            # images_bak, self._more = api.glance.image_list_detailed(self.request,
            #                                                 marker=marker,
            #                                                 paginate=True,
            #                                                 filters=filters)
            images, self._more = api.glance.image_list_detailed(self.request,
                                                            marker=marker,
                                                            paginate=True)
                                                            # filters=filters)
        except Exception:
            self._more = False
            msg = _('Unable to retrieve image list.')
            exceptions.handle(self.request, msg)
        return images


class CreateView(views.CreateView):
    template_name = 'admin/images_bak/create.html'
    form_class = forms.AdminCreateImageForm
    success_url = reverse_lazy('horizon:admin:images_bak:index')


class UpdateView(views.UpdateView):
    template_name = 'admin/images_bak/update.html'
    form_class = forms.AdminUpdateImageForm
    success_url = reverse_lazy('horizon:admin:images_bak:index')


class DetailView(views.DetailView):
    """Admin placeholder for image detail view."""
    pass
