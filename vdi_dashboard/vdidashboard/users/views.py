# Copyright 2014 Huawei Technologies.
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
from vdidashboard.users import forms as project_forms
from vdidashboard.users import tables as project_tables


class IndexView(tables.DataTableView):
    table_class = project_tables.UsersTable
    template_name = 'vdi/users/index.html'

    def get_data(self):
        users = []
        domain_context = self.request.session.get('domain_context', None)
        try:
            user = self.request.user
            # LOG.info("request user = %s", self.request)
            # users = api.keystone.user_list(self.request,
            #                                domain=domain_context,
            #                                project=user.tenant_id)
            if user.is_superuser:
                all_users = api.keystone.user_list(self.request,
                                                   domain=domain_context)
                for u in all_users:
                    # Works for keystone v3 with multi-tenants
                    # if getattr(u, 'default_project_id', None) == user.tenant_id:
                    #     users.append(u)
                    # Works for single-tenant
                    if getattr(u, 'tenantId', None) == user.tenant_id:
                        users.append(u)
                    # import pdb; pdb.set_trace()
                # remove admin from users
                # for item in users:
                #     if item.name == "admin":
                #         users.remove(item)
            else:
                user.name = user.username
                users = [user]
        except Exception:
            exceptions.handle(self.request, _('Unable to retrieve user list.'))

        # import pdb; pdb.set_trace()

        return sorted(users, key=lambda x: x.name)


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateUserForm
    # template_name = 'admin/users/update.html'
    # template_name = 'vdi/users/update.html'
    template_name = 'users/update.html'
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
                'email': getattr(user, 'email', None),
                'vdi_group': getattr(user, 'vdi_group', None)}


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateUserForm
    template_name = 'users/create.html'
    success_url = reverse_lazy('horizon:vdi:users:index')

    @method_decorator(sensitive_post_parameters('password',
                                                'confirm_password'))
    def dispatch(self, *args, **kwargs):
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        try:
            roles = api.keystone.role_list(self.request)
        except Exception:
            redirect = reverse("horizon:vdi:users:index")
            exceptions.handle(self.request,
                              _("Unable to retrieve user roles."),
                              redirect=redirect)
        roles.sort(key=operator.attrgetter("id"))
        kwargs['roles'] = roles
        return kwargs

    def get_initial(self):
        # Set the domain of the user
        domain = api.keystone.get_default_domain(self.request)
        user = self.request.user
        default_role = api.keystone.get_default_role(self.request)
        roles = api.keystone.role_list(self.request)
        for role in roles:
            if role.name == "vdi":
                vdi_role = role
                break
        return {'domain_id': domain.id,
                'domain_name': domain.name,
                'role_id': vdi_role.id or default_role.id,
                'project': user.project_id}
