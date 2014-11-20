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

from vdidashboard.api.client import client as vdiclient
from openstack_dashboard import api

LOG = logging.getLogger(__name__)


class CreateGroup(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Group")
    url = "horizon:vdi:groups:create-images_bak"
    classes = ("btn-launch", "ajax-modal")


# class ScaleCluster(tables.LinkAction):
#     name = "scale"
#     verbose_name = _("Scale Cluster")
#     url = "horizon:sahara:clusters:scale"
#     classes = ("ajax-modal", "btn-edit")
#
#     def allowed(self, request, cluster=None):
#         return cluster.status == "Active"


class EditGroup(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    # url = "horizon:admin:users:update"
    url = "horizon:vdi:groups:update"
    classes = ("ajax-modal", "btn-edit")
    policy_rules = (("identity", "identity:update_user"),
                    ("identity", "identity:list_projects"),)

    def get_policy_target(self, request, user):
        return {"user_id": user.id}

    def allowed(self, request, user):
        return api.keystone.keystone_can_edit_user()


class DeleteGroup(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Group")
    data_type_plural = _("Groups")
    classes = ('btn-danger', 'btn-terminate')

    def action(self, request, obj_id):
        sahara = vdiclient(request)
        sahara.groups.delete(obj_id)


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, instance_id):
        sahara = vdiclient(request)
        instance = sahara.groups.get(instance_id)
        return instance


# def get_instances_count(cluster):
#     return sum([len(ng["instances"])
#                 for ng in cluster.node_groups])


def get_instances_count(group):
    return sum([len(ng["name"])
                for ng in group.name])


class ConfigureGroup(tables.LinkAction):
    name = "configure"
    verbose_name = _("Configure Group")
    url = "horizon:vdi:groups:configure-images_bak"
    classes = ("ajax-modal", "btn-create", "configure-images_bak-btn")
    attrs = {"style": "display: none"}


class PoolsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("error", False)
    )
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:vdi:pools:detail")
    id = tables.Column("id",
                       verbose_name=_("ID"))
    vdi_group = tables.Column("vdi_group",
                              verbose_name=_("VDI Group"))
    status = tables.Column("status",
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)
    # instances_count = tables.Column(get_instances_count,
    #                                 verbose_name=_("Instances Count"))

    class Meta:
        name = "pools"
        verbose_name = _("Pools")
        # row_class = UpdateRow
        # status_columns = ["status"]
        # table_actions = (CreateGroup,
        #                  # ConfigureGroup,
        #                  DeleteGroup)
        # # row_actions = (ScaleCluster,
        # #                DeleteGroup,)
        # row_actions = (EditGroup,)
        #                # DeleteGroup,)
