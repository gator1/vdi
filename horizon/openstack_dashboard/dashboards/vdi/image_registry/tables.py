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

from django import template
from django.utils.translation import ugettext_lazy as _

from horizon import tables

from openstack_dashboard.dashboards.vdi.api.client import client as saharaclient
from openstack_dashboard.dashboards.vdi.utils import compatibility

LOG = logging.getLogger(__name__)


class EditTagsAction(tables.LinkAction):
    name = "edit_tags"
    verbose_name = _("Edit Tags")
    url = "horizon:vdi:image_registry:edit_tags"
    classes = ("ajax-modal", "btn-create")


def tags_to_string(image):
    template_name = 'image_registry/_list_tags.html'
    context = {"image": image}
    return template.loader.render_to_string(template_name, context)


class RegisterImage(tables.LinkAction):
    name = "register"
    verbose_name = _("Register Image")
    url = "horizon:vdi:image_registry:register"
    classes = ("btn-launch", "ajax-modal")


class UnregisterImages(tables.BatchAction):
    name = "Unregister"
    action_present = _("Unregister")
    action_past = _("Unregistered")
    data_type_singular = _("Image")
    data_type_plural = _("Images")
    classes = ('btn-danger', 'btn-terminate')

    def action(self, request, obj_id):
        vdi = saharaclient(request)
        vdi.images.unregister_image(obj_id)


class ImageRegistryTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Image"),
                         link=compatibility.convert_url(
                             "horizon:project:"
                             "images_bak:images_bak:detail"))
    tags = tables.Column(tags_to_string,
                         verbose_name=_("Tags"))

    class Meta:
        name = "image_registry"
        verbose_name = _("Image Registry")
        table_actions = ()
        table_actions = (RegisterImage, UnregisterImages,)
        row_actions = (EditTagsAction, UnregisterImages,)
