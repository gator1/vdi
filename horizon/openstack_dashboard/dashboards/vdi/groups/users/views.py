# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import operator
import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters  # noqa

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized

LOG = logging.getLogger(__name__)

from openstack_dashboard import api

# from openstack_dashboard.dashboards.admin.users \
#     import forms as project_forms
# from openstack_dashboard.dashboards.admin.users \
#     import tables as project_tables
from openstack_dashboard.dashboards.vdi.users import forms as project_forms
from saharadashboard.users import tables as project_tables


class IndexView(tables.DataTableView):
    table_class = project_tables.UsersTable
    template_name = 'vdi/users/index.html'

    def get_data(self):
        users = []
        domain_context = self.request.session.get('domain_context', None)
        try:
            user = self.request.user
            users = api.keystone.user_list(self.request,
                                           domain=domain_context,
                                           project=user.tenant_id)
            # remove admin from users
            for item in users:
                if item.username == "admin":
                    users.remove(item)

        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve user list.'))
        return sorted(users, key=lambda x: x.name)


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateUserForm
    # template_name = 'admin/users/update.html'
    template_name = 'vdi/users/update.html'
    success_url = reverse_lazy('horizon:vdi:users:index')

    @method_decorator(sensitive_post_parameters('password',
                                                'confirm_password'))
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.keystone.user_get(self.request, self.kwargs['user_id'],
                admin=True)
        except Exception:
            redirect = reverse("horizon:vdi:users:index")
            exceptions.handle(self.request,
                              _('Unable to update user.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['user'] = self.get_object()
        return context

    def get_initial(self):
        user = self.get_object()
        domain_id = getattr(user, "domain_id", None)
        domain_name = ''
        # Retrieve the domain name where the project belong
        if api.keystone.VERSIONS.active >= 3:
            try:
                domain = api.keystone.domain_get(self.request,
                                                    domain_id)
                domain_name = domain.name
            except Exception:
                exceptions.handle(self.request,
                    _('Unable to retrieve project domain.'))
        return {'domain_id': domain_id,
                'domain_name': domain_name,
                'id': user.id,
                'name': user.name,
                'project': user.project_id,
                'email': getattr(user, 'email', None)}


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateUserForm
    template_name = 'admin/users/create.html'
    success_url = reverse_lazy('horizon:admin:users:index')

    @method_decorator(sensitive_post_parameters('password',
                                                'confirm_password'))
    def dispatch(self, *args, **kwargs):
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        try:
            roles = api.keystone.role_list(self.request)
        except Exception:
            redirect = reverse("horizon:admin:users:index")
            exceptions.handle(self.request,
                              _("Unable to retrieve user roles."),
                              redirect=redirect)
        roles.sort(key=operator.attrgetter("id"))
        kwargs['roles'] = roles
        return kwargs

    def get_initial(self):
        # Set the domain of the user
        domain = api.keystone.get_default_domain(self.request)
        default_role = api.keystone.get_default_role(self.request)
        return {'domain_id': domain.id,
                'domain_name': domain.name,
                'role_id': getattr(default_role, "id", None)}
