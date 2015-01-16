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

from horizon import exceptions
from horizon import forms
from horizon import workflows

from vdidashboard.utils import importutils
from vdidashboard.utils import neutron_support
import vdidashboard.utils.workflow_helpers as whelpers

neutron = importutils.import_any('openstack_dashboard.api.quantum',
                                 'openstack_dashboard.api.neutron',
                                 'horizon.api.quantum',
                                 'horizon.api.neutron')

nova = importutils.import_any('openstack_dashboard.api.nova',
                              'horizon.api.nova')

from django.utils.translation import ugettext as _

from vdidashboard.api import client as vdiclient
from vdiclient.api import base as api_base
from vdidashboard.api.client import VDI_USE_NEUTRON
import vdidashboard.cluster_templates.workflows.create as t_flows

import logging

LOG = logging.getLogger(__name__)


class CreateGroup(t_flows.CreateClusterTemplate):
    slug = "create_group"
    name = _("Create Group")
    success_url = "horizon:vdi:groups:index"


class GeneralConfigAction(workflows.Action):
    hidden_configure_field = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"class": "hidden_configure_field"}))

    hidden_to_delete_field = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"class": "hidden_to_delete_field"}))

    cluster_name = forms.CharField(label=_("Cluster Name"),
                                   required=True)

    description = forms.CharField(label=_("Description"),
                                  required=False,
                                  widget=forms.Textarea)
    cluster_template = forms.ChoiceField(label=_("Cluster Template"),
                                         initial=(None, "None"),
                                         required=False)

    image = forms.ChoiceField(label=_("Base Image"),
                              required=True)

    keypair = forms.ChoiceField(
        label=_("Keypair"),
        required=False,
        help_text=_("Which keypair to use for authentication."))

    def __init__(self, request, *args, **kwargs):
        super(GeneralConfigAction, self).__init__(request, *args, **kwargs)

        plugin, vdi_version = whelpers.\
            get_plugin_and_vdi_version(request)

        if VDI_USE_NEUTRON:
            self.fields["neutron_management_network"] = forms.ChoiceField(
                label=_("Neutron Management Network"),
                required=True,
                choices=self.populate_neutron_management_network_choices(
                    request, {})
            )

        self.fields["plugin_name"] = forms.CharField(
            widget=forms.HiddenInput(),
            initial=plugin
        )
        self.fields["vdi_version"] = forms.CharField(
            widget=forms.HiddenInput(),
            initial=vdi_version
        )

    def populate_image_choices(self, request, context):
        vdi = vdiclient.client(request)
        all_images = vdi.images.list()

        plugin, vdi_version = whelpers.\
            get_plugin_and_vdi_version(request)

        details = vdi.plugins.get_version_details(plugin,
                                                     vdi_version)

        return [(image.id, image.name) for image in all_images
                if set(details.required_image_tags).issubset(set(image.tags))]

    def populate_keypair_choices(self, request, context):
        keypairs = nova.keypair_list(request)
        keypair_list = [(kp.name, kp.name) for kp in keypairs]
        keypair_list.insert(0, ("", "No keypair"))
        return keypair_list

    
    populate_neutron_management_network_choices = \
        neutron_support.populate_neutron_management_network_choices

    def get_help_text(self):
        extra = dict()
        plugin, vdi_version = whelpers.\
            get_plugin_and_vdi_version(self.request)
        extra["plugin_name"] = plugin
        extra["vdi_version"] = vdi_version
        return super(GeneralConfigAction, self).get_help_text(extra)

    def clean(self):
        cleaned_data = super(GeneralConfigAction, self).clean()
        if cleaned_data.get("hidden_configure_field", None) \
                == "create_nodegroup":
            self._errors = dict()
        return cleaned_data

    class Meta:
        name = _("Configure Cluster")
        help_text_template = \
            ("clusters/_configure_general_help.html")


class GeneralConfig(workflows.Step):
    action_class = GeneralConfigAction
    contributes = ("hidden_configure_field", )

    def contribute(self, data, context):
        for k, v in data.items():
            context["general_" + k] = v

        return context


