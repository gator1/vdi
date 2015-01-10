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

from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon import tabs

from openstack_dashboard.dashboards.vdi.utils import compatibility
from openstack_dashboard.dashboards.vdi.utils import importutils
from openstack_dashboard.dashboards.vdi.utils import workflow_helpers as helpers

neutron = importutils.import_any('openstack_dashboard.api.quantum',
                                 'horizon.api.quantum',
                                 'openstack_dashboard.api.neutron')
nova = importutils.import_any('openstack_dashboard.api.nova',
                              'horizon.api.nova')
glance = importutils.import_any('openstack_dashboard.api.glance',
                                'horizon.api.glance')


from openstack_dashboard.dashboards.vdi.api.client import client as saharaclient

LOG = logging.getLogger(__name__)


class GeneralTab(tabs.Tab):
    name = _("General Info")
    slug = "cluster_details_tab"
    template_name = "clusters/_details.html"

    def get_context_data(self, request):
        cluster_id = self.tab_group.kwargs['cluster_id']
        sahara = saharaclient(request)
        cluster = sahara.clusters.get(cluster_id)

        for info_key, info_val in cluster.info.items():
            for key, val in info_val.items():
                if str(val).startswith(('http://', 'https://')):
                    cluster.info[info_key][key] = build_link(val)

        base_image = glance.image_get(request,
                                      cluster.default_image_id)

        if getattr(cluster, 'cluster_template_id', None):
            cluster_template = helpers.safe_call(sahara.cluster_templates.get,
                                                 cluster.cluster_template_id)
        else:
            cluster_template = None

        if getattr(cluster, 'neutron_management_network', None):
            net_id = cluster.neutron_management_network
            network = neutron.network_get(request, net_id)
            network.set_id_as_name_if_empty()
            net_name = network.name
        else:
            net_name = None

        return {"cluster": cluster,
                "base_image": base_image,
                "cluster_template": cluster_template,
                "network": net_name}


def build_link(url):
    return "<a href='" + url + "' target=\"_blank\">" + url + "</a>"


class NodeGroupsTab(tabs.Tab):
    name = _("Node Groups")
    slug = "cluster_nodegroups_tab"
    template_name = "clusters/_nodegroups_details.html"

    def get_context_data(self, request):
        cluster_id = self.tab_group.kwargs['cluster_id']
        sahara = saharaclient(request)
        cluster = sahara.clusters.get(cluster_id)
        for ng in cluster.node_groups:
            if not ng["flavor_id"]:
                continue
            ng["flavor_name"] = nova.flavor_get(request, ng["flavor_id"]).name
            ng["node_group_template"] = helpers.safe_call(
                sahara.node_group_templates.get,
                ng.get("node_group_template_id", None))

        return {"cluster": cluster}


class Instance(object):
    def __init__(self, name=None, id=None, internal_ip=None,
                 management_ip=None):
        self.name = name
        self.id = id
        self.internal_ip = internal_ip
        self.management_ip = management_ip


class InstancesTable(tables.DataTable):
    name = tables.Column("name",
                         link=(compatibility.convert_url(
                               "horizon:project:instances:detail")),
                         verbose_name=_("Name"))

    internal_ip = tables.Column("internal_ip",
                                verbose_name=_("Internal IP"))

    management_ip = tables.Column("management_ip",
                                  verbose_name=_("Management IP"))

    class Meta:
        name = "cluster_instances"
        #just ignoring the name
        verbose_name = _(" ")


class InstancesTab(tabs.TableTab):
    name = _("Instances")
    slug = "cluster_instances_tab"
    template_name = "clusters/_instances_details.html"
    table_classes = (InstancesTable, )

    def get_cluster_instances_data(self):
        cluster_id = self.tab_group.kwargs['cluster_id']
        sahara = saharaclient(self.request)
        cluster = sahara.clusters.get(cluster_id)

        instances = []
        for ng in cluster.node_groups:
            for instance in ng["instances"]:
                instances.append(Instance(
                    name=instance["instance_name"],
                    id=instance["instance_id"],
                    internal_ip=instance.get("internal_ip",
                                             "Not assigned"),
                    management_ip=instance.get("management_ip",
                                               "Not assigned")))
        return instances


class ClusterDetailsTabs(tabs.TabGroup):
    slug = "cluster_details"
    tabs = (GeneralTab, NodeGroupsTab, InstancesTab, )
    sticky = True
