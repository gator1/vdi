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

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.images.images \
    import tables as project_tables

from saharadashboard.api.client import client as saharaclient


LOG = logging.getLogger(__name__)


class CreateImage(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Image")
    url = "horizon:vdi:images_bak:create-image"
    classes = ("btn-launch", "ajax-modal")


# class ScaleCluster(tables.LinkAction):
#     name = "scale"
#     verbose_name = _("Scale Cluster")
#     url = "horizon:sahara:clusters:scale"
#     classes = ("ajax-modal", "btn-edit")
#
#     def allowed(self, request, cluster=None):
#         return cluster.status == "Active"


class DeleteImage(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Image")
    data_type_plural = _("Images")
    classes = ('btn-danger', 'btn-terminate')

    def action(self, request, obj_id):
        sahara = saharaclient(request)
        sahara.images.delete(obj_id)


# class UpdateRow(tables.Row):
#     ajax = True
#
#     def get_data(self, request, instance_id):
#         sahara = saharaclient(request)
#         instance = sahara.images_bak.get(instance_id)
#         return instance
class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, image_id):
        image = api.glance.image_get(request, image_id)
        return image


# def get_instances_count(cluster):
#     return sum([len(ng["instances"])
#                 for ng in cluster.node_groups])


def get_instances_count(image):
    return sum([len(ng["name"])
                for ng in image.name])


class ConfigureImage(tables.LinkAction):
    name = "configure"
    verbose_name = _("Configure Image")
    url = "horizon:vdi:images_bak:configure-image"
    classes = ("ajax-modal", "btn-create", "configure-image-btn")
    attrs = {"style": "display: none"}


class ImagesTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("error", False)
    )
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link=("horizon:vdi:images_bak:details"))
    id = tables.Column("id",
                         verbose_name=_("ID"))
    status = tables.Column("status",
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    class Meta:
        name = "images_bak"
        verbose_name = _("Images")
        row_class = UpdateRow
        status_columns = ["status"]
        table_actions = (CreateImage,
                         ConfigureImage,
                         DeleteImage)
        # row_actions = (ScaleCluster,
        #                DeleteGroup,)
        row_actions = (DeleteImage,)


class AdminCreateImage(project_tables.CreateImage):
    url = "horizon:admin:images_bak:create"


class AdminDeleteImage(project_tables.DeleteImage):
    def allowed(self, request, image=None):
        if image and image.protected:
            return False
        else:
            return True


class AdminEditImage(project_tables.EditImage):
    url = "horizon:admin:images_bak:update"

    def allowed(self, request, image=None):
        return True


# class UpdateRow(tables.Row):
#     ajax = True
#
#     def get_data(self, request, image_id):
#         image = api.glance.image_get(request, image_id)
#         return image


class AdminImagesTable(project_tables.ImagesTable):
    name = tables.Column("name",
                         link="horizon:admin:images_bak:detail",
                         verbose_name=_("Image Name"))

    class Meta:
        name = "images_bak"
        row_class = UpdateRow
        status_columns = ["status"]
        verbose_name = _("Images")
        table_actions = (AdminCreateImage, AdminDeleteImage)
        row_actions = (AdminEditImage, AdminDeleteImage)