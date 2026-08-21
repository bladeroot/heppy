# -*- coding: utf-8 -*-

import os

ENV_OVERRIDES = {
    'username': 'RABBITMQ_USERNAME',
    'password': 'RABBITMQ_PASSWORD',
}


class RabbitMQConfig:
    """Resolves the final RabbitMQ.* config dict for a worker: config file
    values, the default queue name, and RABBITMQ_USERNAME/PASSWORD env-var
    overrides. Env vars win when *present* (checked via `in os.environ`, not
    truthiness) so a value that resolves to an empty string still overrides
    instead of silently falling back to a stale config value. A deployment
    can inject these from the same secret the broker itself reads, so a
    credential rotation only needs the env var updated instead of resealing
    every worker's config file to match a copy of the password."""

    def __init__(self, config):
        self.config = config

    def resolve(self):
        rabbit_config = dict(self.config.get('RabbitMQ', {}))
        rabbit_config.setdefault('queue', 'heppy-' + self.config['name'])
        for key, env_name in ENV_OVERRIDES.items():
            if env_name in os.environ:
                rabbit_config[key] = os.environ[env_name]
        return rabbit_config
