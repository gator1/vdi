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

import hashlib

from oslo.config import cfg

from vdi import context
from vdi import exceptions as ex
from vdi.openstack.common import log
from vdi.utils.openstack import nova
from vdi.utils import xmlutils as x


TOPOLOGY_CONFIG = {
    "topology.node.switch.mapping.impl":
    "org.apache.hadoop.net.ScriptBasedMapping",
    "topology.script.file.name":
    "/etc/hadoop/topology.sh"
}

LOG = log.getLogger(__name__)

opts = [
    cfg.BoolOpt('enable_data_locality',
                default=False,
                help="""Enables data locality for hadoop cluster.
                 Also enables data locality for Swift used by hadoop.
                 If enabled, 'compute_topology' and 'swift_topology'
                 configuration parameters should point to OpenStack and Swift
                 topology correspondingly."""),
    cfg.BoolOpt('enable_hypervisor_awareness',
                default=True,
                help="""Enables four-level topology for data locality.
                Works only if corresponding plugin supports such mode."""),
    cfg.StrOpt('compute_topology_file',
               default='etc/vdi/compute.topology',
               help="""File with nova compute topology.
                It should contain mapping between nova computes and racks.
                File format:
                compute1 /rack1
                compute2 /rack2
                compute3 /rack2"""),
    cfg.StrOpt('swift_topology_file',
               default='etc/vdi/swift.topology',
               help="""File with Swift topology.
                It should contain mapping between Swift nodes and racks.
                File format:
                node1 /rack1
                node2 /rack2
                node3 /rack2""")
]

CONF = cfg.CONF
CONF.register_opts(opts)


def _read_swift_topology():
    topology = {}
    try:
        with open(CONF.swift_topology_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                (host, path) = line.split()
                topology[host] = path
    except IOError:
        raise ex.NotFoundException(
            CONF.swift_topology_file,
            "Unable to find file %s with Swift topology")
    return topology


def _read_compute_topology():
    ctx = context.ctx()
    tenant_id = str(ctx.tenant_id)
    topology = {}
    try:
        with open(CONF.compute_topology_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                (host, path) = line.split()
                #calulating host id based on tenant id and host
                #using the same algorithm as in nova
                #see nova/api/openstack/compute/views/servers.py
                #def _get_host_id(instance):
                sha_hash = hashlib.sha224(tenant_id + host)
                topology[sha_hash.hexdigest()] = path
    except IOError:
        raise ex.NotFoundException(
            CONF.compute_topology_file,
            "Unable to find file %s with compute topology")
    return topology


def generate_topology_map(cluster, is_node_awareness):
    mapping = _read_compute_topology()
    nova_client = nova.client()
    topology_mapping = {}
    for ng in cluster.node_groups:
        for i in ng.instances:
            #TODO(alazarev) get all servers info with one request
            ni = nova_client.servers.get(i.instance_id)
            hostId = ni.hostId
            if hostId not in mapping:
                raise ex.NotFoundException(
                    i.instance_id, "Was not able to find compute node "
                                   "topology for VM %s")
            rack = mapping[hostId]
            if is_node_awareness:
                rack += "/" + hostId

            topology_mapping[i.instance_name] = rack
            topology_mapping[i.management_ip] = rack
            topology_mapping[i.internal_ip] = rack

    topology_mapping.update(_read_swift_topology())

    return topology_mapping


def vm_awareness_core_config():
    c = x.load_hadoop_xml_defaults('topology/resources/core-template.xml')
    result = [cfg for cfg in c if cfg['value']]

    if not CONF.enable_hypervisor_awareness:
        # not leveraging 4-layer approach so override template value
        param = next((prop for prop in result
                      if prop['name'] == 'net.topology.impl'), None)
        if param:
            param['value'] = 'org.apache.hadoop.net.NetworkTopology'

    LOG.info("Vm awareness will add following configs in core-site "
             "params: %s", result)
    return result


def vm_awareness_mapred_config():
    c = x.load_hadoop_xml_defaults('topology/resources/mapred-template.xml')
    result = [cfg for cfg in c if cfg['value']]
    LOG.info("Vm awareness will add following configs in map-red "
             "params: %s", result)
    return result


def vm_awareness_all_config():
    return vm_awareness_core_config() + vm_awareness_mapred_config()
