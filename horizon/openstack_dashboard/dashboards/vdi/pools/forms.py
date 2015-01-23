# Copyright (c) 2014 Huawei Technologies.
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

import logging

from django.forms import ValidationError  # noqa
from django import http
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import validators
import openstack_dashboard.api.keystone as keystone

from openstack_dashboard import api
from openstack_dashboard.dashboards.vdi.api.client import client as vdiclient


LOG = logging.getLogger(__name__)


class BaseUserForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(BaseUserForm, self).__init__(request, *args, **kwargs)

        # Populate project choices
        # project_choices = []

        # If the user is already set (update action), list only projects which
        # the user has access to.
        # group_id = kwargs['initial'].get('id', None)
        # domain_id = kwargs['initial'].get('domain_id', None)
        # projects, has_more = api.keystone.tenant_list(request,
        #                                               domain=domain_id,
        #                                               user=group_id)
        #
        # LOG.info("projects = %s", projects)
        #
        # for project in projects:
        #     if project.enabled:
        #         project_choices.append((project.id, project.name))
        # if not project_choices:
        #     project_choices.insert(0, ('', _("No available projects")))
        # elif len(project_choices) > 1:
        #     project_choices.insert(0, ('', _("Select a project")))
        # self.fields['project'].choices = project_choices

        # self.fields['domain_id'] = "test"

        domain_context = self.request.session.get('domain_context', None)

        # # Populate domain choices
        # domain_choices = []
        # domains = keystone.domain_list(self.request)
        # temp_list = [(x.id, x.name) for x in domains]
        # for v in sorted(temp_list, key=lambda x: x[1]):
        #     domain_choices.append(v)
        # self.fields['domain_id'].choices = domain_choices

        # Populate image choices
        image_choices = []
        filters = {'is_public': None}
        images = api.glance.image_list_detailed(request, filters=filters)
        temp_list = [(x.id, x.name) for x in images[0]]
        for v in sorted(temp_list, key=lambda y: y[1]):
            image_choices.append(v)
        self.fields['image_ref'].choices = image_choices

        # Populate VDI group choices
        group_choices = []
        vdi = vdiclient(self.request)
        groups = vdi.groups.list()
        if domain_context:
            temp_list = [(x.id, x.name) for x in groups if x.domain_id == domain_context]
        else:
            temp_list = [(x.id, x.name) for x in groups]
        for v in sorted(temp_list, key=lambda y: y[1]):
            group_choices.append(v)
        self.fields['vdi_group'].choices = group_choices

        # # Populate project choices
        # project_choices = []
        # if domain_context:
        #     domain = domain_context
        # else:
        #     domain = self.request.user.user_domain_id
        # projects, has_more = api.keystone.tenant_list(self.request, domain=domain)
        # temp_list = [(x.id, x.name) for x in projects]
        # for v in sorted(temp_list, key=lambda y: y[1]):
        #     project_choices.append(v)
        # self.fields['vdi_group'].choices = project_choices

    def clean(self):
        # Check to make sure password fields match.
        data = super(forms.Form, self).clean()
        if 'password' in data:
            if data['password'] != data.get('confirm_password', None):
                raise ValidationError(_('Passwords do not match.'))
        return data


ADD_PROJECT_URL = "horizon:admin:projects:create"


class CreatePoolForm(BaseUserForm):
    # Hide the domain_id and domain_name by default
    domain_id = forms.CharField(label=_("Domain ID"),
                                required=False,
                                widget=forms.HiddenInput())
    # domain_id = forms.ChoiceField(label=_("Domain"),
    #                               required=False)
    domain_name = forms.CharField(label=_("Domain Name"),
                                  required=True)
                                  # widget=forms.HiddenInput())
    name = forms.CharField(max_length=255, label=_("Pool Name"))
    description = forms.CharField(label=_("Description"))
    image_ref = forms.ChoiceField(label=_("Image"))
    vdi_group = forms.MultipleChoiceField(label=_("Department"),
                                          required=True)

    def __init__(self, *args, **kwargs):
        super(CreatePoolForm, self).__init__(*args, **kwargs)

        if api.keystone.keystone_can_edit_user() is False:
            for field in ('name', 'email', 'password', 'confirm_password'):
                self.fields.pop(field)
        # For keystone V3, display the two fields in read-only
        if api.keystone.VERSIONS.active >= 3:
            domain_context = self.request.session.get('domain_context', None)
            if domain_context:
                readonlyInput = forms.TextInput(attrs={'readonly': 'readonly'})
                self.fields["domain_id"].widget = forms.HiddenInput()
                self.fields["domain_name"].widget = readonlyInput

    # We have to protect the entire "data" dict because it contains the
    # password and confirm_password strings.
    # @sensitive_variables('data')
    # def handle(self, request, data):
    @staticmethod
    def handle(request, data):
        try:
            domain_id = data.pop('domain_id')
            name = data.pop('name')
            description = data.pop('description')
            LOG.info('Creating pool with name "%s"' % name)
            vdi = vdiclient(request)
            pool = vdi.pools.create(domain_id, name, description)
            messages.success(request,
                             _('User "%s" was successfully created.' % name))
            if data:
                try:
                    pool = vdi.pools.update(pool.id, data)
                except Exception:
                    exceptions.handle(request,
                                      _('Unable to update pool.'))
            return pool
        except Exception:
            exceptions.handle(request, _('Unable to create pool.'))


class UpdatePoolForm(BaseUserForm):
    # Hide the domain_id and domain_name by default
    domain_id = forms.CharField(label=_("Domain ID"),
                                required=False,
                                widget=forms.HiddenInput())
    domain_name = forms.CharField(label=_("Domain Name"),
                                  required=False,
                                  widget=forms.HiddenInput())
    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput)
    name = forms.CharField(label=_("Pool Name"))
    description = forms.CharField(label=_("Description"))
    image_ref = forms.ChoiceField(label=_("Image"), required=True)
    vdi_group = forms.MultipleChoiceField(label=_("Department"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePoolForm, self).__init__(request, *args, **kwargs)

        if api.keystone.keystone_can_edit_user() is False:
            for field in ('name', 'email', 'password', 'confirm_password'):
                self.fields.pop(field)
                # For keystone V3, display the two fields in read-only
        if api.keystone.VERSIONS.active >= 3:
            readonlyInput = forms.TextInput(attrs={'readonly': 'readonly'})
            self.fields["domain_id"].widget = readonlyInput
            self.fields["domain_name"].widget = readonlyInput

    # @sensitive_variables('data')
    # def handle(self, request, data):
    @staticmethod
    def handle(request, data):
        pool_id = data.pop('id')
        try:
            vdi = vdiclient(request)
            response = vdi.pools.update(pool_id, data)
            messages.success(request,
                             _('Pool has been updated successfully.'))
        except Exception:
            response = exceptions.handle(request, ignore=True)
            messages.error(request, _('Unable to update the pool.'))
        if isinstance(response, http.HttpResponse):
            return response
        else:
            return True
