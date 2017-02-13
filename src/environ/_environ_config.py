from __future__ import absolute_import, division, print_function

import os
import sys

import attr

from .exceptions import MissingEnvValueError


CNF_KEY = object()


@attr.s
class Raise(object):
    pass


RAISE = Raise()


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


def config(maybe_cls=None, vault_prefix=None, prefix="APP"):
    def wrap(cls):
        cls._vault_prefix = vault_prefix
        cls._prefix = prefix
        return attr.s(cls, slots=True, frozen=True)

    if maybe_cls is None:
        return wrap
    else:
        return wrap(maybe_cls)


@attr.s(slots=True, frozen=True)
class _ConfigEntry(object):
    name = attr.ib(default=None)
    default = attr.ib(default=RAISE)
    sub_cls = attr.ib(default=None)
    from_vault = attr.ib(default=False)


def var(default=RAISE, convert=None, name=None):
    return attr.ib(
        default=default,
        metadata={CNF_KEY: _ConfigEntry(name, default, None, False)},
        convert=convert,
    )


def vault_var(default=RAISE, name=None):
    return attr.ib(
        default=default,
        metadata={CNF_KEY: _ConfigEntry(name, default, None, True)}
    )


def group(cls):
    return attr.ib(
        default=None,
        metadata={CNF_KEY: _ConfigEntry(None, None, cls, True)}
    )


def to_config(config_cls, environ=os.environ, prefix=None, vault_prefix=None):
    if prefix is None:
        prefix = config_cls._prefix or ""
    if vault_prefix is None:
        vault_prefix = config_cls._vault_prefix or ""

    vals = {}
    for a in attr.fields(config_cls):
        name = a.name.upper()
        cm = a.metadata[CNF_KEY]
        if cm.sub_cls is None:
            if cm.name is not None:
                var = cm.name
            elif cm.from_vault is False:
                p = prefix + "_" if prefix else ""
                var = p + name
            else:
                p = vault_prefix + "_" if vault_prefix else ""
                var = "SECRET_" + p + name

            val = environ.get(var, cm.default)
            if val is RAISE:
                raise MissingEnvValueError(var)

            if cm.from_vault is True and val is not None:
                val = _SecretStr(val)

            if name == "ENV" and "{env}" in vault_prefix:
                vault_prefix = vault_prefix.replace("{env}", val.upper())
        else:
            val = to_config(
                cm.sub_cls, environ,
                prefix + "_" + name,
                vault_prefix + "_" + name
                if vault_prefix is not None else None,
            )

        vals[a.name] = val
    return config_cls(**vals)
