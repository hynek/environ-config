from __future__ import absolute_import, division, print_function

import codecs
import logging
import sys

try:
    from configparser import ConfigParser, NoOptionError
except ImportError:
    from ConfigParser import ConfigParser, NoOptionError

import attr

from .exceptions import MissingSecretError
from ._environ_config import RAISE, CNF_KEY, _ConfigEntry


log = logging.getLogger(__name__)


@attr.s
class INISecrets(object):
    section = attr.ib()
    cfg = attr.ib()

    @classmethod
    def from_path(cls, path, section="secrets"):
        cfg = ConfigParser()
        with codecs.open(path, mode="r", encoding="utf-8") as f:
            try:
                cfg.read_file(f)
            except AttributeError:
                cfg.readfp(f)

        return cls(
            section, cfg
        )

    def secret(self, default=RAISE, convert=None, name=None, section=None):
        if section is None:
            section = self.section

        return attr.ib(
            default=default,
            metadata={
                CNF_KEY: _ConfigEntry(name, default, None, self._get),
                CNF_INI_SECRET_KEY: _INIConfig(section),
            },
            convert=convert,
        )

    def _get(self, environ, metadata, prefix, name):
        ce = metadata[CNF_KEY]
        ic = metadata[CNF_INI_SECRET_KEY]
        section = ic.section

        if ce.name is not None:
            var = ce.name
        else:
            var = "_".join((prefix + (name,)))
        try:
            log.debug("looking for '%s' in section '%s'." % (var, section,))
            return _SecretStr(self.cfg.get(section, var))
        except NoOptionError:
            if ce.default is not RAISE:
                return ce.default
            raise MissingSecretError(var)


@attr.s
class VaultEnvSecrets(object):
    """
    Almost identical to regular env vars except that it has its own prefix.
    """
    vault_prefix = attr.ib()

    def secret(self, default=RAISE, convert=None, name=None):
        return attr.ib(
            default=default,
            metadata={CNF_KEY: _ConfigEntry(name, default, None, self._get)},
            convert=convert,
        )

    def _get(self, environ, metadata, prefix, name):
        ce = metadata[CNF_KEY]

        if ce.name is not None:
            var = ce.name
        else:
            var = "_".join(
                ((self.vault_prefix,) + prefix + (name,))
            ).upper()

        log.debug("looking for env var '%s'." % (var,))
        val = environ.get(var, ce.default)
        if val is RAISE:
            raise MissingSecretError(var)
        return _SecretStr(val)


class _SecretStr(str):
    """
    String that censors its __repr__ if called from an attrs repr.
    """
    def __repr__(self):
        f = sys._getframe(2)

        if f.f_code.co_name == "repr_":
            return "<SECRET>"
        else:
            return str.__repr__(self)


CNF_INI_SECRET_KEY = CNF_KEY + "_ini_secret"


@attr.s
class _INIConfig(object):
    section = attr.ib()
