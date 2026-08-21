# -*- coding: utf-8 -*-

import os

ENV_OVERRIDES = {
    'username': 'RABBITMQ_USERNAME',
    'password': 'RABBITMQ_PASSWORD',
}


class RabbitMQConfig:
    """Resolves the final RabbitMQ.* config dict for a worker: config file
    values, the default queue name, and RABBITMQ_USERNAME/PASSWORD overrides
    -- each settable directly as an env var, or as a path via the matching
    _FILE env var (e.g. RABBITMQ_PASSWORD_FILE), the same convention the
    official rabbitmq Docker image itself uses for RABBITMQ_DEFAULT_PASS_FILE
    -- so a deployment can point both the broker and every worker at the
    same mounted secret file instead of (or alongside) plain env vars.

    An override is applied whenever its source is *present*, even if the
    resulting value is an empty string -- checked via `in os.environ` /
    reading the file, never truthiness -- so it can't be silently mistaken
    for "unset" and fall back to a stale config value. Setting both the
    plain var and its _FILE counterpart for the same key is rejected
    outright rather than picking one silently.

    A deployment injects these from the same secret the broker itself
    reads, so a credential rotation only needs that one secret updated
    instead of resealing every worker's config file to match a copy of the
    password."""

    def __init__(self, config):
        self.config = config

    def resolve(self):
        rabbit_config = dict(self.config.get('RabbitMQ', {}))
        rabbit_config.setdefault('queue', 'heppy-' + self.config['name'])
        for key, env_name in ENV_OVERRIDES.items():
            value = self._env_override(env_name)
            if value is not None:
                rabbit_config[key] = value
        return rabbit_config

    def _env_override(self, env_name):
        file_env_name = env_name + '_FILE'
        has_value = env_name in os.environ
        has_file = file_env_name in os.environ
        if has_value and has_file:
            raise ValueError(f"both {env_name} and {file_env_name} are set - pick one")
        if has_value:
            return os.environ[env_name]
        if has_file:
            with open(os.environ[file_env_name]) as f:
                return f.read().rstrip('\n')
        return None
