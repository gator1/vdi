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

import random

from oslo.config import cfg

from vdi import conductor as c
from vdi import context
from vdi.openstack.common import log
from vdi.openstack.common import periodic_task
from vdi.openstack.common import threadgroup
from vdi.openstack.common import timeutils
from vdi.service import api
from vdi.service.edp import job_manager
from vdi.service import trusts


LOG = log.getLogger(__name__)

periodic_opts = [
    cfg.BoolOpt('periodic_enable',
                default=True,
                help='Enable periodic tasks.'),
    cfg.IntOpt('periodic_fuzzy_delay',
               default=60,
               help='Range in seconds to randomly delay when starting the'
                    ' periodic task scheduler to reduce stampeding.'
                    ' (Disable by setting to 0).'),
    cfg.IntOpt('periodic_interval_max',
               default=60,
               help='Max interval size between periodic tasks execution in '
                    'seconds'),
    cfg.IntOpt('min_transient_cluster_active_time',
               default=0,
               help='Minimal "lifetime" in seconds for a transient cluster. '
                    'Cluster is guarantied to be "alive" within this time '
                    'period.'),
]

CONF = cfg.CONF
CONF.register_opts(periodic_opts)

conductor = c.API


class SaharaPeriodicTasks(periodic_task.PeriodicTasks):
    @periodic_task.periodic_task(spacing=45, run_immediately=True)
    def update_job_statuses(self, ctx):
        LOG.debug('Updating job statuses')
        ctx = context.get_admin_context()
        context.set_ctx(ctx)
        job_manager.update_job_statuses()
        context.set_ctx(None)

    @periodic_task.periodic_task(spacing=90)
    def terminate_unneeded_clusters(self, ctx):
        LOG.debug('Terminating unneeded clusters')
        ctx = context.get_admin_context()
        context.set_ctx(ctx)
        for cluster in conductor.cluster_get_all(ctx, status='Active'):
            if not cluster.is_transient:
                continue

            jc = conductor.job_execution_count(ctx,
                                               end_time=None,
                                               cluster_id=cluster.id)

            if jc > 0:
                continue

            cluster_updated_at = timeutils.normalize_time(
                timeutils.parse_isotime(cluster.updated_at))
            current_time = timeutils.utcnow()
            spacing = timeutils.delta_seconds(cluster_updated_at, current_time)
            if spacing < CONF.min_transient_cluster_active_time:
                continue

            if CONF.use_identity_api_v3:
                trusts.use_os_admin_auth_token(cluster)
                api.terminate_cluster(cluster.id)
                LOG.debug('Terminated cluster %s with id %s' %
                          (cluster.name, cluster.id))
            else:
                if cluster.status != 'AwaitingTermination':
                    conductor.cluster_update(
                        ctx,
                        cluster,
                        {'status': 'AwaitingTermination'})
        context.set_ctx(None)


def setup(app):
    if CONF.periodic_enable:
        if CONF.periodic_fuzzy_delay:
            initial_delay = random.randint(0, CONF.periodic_fuzzy_delay)
            LOG.debug("Starting periodic tasks with initial delay '%s' "
                      "seconds", initial_delay)
        else:
            initial_delay = None

        app.tg = threadgroup.ThreadGroup()
        pt = SaharaPeriodicTasks()
        app.tg.add_dynamic_timer(
            pt.run_periodic_tasks,
            initial_delay=initial_delay,
            periodic_interval_max=CONF.periodic_interval_max,
            context=None)
