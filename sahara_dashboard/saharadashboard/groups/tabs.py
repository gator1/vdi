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

from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon import tabs

from saharadashboard.utils import compatibility
from saharadashboard.utils import importutils
from saharadashboard.utils import workflow_helpers as helpers

neutron = importutils.import_any('openstack_dashboard.api.quantum',
                                 'horizon.api.quantum',
                                 'openstack_dashboard.api.neutron')
nova = importutils.import_any('openstack_dashboard.api.nova',
                              'horizon.api.nova')
glance = importutils.import_any('openstack_dashboard.api.glance',
                                'horizon.api.glance')


from saharadashboard.api.client import client as vdiclient

LOG = logging.getLogger(__name__)


class GeneralTab(tabs.Tab):
    name = _("General Info")
    slug = "group_details_tab"
    # template_name = "groups/_details.html"
    template_name = "groups/_group_overview.html"

    def get_context_data(self, request):
        group_id = self.tab_group.kwargs['group_id']

        vdi = vdiclient(request)
        group = vdi.groups.get(group_id)

        # print("request={}".format(request))
        # print("images_bak.name={}".format(images_bak.name))
        # raw_input("===get_context_data===")

        group_image = vdi.groups.get_images(group_id)

        # for info_key, info_val in images_bak.info.items():
        #     for key, val in info_val.items():
        #         if str(val).startswith(('http://', 'https://')):
        #             images_bak.info[info_key][key] = build_link(val)

        # base_image = glance.image_get(request,
        #                               images_bak.default_image_id)

        # if getattr(images_bak, 'group_template_id', None):
        #     group_template = helpers.safe_call(vdi.cluster_templates.get,
        #                                          images_bak.cluster_template_id)
        # else:
        #     group_template = None

        # if getattr(images_bak, 'neutron_management_network', None):
        #     net_id = vdi.neutron_management_network
        #     network = neutron.network_get(request, net_id)
        #     network.set_id_as_name_if_empty()
        #     net_name = network.name
        # else:
        #     net_name = None

        # print("group_image = {}".format(group_image[0]))

        return {"group": group,
                "group_image": group_image}
                # "base_image": base_image,
                # "group_template": group_template,
                # "network": net_name}


class GroupDetailsTabs(tabs.TabGroup):
    slug = "group_details"
    tabs = (GeneralTab, )
    sticky = True


def build_link(url):
    return "<a href='" + url + "' target=\"_blank\">" + url + "</a>"


# class NodeGroupsTab(tabs.Tab):
#     name = _("Node Groups")
#     slug = "cluster_nodegroups_tab"
#     template_name = "clusters/_nodegroups_details.html"
#
#     def get_context_data(self, request):
#         cluster_id = self.tab_group.kwargs['cluster_id']
#         sahara = saharaclient(request)
#         cluster = sahara.clusters.get(cluster_id)
#         for ng in cluster.node_groups:
#             if not ng["flavor_id"]:
#                 continue
#             ng["flavor_name"] = nova.flavor_get(request, ng["flavor_id"]).name
#             ng["node_group_template"] = helpers.safe_call(
#                 sahara.node_group_templates.get,
#                 ng.get("node_group_template_id", None))
#
#         return {"cluster": cluster}


# class Instance(object):
#     def __init__(self, name=None, id=None, internal_ip=None,
#                  management_ip=None):
#         self.name = name
#         self.id = id
#         self.internal_ip = internal_ip
#         self.management_ip = management_ip


# class InstancesTable(tables.DataTable):
#     name = tables.Column("name",
#                          link=(compatibility.convert_url(
#                                "horizon:project:instances:detail")),
#                          verbose_name=_("Name"))
#
#     internal_ip = tables.Column("internal_ip",
#                                 verbose_name=_("Internal IP"))
#
#     management_ip = tables.Column("management_ip",
#                                   verbose_name=_("Management IP"))
#
#     class Meta:
#         name = "cluster_instances"
#         #just ignoring the name
#         verbose_name = _(" ")


# class InstancesTab(tabs.TableTab):
#     name = _("Instances")
#     slug = "cluster_instances_tab"
#     template_name = "clusters/_instances_details.html"
#     table_classes = (InstancesTable, )
#
#     def get_cluster_instances_data(self):
#         cluster_id = self.tab_group.kwargs['cluster_id']
#         sahara = saharaclient(self.request)
#         cluster = sahara.clusters.get(cluster_id)
#
#         instances = []
#         for ng in cluster.node_groups:
#             for instance in ng["instances"]:
#                 instances.append(Instance(
#                     name=instance["instance_name"],
#                     id=instance["instance_id"],
#                     internal_ip=instance.get("internal_ip",
#                                              "Not assigned"),
#                     management_ip=instance.get("management_ip",
#                                                "Not assigned")))
#         return instances


