from __future__ import absolute_import, division, print_function

import logging
import os

import attr

from .exceptions import MissingEnvValueError


log = logging.getLogger(__name__)


CNF_KEY = "environ_config"


@attr.s
class Raise(object):
    pass


RAISE = Raise()


def config(maybe_cls=None, prefix="APP"):
    def wrap(cls):
        cls._prefix = prefix
        return attr.s(cls, slots=True)

    if maybe_cls is None:
        return wrap
    else:
        return wrap(maybe_cls)


@attr.s(slots=True)
class _ConfigEntry(object):
    name = attr.ib(default=None)
    default = attr.ib(default=RAISE)
    sub_cls = attr.ib(default=None)
    callback = attr.ib(default=None)


def var(default=RAISE, convert=None, name=None, validator=None):
    return attr.ib(
        default=default,
        metadata={CNF_KEY: _ConfigEntry(name, default, None)},
        convert=convert,
        validator=validator,
    )


def _env_to_bool(val):
    """
    Convert *val* to a bool if it's not a bool in the first place.
    """
    if isinstance(val, bool):
        return val
    val = val.strip().lower()
    if val in ("1", "true", "yes"):
        return True

    return False


def bool_var(default=RAISE, name=None):
    return var(
        default=default,
        name=name,
        convert=_env_to_bool,
    )


def group(cls):
    return attr.ib(
        default=None,
        metadata={CNF_KEY: _ConfigEntry(None, None, cls, True)}
    )


def to_config(config_cls, environ=os.environ):
    if config_cls._prefix:
        app_prefix = (config_cls._prefix,)
    else:
        app_prefix = ()

    def default_get(environ, metadata, prefix, name):
        ce = metadata[CNF_KEY]
        if ce.name is not None:
            var = ce.name
        else:
            var = ("_".join(app_prefix + prefix + (name,))).upper()

        log.debug("looking for env var '%s'." % (var,))
        val = environ.get(var, ce.default)
        if val is RAISE:
            raise MissingEnvValueError(var)
        return val

    return _to_config(config_cls, default_get, environ, ())


def _to_config(config_cls, default_get, environ, prefix):
    vals = {}
    for a in attr.fields(config_cls):
        try:
            ce = a.metadata[CNF_KEY]
        except KeyError:
            continue
        if ce.sub_cls is None:
            get = ce.callback or default_get
            val = get(environ, a.metadata, prefix, a.name)
        else:
            val = _to_config(
                ce.sub_cls, default_get, environ,
                prefix + ((a.name if prefix else a.name),)
            )

        vals[a.name] = val
    return config_cls(**vals)
