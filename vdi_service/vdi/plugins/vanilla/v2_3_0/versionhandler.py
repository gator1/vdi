# Copyright (c) 2014 Mirantis Inc.
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

from oslo.config import cfg

from vdi import conductor
from vdi import context
from vdi.openstack.common import log as logging
from vdi.plugins.general import utils
from vdi.plugins.vanilla import abstractversionhandler as avm
from vdi.plugins.vanilla.v2_3_0 import config as c
from vdi.plugins.vanilla.v2_3_0 import config_helper as c_helper
from vdi.plugins.vanilla.v2_3_0 import run_scripts as run
from vdi.plugins.vanilla.v2_3_0 import scaling as sc
from vdi.plugins.vanilla.v2_3_0 import validation as vl

conductor = conductor.API
LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class VersionHandler(avm.AbstractVersionHandler):
    def get_plugin_configs(self):
        return c_helper.get_plugin_configs()

    def get_node_processes(self):
        return {
            "Hadoop": [],
            "MapReduce": ["historyserver"],
            "HDFS": ["namenode", "datanode"],
            "YARN": ["resourcemanager", "nodemanager"]
        }

    def validate(self, cluster):
        vl.validate_cluster_creating(cluster)

    def update_infra(self, cluster):
        pass

    def configure_cluster(self, cluster):
        c.configure_cluster(cluster)

    def start_cluster(self, cluster):
        nn = utils.get_namenode(cluster)
        run.format_namenode(nn)
        run.start_hadoop_process(nn, 'namenode')

        rm = utils.get_resourcemanager(cluster)
        run.start_yarn_process(rm, 'resourcemanager')

        for dn in utils.get_datanodes(cluster):
            run.start_hadoop_process(dn, 'datanode')

        for nm in utils.get_nodemanagers(cluster):
            run.start_yarn_process(nm, 'nodemanager')

        hs = utils.get_historyserver(cluster)
        if hs:
            run.start_historyserver(hs)

        self._set_cluster_info(cluster)

    def decommission_nodes(self, cluster, instances):
        sc.decommission_nodes(cluster, instances)

    def validate_scaling(self, cluster, existing, additional):
        vl.validate_additional_ng_scaling(cluster, additional)
        vl.validate_existing_ng_scaling(cluster, existing)

    def scale_cluster(self, cluster, instances):
        sc.scale_cluster(cluster, instances)

    def _set_cluster_info(self, cluster):
        nn = utils.get_namenode(cluster)
        rm = utils.get_resourcemanager(cluster)
        hs = utils.get_historyserver(cluster)

        info = {}

        if rm:
            info['YARN'] = {
                'Web UI': 'http://%s:%s' % (rm.management_ip, '8088'),
            }

        if nn:
            info['HDFS'] = {
                'Web UI': 'http://%s:%s' % (nn.management_ip, '50070'),
            }

        if hs:
            info['MapReduce JobHistory Server'] = {
                'Web UI': 'http://%s:%s' % (hs.management_ip, '19888')
            }

        ctx = context.ctx()
        conductor.cluster_update(ctx, cluster, {'info': info})

    def get_oozie_server(self, cluster):
        pass

    def get_resource_manager_uri(self, cluster):
        pass
