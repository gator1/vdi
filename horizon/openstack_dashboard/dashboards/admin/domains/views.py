# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import workflows

from openstack_dashboard import api

from openstack_dashboard.dashboards.admin.domains import constants
from openstack_dashboard.dashboards.admin.domains \
    import tables as project_tables
from openstack_dashboard.dashboards.admin.domains \
    import workflows as project_workflows


class IndexView(tables.DataTableView):
    table_class = project_tables.DomainsTable
    template_name = constants.DOMAINS_INDEX_VIEW_TEMPLATE

    def get_data(self):
        domains = []
        domain_context = self.request.session.get('domain_context', None)
        # user = self.request.user
        # if user.user_domain_name.lower() not in ['admin_domain', 'default']:
        #     domain_context = user.user_domain_id
        #     self.request.session['domain_context'] = user.user_domain_id
        #     self.request.session['domain_context_name'] = user.user_domain_name
        try:
            if domain_context:
                domain = api.keystone.domain_get(self.request,
                                                 domain_context)
                domains.append(domain)
            else:
                domains = api.keystone.domain_list(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve domain list.'))
        return domains


class CreateDomainView(workflows.WorkflowView):
    workflow_class = project_workflows.CreateDomain


class UpdateDomainView(workflows.WorkflowView):
    workflow_class = project_workflows.UpdateDomain

    def get_initial(self):
        initial = super(UpdateDomainView, self).get_initial()

        domain_id = self.kwargs['domain_id']
        initial['domain_id'] = domain_id

        try:
            # get initial domain info
            domain_info = api.keystone.domain_get(self.request,
                                                  domain_id)
            for field in constants.DOMAIN_INFO_FIELDS:
                initial[field] = getattr(domain_info, field, None)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve domain details.'),
                              redirect=reverse(constants.DOMAINS_INDEX_URL))
        return initial
