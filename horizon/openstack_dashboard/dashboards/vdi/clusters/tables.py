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

from openstack_dashboard.dashboards.vdi.api.client import client as vdiclient


LOG = logging.getLogger(__name__)


class CreateCluster(tables.LinkAction):
    name = "create"
    verbose_name = _("Launch Cluster")
    url = "horizon:sahara:clusters:create-cluster"
    classes = ("btn-launch", "ajax-modal")


class ScaleCluster(tables.LinkAction):
    name = "scale"
    verbose_name = _("Scale Cluster")
    url = "horizon:sahara:clusters:scale"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, cluster=None):
        return cluster.status == "Active"


class DeleteCluster(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Cluster")
    data_type_plural = _("Clusters")
    classes = ('btn-danger', 'btn-terminate')

    def action(self, request, obj_id):
        sahara = vdiclient(request)
        sahara.clusters.delete(obj_id)


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, instance_id):
        sahara = vdiclient(request)
        instance = sahara.clusters.get(instance_id)
        return instance


def get_instances_count(cluster):
    return sum([len(ng["instances"])
                for ng in cluster.node_groups])


class ConfigureCluster(tables.LinkAction):
    name = "configure"
    verbose_name = _("Configure Cluster")
    url = "horizon:sahara:clusters:configure-cluster"
    classes = ("ajax-modal", "btn-create", "configure-cluster-btn")
    attrs = {"style": "display: none"}


class ClustersTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("error", False)
    )

    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link=("horizon:sahara:clusters:details"))
    status = tables.Column("status",
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)
    instances_count = tables.Column(get_instances_count,
                                    verbose_name=_("Instances Count"))

    class Meta:
        name = "clusters"
        verbose_name = _("Clusters")
        row_class = UpdateRow
        status_columns = ["status"]
        table_actions = (CreateCluster,
                         ConfigureCluster,
                         DeleteCluster)
        row_actions = (ScaleCluster,
                       DeleteCluster,)
