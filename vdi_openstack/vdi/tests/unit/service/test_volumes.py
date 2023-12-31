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

from cinderclient.v1 import volumes as v
import mock

from vdi.conductor import resource as r
from vdi import exceptions as ex
from vdi.service import volumes
from vdi.tests.unit import base


class TestAttachVolume(base.SaharaWithDbTestCase):

    @mock.patch(
        'vdi.service.engine.Engine.get_node_group_image_username')
    def test_mount_volume(self, p_get_username):
        p_get_username.return_value = 'root'

        instance = self._get_instance()
        execute_com = instance.remote().execute_command

        self.assertIsNone(volumes._mount_volume(instance, '123', '456'))
        self.assertEqual(execute_com.call_count, 3)

        execute_com.side_effect = ex.RemoteCommandException('cmd')
        self.assertRaises(ex.RemoteCommandException, volumes._mount_volume,
                          instance, '123', '456')

    @mock.patch('vdi.conductor.manager.ConductorManager.cluster_get')
    @mock.patch('cinderclient.v1.volumes.Volume.delete')
    @mock.patch('cinderclient.v1.volumes.Volume.detach')
    @mock.patch('vdi.utils.openstack.cinder.get_volume')
    def test_detach_volumes(self, p_get_volume, p_detach, p_delete, p_cond):
        class Instance:
            def __init__(self):
                self.instance_id = '123454321'
                self.volumes = [123]

        instance = Instance()
        p_get_volume.return_value = v.Volume(None, {'id': '123'})
        p_detach.return_value = None
        p_delete.return_value = None
        self.assertIsNone(
            volumes.detach_from_instance(instance))

        p_delete.side_effect = RuntimeError
        self.assertRaises(RuntimeError, volumes.detach_from_instance, instance)

    @mock.patch('vdi.service.volumes._mount_volume')
    @mock.patch('vdi.service.volumes._await_attach_volumes')
    @mock.patch('vdi.service.volumes._create_attach_volume')
    @mock.patch('vdi.service.volumes._get_unmounted_devices')
    def test_attach(self, p_dev_path, p_create_attach_vol,
                    p_await, p_mount):
        p_dev_path.return_value = ['123', '456']
        p_create_attach_vol.return_value = None
        p_await.return_value = None
        p_mount.return_value = None

        instance1 = {'instance_id': '123',
                     'instance_name': 'inst_1'}
        instance2 = {'instance_id': '456',
                     'instance_name': 'inst_2'}

        ng = {'volumes_per_node': 2,
              'volumes_size': 2,
              'volume_mount_prefix': '/mnt/vols',
              'name': 'master',
              'instances': [instance1, instance2]}

        cluster = r.ClusterResource({'node_groups': [ng]})

        volumes.attach(cluster)
        self.assertEqual(p_create_attach_vol.call_count, 4)
        self.assertEqual(p_await.call_count, 2)
        self.assertEqual(p_mount.call_count, 4)
        self.assertEqual(p_dev_path.call_count, 2)

    @mock.patch('vdi.context.sleep')
    @mock.patch('vdi.service.volumes._get_unmounted_devices')
    def test_await_attach_volume(self, dev_paths, p_sleep):
        dev_paths.return_value = ['/dev/vda', '/dev/vdb']
        p_sleep.return_value = None
        instance = r.InstanceResource({'instance_id': '123454321',
                                       'instance_name': 'instt'})
        self.assertIsNone(volumes._await_attach_volumes(instance, 2))
        self.assertRaises(RuntimeError, volumes._await_attach_volumes,
                          instance, 3)

    def test_get_unmounted_devices(self):
        partitions = """major minor  #blocks  name

   7        0   41943040 vdd
   7        1  102400000 vdc
   7        1  222222222 vdc1
   8        0  976762584 vda
   8        0  111111111 vda1
   8        1  842576896 vdb"""

        mount = """
/dev/vda1 qwe rty
/dev/vdb asd fgh"""

        instance = self._get_instance()
        ex_cmd = instance.remote().execute_command
        ex_cmd.side_effect = [(0, partitions), (0, mount)]

        self.assertEqual(
            volumes._get_unmounted_devices(instance), ['/dev/vdd'])

    def _get_instance(self):
        inst_remote = mock.MagicMock()
        inst_remote.execute_command.return_value = 0
        inst_remote.__enter__.return_value = inst_remote

        inst = mock.MagicMock()
        inst.remote.return_value = inst_remote

        return inst
