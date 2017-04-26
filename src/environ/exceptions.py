"""
Exceptions raised by environ_config.
"""

from __future__ import absolute_import, division, print_function


class ConfigError(Exception):
    pass


class MissingEnvValueError(ConfigError):
    pass


class MissingSecretError(ConfigError):
    pass
