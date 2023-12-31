# Copyright 2014 OpenStack Foundation.
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

"""initial

Revision ID: 572fe6dceb6d
Revises: None
Create Date: 2014-01-17 17:20:38.500595

"""

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None

from alembic import op
import sqlalchemy as sa

from vdi.db.sqlalchemy import types as st

MYSQL_ENGINE = 'InnoDB'
MYSQL_CHARSET = 'utf8'


def upgrade():
    op.create_table(
        'groups',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('domain_id', sa.String(length=36), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('image_ref', sa.String(length=255), nullable=True),
        # sa.Column('is_transient', sa.Boolean(), nullable=True),
        # sa.Column('plugin_name', sa.String(length=80), nullable=False),
        # sa.Column('hadoop_version', sa.String(length=80), nullable=False),
        # sa.Column('cluster_configs', st.JsonDictType(), nullable=True),
        # sa.Column('default_image_id', sa.String(length=36), nullable=True),
        # sa.Column('neutron_management_network',
        #           sa.String(length=36), nullable=True),
        # sa.Column('anti_affinity', st.JsonDictType(), nullable=True),
        sa.Column('management_private_key', sa.Text(), nullable=False),
        sa.Column('management_public_key', sa.Text(), nullable=False),
        # sa.Column('user_keypair_id', sa.String(length=80), nullable=True),
        sa.Column('status', sa.String(length=80), nullable=True),
        sa.Column('status_description', sa.String(length=200), nullable=True),
        sa.Column('info', st.JsonDictType(), nullable=True),
        # sa.Column('extra', st.JsonDictType(), nullable=True),
        # sa.Column('cluster_template_id', sa.String(length=36), nullable=True),
        # sa.ForeignKeyConstraint(['cluster_template_id'],
        #                         ['cluster_templates.id'], ),
        # sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'domain_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'images',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('group_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=80), nullable=True),
        sa.Column('status_description', sa.String(length=200), nullable=True),
        sa.Column('info', st.JsonDictType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        # sa.UniqueConstraint('tenant_id'),
        # sa.ForeignKeyConstraint(['group_id'],
        #                         ['groups.id'],),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'pools',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('domain_id', sa.String(length=36), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('image_ref', sa.String(length=255), nullable=True),
        sa.Column('vdi_group', st.JsonDictType(), nullable=True),
        # sa.Column('plugin_name', sa.String(length=80), nullable=False),
        # sa.Column('hadoop_version', sa.String(length=80), nullable=False),
        # sa.Column('cluster_configs', st.JsonDictType(), nullable=True),
        # sa.Column('default_image_id', sa.String(length=36), nullable=True),
        # sa.Column('neutron_management_network',
        #           sa.String(length=36), nullable=True),
        # sa.Column('anti_affinity', st.JsonDictType(), nullable=True),
        sa.Column('management_private_key', sa.Text(), nullable=False),
        sa.Column('management_public_key', sa.Text(), nullable=False),
        # sa.Column('user_keypair_id', sa.String(length=80), nullable=True),
        sa.Column('status', sa.String(length=80), nullable=True),
        sa.Column('status_description', sa.String(length=200), nullable=True),
        sa.Column('info', st.JsonDictType(), nullable=True),
        # sa.Column('extra', st.JsonDictType(), nullable=True),
        # sa.Column('cluster_template_id', sa.String(length=36), nullable=True),
        # sa.ForeignKeyConstraint(['cluster_template_id'],
        #                         ['cluster_templates.id'], ),
        # sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'domain_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'vms',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('group_id', sa.String(length=36), nullable=True),
        # sa.Column('trust_id', sa.String(length=36), nullable=True),
        # sa.Column('is_transient', sa.Boolean(), nullable=True),
        # sa.Column('plugin_name', sa.String(length=80), nullable=False),
        # sa.Column('hadoop_version', sa.String(length=80), nullable=False),
        # sa.Column('cluster_configs', st.JsonDictType(), nullable=True),
        # sa.Column('default_image_id', sa.String(length=36), nullable=True),
        # sa.Column('neutron_management_network',
        #           sa.String(length=36), nullable=True),
        # sa.Column('anti_affinity', st.JsonDictType(), nullable=True),
        sa.Column('management_private_key', sa.Text(), nullable=False),
        sa.Column('management_public_key', sa.Text(), nullable=False),
        # sa.Column('user_keypair_id', sa.String(length=80), nullable=True),
        sa.Column('status', sa.String(length=80), nullable=True),
        sa.Column('status_description', sa.String(length=200), nullable=True),
        sa.Column('info', st.JsonDictType(), nullable=True),
        # sa.Column('extra', st.JsonDictType(), nullable=True),
        # sa.Column('cluster_template_id', sa.String(length=36), nullable=True),
        # sa.ForeignKeyConstraint(['cluster_template_id'],
        #                         ['cluster_templates.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'tenant_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'job_binary_internal',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('data', sa.LargeBinary(), nullable=True),
        sa.Column('datasize', sa.BIGINT(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'tenant_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'node_group_templates',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('flavor_id', sa.String(length=36), nullable=False),
        sa.Column('image_id', sa.String(length=36), nullable=True),
        sa.Column('plugin_name', sa.String(length=80), nullable=False),
        sa.Column('hadoop_version', sa.String(length=80), nullable=False),
        sa.Column('node_processes', st.JsonDictType(), nullable=True),
        sa.Column('node_configs', st.JsonDictType(), nullable=True),
        sa.Column('volumes_per_node', sa.Integer(), nullable=False),
        sa.Column('volumes_size', sa.Integer(), nullable=True),
        sa.Column('volume_mount_prefix', sa.String(length=80), nullable=True),
        sa.Column('floating_ip_pool', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'tenant_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'data_sources',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=80), nullable=False),
        sa.Column('url', sa.String(length=256), nullable=False),
        sa.Column('credentials', st.JsonDictType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'tenant_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'cluster_templates',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cluster_configs', st.JsonDictType(), nullable=True),
        sa.Column('default_image_id', sa.String(length=36), nullable=True),
        sa.Column('anti_affinity', st.JsonDictType(), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('neutron_management_network',
                  sa.String(length=36), nullable=True),
        sa.Column('plugin_name', sa.String(length=80), nullable=False),
        sa.Column('hadoop_version', sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'tenant_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'job_binaries',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=256), nullable=False),
        sa.Column('extra', st.JsonDictType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'tenant_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'jobs',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'tenant_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'templates_relations',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('flavor_id', sa.String(length=36), nullable=False),
        sa.Column('image_id', sa.String(length=36), nullable=True),
        sa.Column('node_processes', st.JsonDictType(), nullable=True),
        sa.Column('node_configs', st.JsonDictType(), nullable=True),
        sa.Column('volumes_per_node', sa.Integer(), nullable=True),
        sa.Column('volumes_size', sa.Integer(), nullable=True),
        sa.Column('volume_mount_prefix', sa.String(length=80), nullable=True),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('cluster_template_id', sa.String(length=36), nullable=True),
        sa.Column('node_group_template_id',
                  sa.String(length=36), nullable=True),
        sa.Column('floating_ip_pool', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['cluster_template_id'],
                                ['cluster_templates.id'], ),
        sa.ForeignKeyConstraint(['node_group_template_id'],
                                ['node_group_templates.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'mains_association',
        sa.Column('Job_id', sa.String(length=36), nullable=True),
        sa.Column('JobBinary_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['JobBinary_id'], ['job_binaries.id'], ),
        sa.ForeignKeyConstraint(['Job_id'], ['jobs.id'], ),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'libs_association',
        sa.Column('Job_id', sa.String(length=36), nullable=True),
        sa.Column('JobBinary_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['JobBinary_id'], ['job_binaries.id'], ),
        sa.ForeignKeyConstraint(['Job_id'], ['jobs.id'], ),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'clusters',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('trust_id', sa.String(length=36), nullable=True),
        sa.Column('is_transient', sa.Boolean(), nullable=True),
        sa.Column('plugin_name', sa.String(length=80), nullable=False),
        sa.Column('hadoop_version', sa.String(length=80), nullable=False),
        sa.Column('cluster_configs', st.JsonDictType(), nullable=True),
        sa.Column('default_image_id', sa.String(length=36), nullable=True),
        sa.Column('neutron_management_network',
                  sa.String(length=36), nullable=True),
        sa.Column('anti_affinity', st.JsonDictType(), nullable=True),
        sa.Column('management_private_key', sa.Text(), nullable=False),
        sa.Column('management_public_key', sa.Text(), nullable=False),
        sa.Column('user_keypair_id', sa.String(length=80), nullable=True),
        sa.Column('status', sa.String(length=80), nullable=True),
        sa.Column('status_description', sa.String(length=200), nullable=True),
        sa.Column('info', st.JsonDictType(), nullable=True),
        sa.Column('extra', st.JsonDictType(), nullable=True),
        sa.Column('cluster_template_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['cluster_template_id'],
                                ['cluster_templates.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'tenant_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'node_groups',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('flavor_id', sa.String(length=36), nullable=False),
        sa.Column('image_id', sa.String(length=36), nullable=True),
        sa.Column('image_username', sa.String(length=36), nullable=True),
        sa.Column('node_processes', st.JsonDictType(), nullable=True),
        sa.Column('node_configs', st.JsonDictType(), nullable=True),
        sa.Column('volumes_per_node', sa.Integer(), nullable=True),
        sa.Column('volumes_size', sa.Integer(), nullable=True),
        sa.Column('volume_mount_prefix', sa.String(length=80), nullable=True),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('cluster_id', sa.String(length=36), nullable=True),
        sa.Column('node_group_template_id',
                  sa.String(length=36), nullable=True),
        sa.Column('floating_ip_pool', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['cluster_id'], ['clusters.id'], ),
        sa.ForeignKeyConstraint(['node_group_template_id'],
                                ['node_group_templates.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'cluster_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'job_executions',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('job_id', sa.String(length=36), nullable=True),
        sa.Column('input_id', sa.String(length=36), nullable=True),
        sa.Column('output_id', sa.String(length=36), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('cluster_id', sa.String(length=36), nullable=True),
        sa.Column('info', st.JsonDictType(), nullable=True),
        sa.Column('progress', sa.Float(), nullable=True),
        sa.Column('oozie_job_id', sa.String(length=100), nullable=True),
        sa.Column('return_code', sa.String(length=80), nullable=True),
        sa.Column('job_configs', st.JsonDictType(), nullable=True),
        sa.Column('main_class', sa.Text(), nullable=True),
        sa.Column('java_opts', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['cluster_id'], ['clusters.id'], ),
        sa.ForeignKeyConstraint(['input_id'], ['data_sources.id'], ),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['output_id'], ['data_sources.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'instances',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('node_group_id', sa.String(length=36), nullable=True),
        sa.Column('instance_id', sa.String(length=36), nullable=True),
        sa.Column('instance_name', sa.String(length=80), nullable=False),
        sa.Column('internal_ip', sa.String(length=15), nullable=True),
        sa.Column('management_ip', sa.String(length=15), nullable=True),
        sa.Column('volumes', st.JsonDictType(), nullable=True),
        sa.ForeignKeyConstraint(['node_group_id'], ['node_groups.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('instance_id', 'node_group_id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )


def downgrade():
    op.drop_table('instances')
    op.drop_table('job_executions')
    op.drop_table('node_groups')
    op.drop_table('clusters')
    op.drop_table('libs_association')
    op.drop_table('mains_association')
    op.drop_table('templates_relations')
    op.drop_table('jobs')
    op.drop_table('job_binaries')
    op.drop_table('cluster_templates')
    op.drop_table('data_sources')
    op.drop_table('node_group_templates')
    op.drop_table('job_binary_internal')
