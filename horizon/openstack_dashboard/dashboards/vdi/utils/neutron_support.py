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

from django.utils.translation import ugettext as _
from horizon import exceptions
from openstack_dashboard.dashboards.vdi.utils import importutils

neutron = importutils.import_any('openstack_dashboard.api.quantum',
                                 'openstack_dashboard.api.neutron',
                                 'horizon.api.quantum',
                                 'horizon.api.neutron')


def populate_neutron_management_network_choices(self, request, context):
    try:
        tenant_id = self.request.user.tenant_id
        networks = neutron.network_list_for_tenant(request, tenant_id)
        for n in networks:
            n.set_id_as_name_if_empty()
        network_list = [(network.id, network.name) for network in networks]
    except Exception:
        network_list = []
        exceptions.handle(request,
                          _('Unable to retrieve networks.'))
    return network_list
