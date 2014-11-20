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

import logging

from django.forms import ValidationError  # noqa
from django import http
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import validators

from openstack_dashboard import api
from vdidashboard.api.client import client as vdiclient


LOG = logging.getLogger(__name__)


class BaseUserForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(BaseUserForm, self).__init__(request, *args, **kwargs)

        # Populate project choices
        project_choices = []

        # If the user is already set (update action), list only projects which
        # the user has access to.
        user_id = kwargs['initial'].get('id', None)
        domain_id = kwargs['initial'].get('domain_id', None)
        projects, has_more = api.keystone.tenant_list(request,
                                                      domain=domain_id,
                                                      user=user_id)
        for project in projects:
            if project.enabled:
                project_choices.append((project.id, project.name))
        if not project_choices:
            project_choices.insert(0, ('', _("No available projects")))
        elif len(project_choices) > 1:
            project_choices.insert(0, ('', _("Select a project")))
        self.fields['project'].choices = project_choices

        # Populate group choices
        group_choices = []

        vdi = vdiclient(self.request)
        groups = vdi.groups.list()
        temp_list = []
        for group in groups:
            temp_list.append((group.id, group.name))
        for v in sorted(temp_list, key=lambda x: x[1]):
            group_choices.append(v)
        self.fields['vdi_group'].choices = group_choices

        # # Populate pool choices
        # pool_choices = []
        #
        # vdi = vdiclient(self.request)
        # pools = vdi.pools.list()
        # temp_list = []
        # for pool in pools:
        #     temp_list.append((pool.id, pool.name))
        # for v in sorted(temp_list, key=lambda x: x[1]):
        #     pool_choices.append(v)
        # self.fields['vdi_pool'].choices = pool_choices

    def clean(self):
        # Check to make sure password fields match.
        data = super(forms.Form, self).clean()
        if 'password' in data:
            if data['password'] != data.get('confirm_password', None):
                raise ValidationError(_('Passwords do not match.'))
        return data


ADD_PROJECT_URL = "horizon:admin:projects:create"


class CreateUserForm(BaseUserForm):
    # Hide the domain_id and domain_name by default
    domain_id = forms.CharField(label=_("Domain ID"),
                                required=False,
                                widget=forms.HiddenInput())
    domain_name = forms.CharField(label=_("Domain Name"),
                                  required=False,
                                  widget=forms.HiddenInput())
    name = forms.CharField(max_length=255, label=_("User Name"))
    email = forms.EmailField(label=_("Email"),
                             required=False)
    password = forms.RegexField(label=_("Password"),
                                widget=forms.PasswordInput(render_value=False),
                                regex=validators.password_validator(),
                                error_messages={'invalid': validators.password_validator_msg()})
    confirm_password = forms.CharField(label=_("Confirm Password"),
                                       widget=forms.PasswordInput(render_value=False))
    role_id = forms.ChoiceField(label=_("Role"),
                                widget=forms.HiddenInput())
    project = forms.DynamicChoiceField(label=_("Primary Project"),
                                       add_item_link=ADD_PROJECT_URL,
                                       widget=forms.HiddenInput())
    vdi_group = forms.MultipleChoiceField(label=_("VDI Group"),
                                          required=True)

    def __init__(self, *args, **kwargs):
        roles = kwargs.pop('roles')
        super(CreateUserForm, self).__init__(*args, **kwargs)
        role_choices = [(role.id, role.name) for role in roles]
        self.fields['role_id'].choices = sorted(role_choices, key=lambda x: x[1].lower())

        # For keystone V3, display the two fields in read-only
        if api.keystone.VERSIONS.active >= 3:
            readonlyInput = forms.TextInput(attrs={'readonly': 'readonly'})
            self.fields["domain_id"].widget = readonlyInput
            self.fields["domain_name"].widget = readonlyInput

    # We have to protect the entire "data" dict because it contains the
    # password and confirm_password strings.
    @sensitive_variables('data')
    def handle(self, request, data):
        domain = api.keystone.get_default_domain(self.request)
        try:
            LOG.info('Creating user with name "%s"' % data['name'])
            if "email" in data:
                data['email'] = data['email'] or None
            new_user = api.keystone.user_create(request,
                                                name=data['name'],
                                                email=data['email'],
                                                password=data['password'],
                                                project=data['project'],
                                                enabled=True,
                                                domain=domain.id)
            messages.success(request,
                             _('User "%s" was successfully created.')
                             % data['name'])
            if data['role_id']:
                try:
                    api.keystone.add_tenant_user_role(request,
                                                      data['project'],
                                                      new_user.id,
                                                      data['role_id'])
                except Exception:
                    exceptions.handle(request,
                                      _('Unable to add user '
                                        'to primary project.'))
            if data['vdi_group']:
                try:
                    api.keystone.user_update(request, new_user.id,
                                             password=data['password'],
                                             project=data['project'],
                                             vdi_group=data['vdi_group'])
                except Exception:
                    exceptions.handle(request,
                                      _("Unable to update user's VDI group"))
            return new_user
        except Exception:
            exceptions.handle(request, _('Unable to create user.'))


