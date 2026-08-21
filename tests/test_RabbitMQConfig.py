# -*- coding: utf-8 -*-

import os
import unittest
from heppy.RabbitMQConfig import RabbitMQConfig


class FakeConfig(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


class TestRabbitMQConfig(unittest.TestCase):
    def setUp(self):
        self._env = dict(os.environ)
        os.environ.pop('RABBITMQ_USERNAME', None)
        os.environ.pop('RABBITMQ_PASSWORD', None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)

    def test_defaults_queue_name_from_config_name(self):
        config = FakeConfig({'name': 'donuts.epp'})

        resolved = RabbitMQConfig(config).resolve()

        self.assertEqual(resolved['queue'], 'heppy-donuts.epp')

    def test_keeps_explicit_queue_name(self):
        config = FakeConfig({'name': 'donuts.epp', 'RabbitMQ': {'queue': 'heppy-custom'}})

        resolved = RabbitMQConfig(config).resolve()

        self.assertEqual(resolved['queue'], 'heppy-custom')

    def test_env_vars_override_config_credentials(self):
        os.environ['RABBITMQ_USERNAME'] = 'env-user'
        os.environ['RABBITMQ_PASSWORD'] = 'env-pass'
        config = FakeConfig({'name': 'x', 'RabbitMQ': {'username': 'file-user', 'password': 'file-pass'}})

        resolved = RabbitMQConfig(config).resolve()

        self.assertEqual(resolved['username'], 'env-user')
        self.assertEqual(resolved['password'], 'env-pass')

    def test_falls_back_to_config_when_env_vars_unset(self):
        config = FakeConfig({'name': 'x', 'RabbitMQ': {'username': 'file-user', 'password': 'file-pass'}})

        resolved = RabbitMQConfig(config).resolve()

        self.assertEqual(resolved['username'], 'file-user')
        self.assertEqual(resolved['password'], 'file-pass')

    def test_env_username_alone_still_sets_credentials(self):
        # Covers workers whose config has no RabbitMQ.username at all
        # (e.g. verisign-ctldepp) -- env injection should still authenticate.
        os.environ['RABBITMQ_USERNAME'] = 'env-user'
        config = FakeConfig({'name': 'x'})

        resolved = RabbitMQConfig(config).resolve()

        self.assertEqual(resolved['username'], 'env-user')
        self.assertNotIn('password', resolved)

    def test_empty_env_var_overrides_rather_than_falling_back(self):
        # A present-but-empty env var (e.g. a misconfigured secretKeyRef
        # resolving to "") must win over a stale config value, not be
        # silently treated as "unset" -- that would reintroduce exactly the
        # kind of drift this class exists to prevent.
        os.environ['RABBITMQ_PASSWORD'] = ''
        config = FakeConfig({'name': 'x', 'RabbitMQ': {'username': 'file-user', 'password': 'file-pass'}})

        resolved = RabbitMQConfig(config).resolve()

        self.assertEqual(resolved['password'], '')


if __name__ == '__main__':
    unittest.main()
