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

from vdi.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def start_processes(remote, *processes):
    for proc in processes:
        remote.execute_command('sudo su -c "/usr/sbin/hadoop-daemon.sh '
                               'start %s" hadoop' % proc)


def refresh_nodes(remote, service):
    remote.execute_command("sudo su -c 'hadoop %s -refreshNodes' hadoop"
                           % service)


def format_namenode(remote):
    remote.execute_command("sudo su -c 'hadoop namenode -format' hadoop")


def hive_create_warehouse_dir(remote):
    LOG.debug("Creating Hive warehouse dir")
    remote.execute_command("sudo su - -c 'hadoop fs -mkdir "
                           "/user/hive/warehouse' hadoop")


def hive_copy_shared_conf(remote, dest):
    LOG.debug("Copying shared Hive conf")
    remote.execute_command(
        "sudo su - -c 'hadoop fs -put /opt/hive/conf/hive-site.xml "
        "%s' hadoop" % dest)


def oozie_share_lib(remote, nn_hostname):
    LOG.debug("Sharing Oozie libs to hdfs://%s:8020" % nn_hostname)
    #remote.execute_command('sudo su - -c "/opt/oozie/bin/oozie-setup.sh '
    #                       'sharelib create -fs hdfs://%s:8020" hadoop'
    #                       % nn_hostname)

    #TODO(alazarev) return 'oozie-setup.sh sharelib create' back
    #when #1262023 is resolved
    remote.execute_command(
        'sudo su - -c "mkdir /tmp/oozielib && '
        'tar zxf /opt/oozie/oozie-sharelib-4.0.0.tar.gz -C /tmp/oozielib && '
        'hadoop fs -put /tmp/oozielib/share share && '
        'rm -rf /tmp/oozielib" hadoop')

    LOG.debug("Creating sqlfile for Oozie")
    remote.execute_command('sudo su - -c "/opt/oozie/bin/ooziedb.sh '
                           'create -sqlfile oozie.sql '
                           '-run Validate DB Connection" hadoop')


def check_datanodes_count(remote, count):
    if count < 1:
        return True

    LOG.debug("Checking datanode count")
    exit_code, stdout = remote.execute_command(
        'sudo su -c "hadoop dfsadmin -report | '
        'grep \'Datanodes available:\' | '
        'awk \'{print \\$3}\'" hadoop')
    LOG.debug("Datanode count='%s'" % stdout.rstrip())

    return exit_code == 0 and int(stdout) == count


def mysql_start(remote, mysql_instance):
    LOG.debug("Starting mysql at %s" % mysql_instance.hostname())
    remote.execute_command("/opt/start-mysql.sh")


def oozie_create_db(remote):
    LOG.debug("Creating Oozie DB Schema...")
    remote.execute_command("mysql -u root < /tmp/create_oozie_db.sql")


def start_oozie(remote):
    remote.execute_command(
        'sudo su - -c "/opt/oozie/bin/oozied.sh start" hadoop')


def hive_create_db(remote):
    LOG.debug("Creating Hive metastore db...")
    remote.execute_command("mysql -u root < /tmp/create_hive_db.sql")


def hive_metastore_start(remote):
    LOG.debug("Starting Hive Metastore Server...")
    remote.execute_command("sudo su - -c 'nohup /opt/hive/bin/hive"
                           " --service metastore > /dev/null &' hadoop")
