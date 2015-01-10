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


from openstack_dashboard.dashboards.vdi.api.client import client as vdiclient

LOG = logging.getLogger(__name__)


class GeneralTab(tabs.Tab):
    name = _("General Info")
    slug = "pool_details_tab"
    template_name = "pools/_details.html"

    def get_context_data(self, request):
        pool_id = self.tab_group.kwargs['pool_id']

        vdi = vdiclient(request)
        pool = vdi.pools.get(pool_id)
        image = glance.image_get(request, pool.image_ref)
        pool.image_name = image.name

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

        return {"pool": pool}
                # "group_image": group_image}
                # "base_image": base_image,
                # "group_template": group_template,
                # "network": net_name}


class PoolDetailsTabs(tabs.TabGroup):
    slug = "pool_details"
    tabs = (GeneralTab, )
    sticky = True


def build_link(url):
    return "<a href='" + url + "' target=\"_blank\">" + url + "</a>"
