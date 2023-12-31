# Copyright 2014 OpenStack Foundation
# Copyright 2014 Mirantis Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Tests for database migrations. This test case reads the configuration
file test_migrations.conf for database connection settings
to use in the tests. For each connection found in the config file,
the test case runs a series of test cases to ensure that migrations work
properly.

There are also "opportunistic" tests for both mysql and postgresql in here,
which allows testing against mysql and pg) in a properly configured unit
test environment.

For the opportunistic testing you need to set up a db named 'openstack_citest'
with user 'openstack_citest' and password 'openstack_citest' on localhost.
The test will then use that db and u/p combo to run the tests.

For postgres on Ubuntu this can be done with the following commands:

sudo -u postgres psql
postgres=# create user openstack_citest with createdb login password
      'openstack_citest';
postgres=# create database openstack_citest with owner openstack_citest;

"""

from oslo.config import cfg

from vdi.openstack.common.db.sqlalchemy import utils as db_utils
from vdi.tests.unit.db.migration import test_migrations_base as base

CONF = cfg.CONF


class TestMigrations(base.BaseWalkMigrationTestCase, base.CommonTestsMixIn):
    """Test sqlalchemy-migrate migrations."""
    USER = "openstack_citest"
    PASSWD = "openstack_citest"
    DATABASE = "openstack_citest"

    def __init__(self, *args, **kwargs):
        super(TestMigrations, self).__init__(*args, **kwargs)

    def setUp(self):
        super(TestMigrations, self).setUp()

    def assertColumnExists(self, engine, table, column):
        t = db_utils.get_table(engine, table)
        self.assertIn(column, t.c)

    def assertColumnsExists(self, engine, table, columns):
        for column in columns:
            self.assertColumnExists(engine, table, column)

    def assertColumnCount(self, engine, table, columns):
        t = db_utils.get_table(engine, table)
        self.assertEqual(len(t.columns), len(columns))

    def assertColumnNotExists(self, engine, table, column):
        t = db_utils.get_table(engine, table)
        self.assertNotIn(column, t.c)

    def assertIndexExists(self, engine, table, index):
        t = db_utils.get_table(engine, table)
        index_names = [idx.name for idx in t.indexes]
        self.assertIn(index, index_names)

    def assertIndexMembers(self, engine, table, index, members):
        self.assertIndexExists(engine, table, index)

        t = db_utils.get_table(engine, table)
        index_columns = None
        for idx in t.indexes:
            if idx.name == index:
                index_columns = idx.columns.keys()
                break

        self.assertEqual(sorted(members), sorted(index_columns))

    def _pre_upgrade_001(self, engine):
        # Anything returned from this method will be
        # passed to corresponding _check_xxx method as 'data'.
        pass

    def _check_001(self, engine, data):
        job_binary_internal_columns = [
            'created_at',
            'updated_at',
            'id',
            'tenant_id',
            'name',
            'data',
            'datasize'
        ]
        self.assertColumnsExists(
            engine, 'job_binary_internal', job_binary_internal_columns)
        self.assertColumnCount(
            engine, 'job_binary_internal', job_binary_internal_columns)

        node_group_templates_columns = [
            'created_at',
            'updated_at',
            'id',
            'name',
            'description',
            'tenant_id',
            'flavor_id',
            'image_id',
            'plugin_name',
            'hadoop_version',
            'node_processes',
            'node_configs',
            'volumes_per_node',
            'volumes_size',
            'volume_mount_prefix',
            'floating_ip_pool'
        ]
        self.assertColumnsExists(
            engine, 'node_group_templates', node_group_templates_columns)
        self.assertColumnCount(
            engine, 'node_group_templates', node_group_templates_columns)

        data_sources_columns = [
            'created_at',
            'updated_at',
            'id',
            'tenant_id',
            'name',
            'description',
            'type',
            'url',
            'credentials'
        ]
        self.assertColumnsExists(
            engine, 'data_sources', data_sources_columns)
        self.assertColumnCount(
            engine, 'data_sources', data_sources_columns)

        cluster_templates_columns = [
            'created_at',
            'updated_at',
            'id',
            'name',
            'description',
            'cluster_configs',
            'default_image_id',
            'anti_affinity',
            'tenant_id',
            'neutron_management_network',
            'plugin_name',
            'hadoop_version'
        ]
        self.assertColumnsExists(
            engine, 'cluster_templates', cluster_templates_columns)
        self.assertColumnCount(
            engine, 'cluster_templates', cluster_templates_columns)

        job_binaries_columns = [
            'created_at',
            'updated_at',
            'id',
            'tenant_id',
            'name',
            'description',
            'url',
            'extra'
        ]
        self.assertColumnsExists(
            engine, 'job_binaries', job_binaries_columns)
        self.assertColumnCount(
            engine, 'job_binaries', job_binaries_columns)

        jobs_columns = [
            'created_at',
            'updated_at',
            'id',
            'tenant_id',
            'name',
            'description',
            'type'
        ]
        self.assertColumnsExists(engine, 'jobs', jobs_columns)
        self.assertColumnCount(engine, 'jobs', jobs_columns)

        templates_relations_columns = [
            'created_at',
            'updated_at',
            'id',
            'tenant_id',
            'name',
            'flavor_id',
            'image_id',
            'node_processes',
            'node_configs',
            'volumes_per_node',
            'volumes_size',
            'volume_mount_prefix',
            'count',
            'cluster_template_id',
            'node_group_template_id',
            'floating_ip_pool'
        ]
        self.assertColumnsExists(
            engine, 'templates_relations', templates_relations_columns)
        self.assertColumnCount(
            engine, 'templates_relations', templates_relations_columns)

        mains_association_columns = [
            'Job_id',
            'JobBinary_id'
        ]
        self.assertColumnsExists(
            engine, 'mains_association', mains_association_columns)
        self.assertColumnCount(
            engine, 'mains_association', mains_association_columns)

        libs_association_columns = [
            'Job_id',
            'JobBinary_id'
        ]
        self.assertColumnsExists(
            engine, 'libs_association', libs_association_columns)
        self.assertColumnCount(
            engine, 'libs_association', libs_association_columns)

        clusters_columns = [
            'created_at',
            'updated_at',
            'id',
            'name',
            'description',
            'tenant_id',
            'trust_id',
            'is_transient',
            'plugin_name',
            'hadoop_version',
            'cluster_configs',
            'default_image_id',
            'neutron_management_network',
            'anti_affinity',
            'management_private_key',
            'management_public_key',
            'user_keypair_id',
            'status',
            'status_description',
            'info',
            'extra',
            'cluster_template_id'
        ]
        self.assertColumnsExists(engine, 'clusters', clusters_columns)
        self.assertColumnCount(engine, 'clusters', clusters_columns)

        node_groups_columns = [
            'created_at',
            'updated_at',
            'id',
            'name',
            'tenant_id',
            'flavor_id',
            'image_id',
            'image_username',
            'node_processes',
            'node_configs',
            'volumes_per_node',
            'volumes_size',
            'volume_mount_prefix',
            'count',
            'cluster_id',
            'node_group_template_id',
            'floating_ip_pool'
        ]
        self.assertColumnsExists(engine, 'node_groups', node_groups_columns)
        self.assertColumnCount(engine, 'node_groups', node_groups_columns)

        job_executions_columns = [
            'created_at',
            'updated_at',
            'id',
            'tenant_id',
            'job_id',
            'input_id',
            'output_id',
            'start_time',
            'end_time',
            'cluster_id',
            'info',
            'progress',
            'oozie_job_id',
            'return_code',
            'job_configs',
            'main_class',
            'java_opts'
        ]
        self.assertColumnsExists(
            engine, 'job_executions', job_executions_columns)
        self.assertColumnCount(
            engine, 'job_executions', job_executions_columns)

        instances_columns = [
            'created_at',
            'updated_at',
            'id',
            'tenant_id',
            'node_group_id',
            'instance_id',
            'instance_name',
            'internal_ip',
            'management_ip',
            'volumes'
        ]
        self.assertColumnsExists(engine, 'instances', instances_columns)
        self.assertColumnCount(engine, 'instances', instances_columns)

    def _check_002(self, engine, date):
        self.assertColumnExists(engine, 'job_executions', 'extra')
