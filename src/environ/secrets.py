# Copyright 2017 Hynek Schlawack

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
Handling of sensitive data.
"""

from __future__ import absolute_import, division, print_function

import codecs
import logging
import sys

from configparser import NoOptionError, RawConfigParser

import attr

from ._environ_config import CNF_KEY, RAISE, _ConfigEntry
from .exceptions import MissingSecretError


log = logging.getLogger(__name__)


@attr.s
class INISecrets(object):
    """
    Load secrets from an `INI file <https://en.wikipedia.org/wiki/INI_file>`_
    using `configparser.RawConfigParser`.
    """

    section = attr.ib()
    _cfg = attr.ib(default=None)
    _env_name = attr.ib(default=None)
    _env_default = attr.ib(default=None)

    @classmethod
    def from_path(cls, path, section="secrets"):
        """
        Look for secrets in *section* of *path*.

        :param str path: A path to an INI file.
        :param str section: The section in the INI file to read the secrets
            from.
        """
        return cls(section, _load_ini(path), None, None)

    @classmethod
    def from_path_in_env(cls, env_name, default=None, section="secrets"):
        """
        Get the path from the environment variable *env_name* **at runtime**
        and then load the secrets from it.

        This allows you to overwrite the path to the secrets file in
        development.

        :param str env_name: Environment variable that is used to determine the
            path of the secrets file.
        :param str default: The default path to load from.
        :param str section: The section in the INI file to read the secrets
            from.
        """
        return cls(section, None, env_name, default)

    def secret(
        self, default=RAISE, converter=None, name=None, section=None, help=None
    ):
        """
        Declare a secret on an `environ.config`-decorated class.

        :param str section: Overwrite the section where to look for the values.

        Other parameters work just like in `environ.var`.
        """
        if section is None:
            section = self.section

        return attr.ib(
            default=default,
            metadata={
                CNF_KEY: _ConfigEntry(name, default, None, self._get, help),
                CNF_INI_SECRET_KEY: _INIConfig(section),
            },
            converter=converter,
        )

    def _get(self, environ, metadata, prefix, name):
        # Delayed loading.
        if self._cfg is None and self._env_name is not None:
            log.debug("looking for env var '%s'." % (self._env_name,))
            self._cfg = _load_ini(
                environ.get(self._env_name, self._env_default)
            )

        ce = metadata[CNF_KEY]
        ic = metadata[CNF_INI_SECRET_KEY]
        section = ic.section

        if ce.name is not None:
            var = ce.name
        else:
            var = "_".join((prefix + (name,)))
        try:
            log.debug("looking for '%s' in section '%s'." % (var, section))
            return _SecretStr(self._cfg.get(section, var))
        except NoOptionError:
            if isinstance(ce.default, attr.Factory):
                return attr.NOTHING
            elif ce.default is not RAISE:
                return ce.default
            raise MissingSecretError(var)


@attr.s
class VaultEnvSecrets(object):
    """
    Loads secrets from environment variables that follow the naming style from
    `envconsul <https://github.com/hashicorp/envconsul>`_.
    """

    vault_prefix = attr.ib()

    def secret(self, default=RAISE, converter=None, name=None, help=None):
        """
        Almost identical to `environ.var` except that it takes *envconsul*
        naming into account.
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

        if ce.name is not None:
            var = ce.name
        else:
            if callable(self.vault_prefix):
                vp = self.vault_prefix(environ)
            else:
                vp = self.vault_prefix
            var = "_".join(((vp,) + prefix + (name,))).upper()

        log.debug("looking for env var '%s'." % (var,))
        val = environ.get(
            var,
            (
                attr.NOTHING
                if isinstance(ce.default, attr.Factory)
                else ce.default
            ),
        )
        if val is RAISE:
            raise MissingSecretError(var)
        return _SecretStr(val)


class _SecretStr(str):
    """
    String that censors its __repr__ if called from an attrs repr.
    """

    def __repr__(self):
        # The frame numbers varies across attrs versions. Use this convoluted
        # form to make the call lazy.
        if (
            sys._getframe(1).f_code.co_name == "__repr__"
            or sys._getframe(2).f_code.co_name == "__repr__"
        ):
            return "<SECRET>"
        else:
            return str.__repr__(self)


CNF_INI_SECRET_KEY = CNF_KEY + "_ini_secret"


@attr.s
class _INIConfig(object):
    section = attr.ib()


def _load_ini(path):
    """
    Load an INI file from *path*.
    """
    cfg = RawConfigParser()
    with codecs.open(path, mode="r", encoding="utf-8") as f:
        cfg.read_file(f)

    return cfg
