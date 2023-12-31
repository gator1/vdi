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

import eventlet
import mock
import unittest2

from vdi import context
from vdi import exceptions


eventlet.monkey_patch()
rnd = random.Random()


class ContextTest(unittest2.TestCase):
    def setUp(self):
        ctx = context.Context('test_user', 'tenant_1', 'test_auth_token', {},
                              remote_semaphore='123')
        context.set_ctx(ctx)

    def _add_element(self, lst, i):
        context.sleep(rnd.uniform(0, 0.1))
        lst.append(i)

    def _raise_test_exc(self, exc_msg):
        raise TestException(exc_msg)

    def test_thread_group_waits_threads(self):
        # That can fail with some probability, so making 5 attempts
        # Actually it takes around 1 second, so maybe we should
        # just remove it
        for _ in range(5):
            lst = []

            with context.ThreadGroup() as tg:
                for i in range(400):
                    tg.spawn('add %i' % i, self._add_element, lst, i)

            self.assertEqual(len(lst), 400)

    def test_thread_group_waits_threads_if_spawning_exception(self):
        lst = []

        with self.assertRaises(Exception):
            with context.ThreadGroup() as tg:
                for i in range(400):
                    tg.spawn('add %i' % i, self._add_element, lst, i)

                raise RuntimeError()

        self.assertEqual(len(lst), 400)

    def test_thread_group_waits_threads_if_child_exception(self):
        lst = []

        with self.assertRaises(Exception):
            with context.ThreadGroup() as tg:
                tg.spawn('raiser', self._raise_test_exc, 'exc')

                for i in range(400):
                    tg.spawn('add %i' % i, self._add_element, lst, i)

        self.assertEqual(len(lst), 400)

    def test_thread_group_handles_spawning_exception(self):
        with self.assertRaises(TestException):
            with context.ThreadGroup():
                raise TestException()

    def test_thread_group_handles_child_exception(self):
        try:
            with context.ThreadGroup() as tg:
                tg.spawn('raiser1', self._raise_test_exc, 'exc1')
        except exceptions.ThreadException as te:
            self.assertIn('exc1', te.message)
            self.assertIn('raiser1', te.message)

    def test_thread_group_prefers_spawning_exception(self):
        with self.assertRaises(RuntimeError):
            with context.ThreadGroup() as tg:
                tg.spawn('raiser1', self._raise_test_exc, 'exc1')
                raise RuntimeError()

    def test_wrapper_does_not_set_exception(self):
        func = mock.MagicMock()

        tg = mock.MagicMock(exc=None, failed_thread=None)

        context._wrapper(None, 'test thread', tg, func)

        self.assertIsNone(tg.exc)
        self.assertIsNone(tg.failed_thread)

    def test_wrapper_catches_base_exception(self):
        func = mock.MagicMock()
        func.side_effect = BaseException()

        tg = mock.MagicMock(exc=None, failed_thread=None)

        context._wrapper(None, 'test thread', tg, func)

        self.assertIsNotNone(tg.exc)
        self.assertEqual(tg.failed_thread, 'test thread')

    def test_is_auth_capable_for_admin_ctx(self):
        ctx = context.ctx()
        self.assertFalse(ctx.is_auth_capable())

    def test_is_auth_capable_for_user_ctx(self):
        existing_ctx = context.ctx()
        try:
            ctx = context.Context('test_user', 'tenant_1', 'test_auth_token',
                                  {"network": "aURL"}, remote_semaphore='123')
            self.assertTrue(ctx.is_auth_capable())
        finally:
            context.set_ctx(existing_ctx)


class TestException(Exception):
    pass
