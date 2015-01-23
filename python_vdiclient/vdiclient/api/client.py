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

from keystoneclient.v2_0 import client as keystone_client_v2
from keystoneclient.v3 import client as keystone_client_v3

from vdiclient.api import cluster_templates
from vdiclient.api import clusters
from vdiclient.api import data_sources
from vdiclient.api import httpclient
from vdiclient.api import images
from vdiclient.api import job_binaries
from vdiclient.api import job_binary_internals
from vdiclient.api import job_executions
from vdiclient.api import jobs
from vdiclient.api import node_group_templates
from vdiclient.api import plugins
from vdiclient.api import test_vm as vm
from vdiclient.api import groups
from vdiclient.api import pools


class Client(object):
    def __init__(self, username=None, api_key=None, domain_name=None,
                 project_id=None,project_name=None, auth_url=None,
                 vdi_url=None, endpoint_type='publicURL', service_type='vdi',
                 input_auth_token=None):

        # import pdb; pdb.set_trace()

        if not input_auth_token:
            keystone = self.get_keystone_client(domain_name=domain_name,
                                                username=username,
                                                api_key=api_key,
                                                auth_url=auth_url,
                                                project_id=project_id,
                                                project_name=project_name)
            input_auth_token = keystone.auth_token

        if not input_auth_token:
            raise RuntimeError("Not Authorized")

        vdi_catalog_url = vdi_url
        if not vdi_url:
            keystone = self.get_keystone_client(user_domain_name=domain_name,
                                                username=username,
                                                api_key=api_key,
                                                auth_url=auth_url,
                                                token=input_auth_token,
                                                project_id=project_id,
                                                project_name=project_name)
            catalog = keystone.service_catalog.get_endpoints(service_type)

            if service_type in catalog:
                if keystone.version == "v3":
                    vdi_endpoints = catalog[service_type]
                    for e in vdi_endpoints:
                        if str(e['interface']).lower() in str(endpoint_type).lower():
                            vdi_catalog_url = e['url']
                            break
                else:
                    for e_type, endpoint in catalog.get(service_type)[0].items():
                        if str(e_type).lower() == str(endpoint_type).lower():
                            vdi_catalog_url = endpoint
                            # 4/17/2014 - Ching, hack the url with vdi endpoint
                            # if vdi_catalog_url:
                            #     import re
                            #
                            #     sptn = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\:\d+\/\S*\/')
                            #     vdi_catalog_url = re.sub(sptn, "127.0.0.1:9000/v1.0/", vdi_catalog_url)
                            # end of hack
                            break

        # try:
        #     vdi_catalog_url
        # except NameError:
        #     vdi_catalog_url = vdi_url

        if not vdi_catalog_url:
            raise RuntimeError("Could not find VDI endpoint in catalog")

        self.client = httpclient.HTTPClient(vdi_catalog_url, input_auth_token)
        self.keystone_client = None

        # 4/2/2014, Ching - add vm
        self.vm = vm.VMManager(self)
        # 4/17/2014, Ching - add groups
        self.groups = groups.GroupManager(self)
        # 8/21/2014, Ching - add pools
        self.pools = pools.PoolManager(self)

        self.clusters = clusters.ClusterManager(self)
        self.cluster_templates = cluster_templates.ClusterTemplateManager(self)
        self.node_group_templates = (node_group_templates. NodeGroupTemplateManager(self))
        self.plugins = plugins.PluginManager(self)
        self.images = images.ImageManager(self)
        self.data_sources = data_sources.DataSourceManager(self)
        self.jobs = jobs.JobsManager(self)
        self.job_executions = job_executions.JobExecutionsManager(self)
        self.job_binaries = job_binaries.JobBinariesManager(self)
        self.job_binary_internals = \
            job_binary_internals.JobBinaryInternalsManager(self)

    def get_keystone_client(self, user_domain_name=None, username=None,
                            api_key=None, auth_url=None, token=None,
                            project_id=None, project_name=None):
        if not auth_url:
                raise RuntimeError("No auth url specified")
        # imported_client = keystone_client_v2 if "v2.0" in auth_url\
        #     else keystone_client_v3
        # if not getattr(self, "keystone_client", None):
        #     self.keystone_client = imported_client.Client(
        #         username=username,
        #         password=api_key,
        #         token=token,
        #         tenant_id=project_id,
        #         tenant_name=project_name,
        #         # project_id=project_id,
        #         # project_name=project_name,
        #         auth_url=auth_url,
        #         endpoint=auth_url)

        if "2.0" in auth_url:
            # if not getattr(self, "keystone_client", None):
            self.keystone_client = keystone_client_v2.Client(
                username=username,
                password=api_key,
                token=token,
                tenant_id=project_id,
                tenant_name=project_name,
                auth_url=auth_url,
                endpoint=auth_url)
        else:
            self.keystone_client = keystone_client_v3.Client(
                auth_url=auth_url,
                token=token,
                project_id=project_id,
                project_name=project_name)

        # import pdb; pdb.set_trace()

        self.keystone_client.authenticate()

        return self.keystone_client

    @staticmethod
    def get_projects_list(keystone_client):
        if isinstance(keystone_client, keystone_client_v2.Client):
            return keystone_client.tenants

        return keystone_client.projects
