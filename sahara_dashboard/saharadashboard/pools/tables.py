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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables
from django.utils.http import urlencode

from saharadashboard.api.client import client as vdiclient
from openstack_dashboard import api

LOG = logging.getLogger(__name__)

NOT_LAUNCHABLE_FORMATS = ['aki', 'ari']


class CreatePool(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Pool")
    url = "horizon:vdi:pools:create-pool"
    classes = ("btn-launch", "ajax-modal")


class EditPool(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:vdi:pools:update"
    classes = ("ajax-modal", "btn-edit")
    policy_rules = (("identity", "identity:update_user"),
                    ("identity", "identity:list_projects"),)

    def get_policy_target(self, request, user):
        return {"user_id": user.id}

    def allowed(self, request, user):
        return api.keystone.keystone_can_edit_user()


class DeletePool(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Pool")
    data_type_plural = _("Pools")
    classes = ('btn-danger', 'btn-terminate')

    def action(self, request, obj_id):
        vdi = vdiclient(request)
        vdi.pools.delete(obj_id)


class LaunchImage(tables.LinkAction):
    name = "launch_image"
    verbose_name = _("Launch")
    url = "horizon:project:instances:launch"
    classes = ("btn-launch", "ajax-modal")
    policy_rules = (("compute", "compute:create"),)

    def get_link_url(self, datum):
        base_url = reverse(self.url)

        if get_image_type(datum) == "image":
            source_type = "image_id"
        else:
            source_type = "instance_snapshot_id"

        params = urlencode({"source_type": source_type,
                            # "source_id": self.table.get_object_id(datum)})
                            "source_id": datum.image_ref,
                            "source_name": datum.name})
        return "?".join([base_url, params])

    def allowed(self, request, pool=None):
        image = api.glance.image_get(request, pool.image_ref)

        if image and image.container_format not in NOT_LAUNCHABLE_FORMATS:
            return image.status in ("active",)
        return False


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, instance_id):
        vdi = vdiclient(request)
        instance = vdi.pools.get(instance_id)
        return instance


def get_instances_count(pool):
    return sum([len(ng["name"])
                for ng in pool.name])


def get_image_type(image):
    return getattr(image, "properties", {}).get("image_type", "image")


# class ConfigureGroup(tables.LinkAction):
#     name = "configure"
#     verbose_name = _("Configure Group")
#     url = "horizon:vdi:groups:configure-images_bak"
#     classes = ("ajax-modal", "btn-create", "configure-images_bak-btn")
#     attrs = {"style": "display: none"}


class PoolsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("error", False)
    )
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link=("horizon:vdi:pools:detail"))
    # id = tables.Column("id",
    #                      verbose_name=_("ID"))
    image_name = tables.Column("image_name",
                          verbose_name=_("Image Name"))
    # vdi_group = tables.Column("vdi_group",
    #                       verbose_name=_("VDI Group"))
    status = tables.Column("status",
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    class Meta:
        name = "pools"
        verbose_name = _("Pools")
        row_class = UpdateRow
        status_columns = ["status"]
        table_actions = (CreatePool,
                         DeletePool)
        row_actions = (LaunchImage, EditPool, DeletePool,)
