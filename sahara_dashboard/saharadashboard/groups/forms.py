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
from saharadashboard.api.client import client as vdiclient


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

        # # Populate pool choices
        # pool_choices = []
        #
        # vdi = vdiclient(self.request)
        # pools = vdi.pools.list()
        # temp_list = []
        # for pool in pools:
        #     temp_list.append(pool.name)
        # for i, v in enumerate(sorted(temp_list)):
        #     pool_choices.append((i, v))
        # self.fields['pool'].choices = pool_choices

    def clean(self):
        '''Check to make sure password fields match.'''
        data = super(forms.Form, self).clean()
        if 'password' in data:
            if data['password'] != data.get('confirm_password', None):
                raise ValidationError(_('Passwords do not match.'))
        return data


# ADD_PROJECT_URL = "horizon:admin:projects:create"


class CreateGroupForm(BaseUserForm):
    # Hide the domain_id and domain_name by default
    domain_id = forms.CharField(label=_("Domain ID"),
                                required=False,
                                widget=forms.HiddenInput())
    domain_name = forms.CharField(label=_("Domain Name"),
                                  required=False,
                                  widget=forms.HiddenInput())
    # name = forms.CharField(max_length=255, label=_("User Name"))
    # email = forms.EmailField(
    #     label=_("Email"),
    #     required=False)
    # password = forms.RegexField(
    #     label=_("Password"),
    #     widget=forms.PasswordInput(render_value=False),
    #     regex=validators.password_validator(),
    #     error_messages={'invalid': validators.password_validator_msg()})
    # confirm_password = forms.CharField(
    #     label=_("Confirm Password"),
    #     widget=forms.PasswordInput(render_value=False))
    # project = forms.DynamicChoiceField(label=_("Primary Project"),
    #                                    add_item_link=ADD_PROJECT_URL)
    # role_id = forms.ChoiceField(label=_("Role"))
    name = forms.CharField(label=_("Group Name"))
    description = forms.CharField(label=_("Description"))

    def __init__(self, *args, **kwargs):
        super(CreateGroupForm, self).__init__(*args, **kwargs)

        # For keystone V3, display the two fields in read-only
        if api.keystone.VERSIONS.active >= 3:
            readonlyInput = forms.TextInput(attrs={'readonly': 'readonly'})
            self.fields["domain_id"].widget = readonlyInput
            self.fields["domain_name"].widget = readonlyInput

    # We have to protect the entire "data" dict because it contains the
    # password and confirm_password strings.
    # @sensitive_variables('data')
    # def handle(self, request, data):
    @staticmethod
    def handle(request, data):
        # domain = api.keystone.get_default_domain(self.request)
        try:
            name = data.pop('name')
            description = data.pop('description')
            LOG.info('Creating group with name "%s"' % name)
            vdi = vdiclient(request)
            group = vdi.groups.create(name, description)
            # new_user = api.keystone.user_create(request,
            #                                     name=data['name'],
            #                                     email=data['email'],
            #                                     password=data['password'],
            #                                     project=data['project'],
            #                                     enabled=True,
            #                                     domain=domain.id)
            messages.success(request,
                             _('Group "%s" was successfully created.')
                             % name)

            # if isinstance(response, http.HttpResponse):
            #     return response
            # else:
            #     return True
            return group
        except Exception:
            exceptions.handle(request, _('Unable to create group.'))


class UpdateGroupForm(BaseUserForm):
    # Hide the domain_id and domain_name by default
    domain_id = forms.CharField(label=_("Domain ID"),
                                required=False,
                                widget=forms.HiddenInput())
    domain_name = forms.CharField(label=_("Domain Name"),
                                  required=False,
                                  widget=forms.HiddenInput())
    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput)
    name = forms.CharField(label=_("Group Name"))
    description = forms.CharField(label=_("Description"))
    # email = forms.EmailField(
    #     label=_("Email"),
    #     required=False)
    # password = forms.RegexField(
    #     label=_("Password"),
    #     widget=forms.PasswordInput(render_value=False),
    #     regex=validators.password_validator(),
    #     required=False,
    #     error_messages={'invalid': validators.password_validator_msg()})
    # confirm_password = forms.CharField(
    #     label=_("Confirm Password"),
    #     widget=forms.PasswordInput(render_value=False),
    #     required=False)
    # project = forms.ChoiceField(label=_("Primary Project"))
    # pool = forms.ChoiceField(label=_("Pool"),
    #                          required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdateGroupForm, self).__init__(request, *args, **kwargs)

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
    # @sensitive_variables('data')
    # def handle(self, request, data):
    @staticmethod
    def handle(request, data):
        group_id = data.pop('id')
        try:
            vdi = vdiclient(request)
            response = vdi.groups.update(group_id, data)
            messages.success(request,
                             _('Group has been updated successfully.'))
        except Exception:
            response = exceptions.handle(request, ignore=True)
            messages.error(request, _('Unable to update the user.'))
        if isinstance(response, http.HttpResponse):
            return response
        else:
            return True
