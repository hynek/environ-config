# Copyright 2021 Chris Rose

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Handling of sensitive data stored in AWS SecretsManager
"""
import functools
import logging

import attr
import boto3

from environ._environ_config import CNF_KEY, RAISE, _ConfigEntry

from ._utils import _get_default_secret


log = logging.getLogger(__name__)


def convert_secret(key):
    def converter(value):
        if isinstance(value, str):
            return value
        return value[key]

    return converter


@attr.s
class SecretsManagerSecrets(object):
    """
    Load secrets from the AWS secretsmanager.

    The secret name should be stored in the environment variable

    .. versionadded:: 21.4.0
    """

    client = attr.ib(
        default=attr.Factory(functools.partial(boto3.client, "secretsmanager"))
    )

    def secret(
        self,
        default=RAISE,
        converter=convert_secret("SecretString"),
        name=None,
        help=None,
    ):
        """
        Declare a secrets manager secret on an `environ.config`-decorated class

        All parameters work just like in `environ.var`.
        """
        return attr.ib(
            default=default,
            metadata={
                CNF_KEY: _ConfigEntry(name, default, None, self._get, help)
            },
            converter=converter,
        )

    def _get(self, environ, metadata, prefix, name):
        ce = metadata[CNF_KEY]
        if ce.name:
            secret_name_envvar = ce.name
            log.debug(
                "override env variable with explicit name %s",
                secret_name_envvar,
            )
        else:
            parts = prefix + (name,)
            secret_name_envvar = "_".join(parts).upper()
            log.debug(
                "secret name environment variable %s", secret_name_envvar
            )

        try:
            secret_name = environ[secret_name_envvar]
        except KeyError:
            # missing the environment; let's try to get the default
            log.debug(
                "no key %s in environment, using default=%s",
                secret_name_envvar,
                ce.default,
            )
            return _get_default_secret(secret_name_envvar, ce.default)
        log.debug("secret name: %s", secret_name)

        return self.client.get_secret_value(SecretId=secret_name)
