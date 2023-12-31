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

from vdi import context
from vdi import exceptions as ex
from vdi.openstack.common import timeutils
from vdi.plugins.general import utils as u
from vdi.plugins.vanilla.v2_3_0 import config
from vdi.plugins.vanilla.v2_3_0 import run_scripts as run
from vdi.plugins.vanilla.v2_3_0 import utils as pu

HADOOP_CONF_DIR = config.HADOOP_CONF_DIR


def scale_cluster(cluster, instances):
    config.configure_instances(instances)
    _update_include_files(cluster)
    run.refresh_hadoop_nodes(cluster)
    run.refresh_yarn_nodes(cluster)
    for instance in instances:
        run.start_instance(instance)


def _get_instances_with_service(instances, service):
    ret = []
    for instance in instances:
        if service in instance.node_group.node_processes:
            ret.append(instance)

    return ret


def _update_include_files(cluster):
    instances = u.get_instances(cluster)

    datanodes = u.get_datanodes(cluster)
    nodemanagers = u.get_nodemanagers(cluster)
    dn_hosts = u.generate_fqdn_host_names(datanodes)
    nm_hosts = u.generate_fqdn_host_names(nodemanagers)
    for instance in instances:
        with instance.remote() as r:
            r.execute_command(
                'sudo su - -c "echo \'%s\' > %s/dn-include" hadoop' % (
                    dn_hosts, HADOOP_CONF_DIR))
            r.execute_command(
                'sudo su - -c "echo \'%s\' > %s/nm-include" hadoop' % (
                    nm_hosts, HADOOP_CONF_DIR))


def decommission_nodes(cluster, instances):
    datanodes = _get_instances_with_service(instances, 'datanode')
    nodemanagers = _get_instances_with_service(instances, 'nodemanager')
    _update_exclude_files(cluster, instances)

    run.refresh_hadoop_nodes(cluster)
    run.refresh_yarn_nodes(cluster)

    _check_nodemanagers_decommission(cluster, nodemanagers)
    _check_datanodes_decommission(cluster, datanodes)

    _update_include_files(cluster)
    _clear_exclude_files(cluster)


def _update_exclude_files(cluster, instances):
    datanodes = _get_instances_with_service(instances, 'datanode')
    nodemanagers = _get_instances_with_service(instances, 'nodemanager')
    dn_hosts = u.generate_fqdn_host_names(datanodes)
    nm_hosts = u.generate_fqdn_host_names(nodemanagers)
    for instance in u.get_instances(cluster):
        with instance.remote() as r:
            r.execute_command(
                'sudo su - -c "echo \'%s\' > %s/dn-exclude" hadoop' % (
                    dn_hosts, HADOOP_CONF_DIR))
            r.execute_command(
                'sudo su - -c "echo \'%s\' > %s/nm-exclude" hadoop' % (
                    nm_hosts, HADOOP_CONF_DIR))


def _clear_exclude_files(cluster):
    for instance in u.get_instances(cluster):
        with instance.remote() as r:
            r.execute_command(
                'sudo su - -c "echo > %s/dn-exclude" hadoop' % HADOOP_CONF_DIR)
            r.execute_command(
                'sudo su - -c "echo > %s/nm-exclude" hadoop' % HADOOP_CONF_DIR)


def _check_decommission(cluster, instances, check_func, timeout):
    s_time = timeutils.utcnow()
    while timeutils.delta_seconds(s_time, timeutils.utcnow()) < timeout:
        statuses = check_func(cluster)
        dec_ok = True
        for instance in instances:
            if statuses[instance.fqdn()] != 'decommissioned':
                dec_ok = False

        if dec_ok:
            return
        else:
            context.sleep(5)
    else:
        ex.SaharaException("Cannot finish decommission in %d seconds" %
                           timeout)


def _check_nodemanagers_decommission(cluster, instances):
    _check_decommission(cluster, instances, pu.get_nodemanagers_status, 300)


def _check_datanodes_decommission(cluster, instances):
    _check_decommission(cluster, instances, pu.get_datanodes_status, 3600 * 4)