class UpdateUserForm(BaseUserForm):
    # Hide the domain_id and domain_name by default
    domain_id = forms.CharField(label=_("Domain ID"),
                                required=False,
                                widget=forms.HiddenInput())
    domain_name = forms.CharField(label=_("Domain Name"),
                                  required=False,
                                  widget=forms.HiddenInput())
    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput)
    name = forms.CharField(label=_("User Name"))
    email = forms.EmailField(
        label=_("Email"),
        required=False)
    password = forms.RegexField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=False),
        regex=validators.password_validator(),
        required=False,
        error_messages={'invalid': validators.password_validator_msg()})
    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(render_value=False),
        required=False)
    # role_id = forms.ChoiceField(label=_("Role"))
    project = forms.ChoiceField(label=_("Primary Project"))
    vdi_group = forms.MultipleChoiceField(label=_("VDI Group"),
                                          required=True)
    # vdi_pool = forms.MultipleChoiceField(label=_("VDI Pool"),
    #                                      required=True)

    def __init__(self, request, *args, **kwargs):
        super(UpdateUserForm, self).__init__(request, *args, **kwargs)

        if api.keystone.keystone_can_edit_user() is False:
            for field in ('name', 'email', 'password', 'confirm_password'):
                self.fields.pop(field)
                # For keystone V3, display the two fields in read-only
        if api.keystone.VERSIONS.active >= 3:
            readonlyInput = forms.TextInput(attrs={'readonly': 'readonly'})
            self.fields["domain_id"].widget = readonlyInput
            self.fields["domain_name"].widget = readonlyInput

    # We have to protect the entire "data" dict because it contains the
    # password and confirm_password strings.
    @sensitive_variables('data', 'password')
    def handle(self, request, data):
        user = data.pop('id')

        # Throw away the password confirmation, we're done with it.
        data.pop('confirm_password', None)

        data.pop('domain_id')
        data.pop('domain_name')

        try:
            if "email" in data:
                data['email'] = data['email'] or None
            if "vdi_group" in data:
                data['vdi_group'] = data['vdi_group'] or None
            response = api.keystone.user_update(request, user, **data)
            messages.success(request,
                             _('User has been updated successfully.'))
        except Exception:
            response = exceptions.handle(request, ignore=True)
            messages.error(request, _('Unable to update the user.'))

        try:
            if "vdi_group" in data:
                group_ids = data['vdi_group'] or None
            vdi = vdiclient(self.request)
            for group_id in group_ids:
                vdi.groups.create_membership(user, group_id)

        except Exception:
            response = exceptions.handle(request, ignore=True)
            messages.error(request, _('Unable to update the group_membership.'))

        if isinstance(response, http.HttpResponse):
            return response
        else:
            return True
