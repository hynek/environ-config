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


def config(
    maybe_cls=None,
    prefix="APP",
    from_environ="from_environ",
    generate_help="generate_help",
):
    def wrap(cls):
        def from_environ_fnc(cls, environ=os.environ):
            import environ as environ_config

            return environ_config.to_config(cls, environ)

        def generate_help_fnc(cls, **kwargs):
            import environ

            return environ.generate_help(cls, **kwargs)

        cls._prefix = prefix
        if from_environ is not None:
            setattr(cls, from_environ, classmethod(from_environ_fnc))
        if generate_help is not None:
            setattr(cls, generate_help, classmethod(generate_help_fnc))
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
    help = attr.ib(default=None)


def var(default=RAISE, converter=None, name=None, validator=None, help=None):
    return attr.ib(
        default=default,
        metadata={CNF_KEY: _ConfigEntry(name, default, None, None, help)},
        converter=converter,
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


def bool_var(default=RAISE, name=None, help=None):
    return var(default=default, name=name, converter=_env_to_bool, help=help)


def group(cls):
    return attr.ib(
        default=None, metadata={CNF_KEY: _ConfigEntry(None, None, cls, True)}
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
        val = environ.get(
            var,
            (
                attr.NOTHING
                if isinstance(ce.default, attr.Factory)
                else ce.default
            ),
        )
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
                ce.sub_cls,
                default_get,
                environ,
                prefix + ((a.name if prefix else a.name),),
            )

        vals[a.name] = val
    return config_cls(**vals)


def _format_help_dicts(help_dicts, display_defaults=False):
    """
    Format the output of _generate_help_dicts into a str
    """
    help_strs = []
    for help_dict in help_dicts:
        help_str = "%s (%s" % (
            help_dict["var_name"],
            "Required" if help_dict["required"] else "Optional",
        )
        if help_dict.get("default") and display_defaults:
            help_str += ", Default=%s)" % help_dict["default"]
        else:
            help_str += ")"
        if help_dict.get("help_str"):
            help_str += ": %s" % help_dict["help_str"]
        help_strs.append(help_str)

    return "\n".join(help_strs)


def _generate_help_dicts(config_cls, _prefix=None):
    """
    Generate dictionaries for use in building help strings.

    Every dictionary includes the keys...

    var_name: The env var that should be set to populate the value.
    required: A bool, True if the var is required, False if it's optional.

    Conditionally, the following are included...

    default: Included if an optional variable has a default set
    help_str: Included if the var uses the help kwarg to provide additional
        context for the value.

    Conditional key inclusion is meant to differentiate between exclusion
    vs explicitly setting a value to None.
    """
    help_dicts = []
    if _prefix is None:
        _prefix = config_cls._prefix
    for a in attr.fields(config_cls):
        try:
            ce = a.metadata[CNF_KEY]
        except KeyError:
            continue
        if ce.sub_cls is None:  # Base case for "leaves".
            if ce.name is None:
                var_name = "_".join((_prefix, a.name)).upper()
            else:
                var_name = ce.name
            req = ce.default == RAISE
            help_dict = {"var_name": var_name, "required": req}
            if not req:
                help_dict["default"] = ce.default
            if ce.help is not None:
                help_dict["help_str"] = ce.help
            help_dicts.append(help_dict)
        else:  # Construct the new prefix and recurse.
            help_dicts += _generate_help_dicts(
                ce.sub_cls, _prefix="_".join((_prefix, a.name)).upper()
            )
    return help_dicts


def generate_help(config_cls, **kwargs):
    """
    Autogenerate a help string for a config class.

    If a callable is provided via the "formatter" kwarg it
    will be provided with the help dictionaries as an argument
    and any other kwargs provided to this function. That callable
    should return the help text string.
    """
    try:
        formatter = kwargs.pop("formatter")
    except KeyError:
        formatter = _format_help_dicts
    help_dicts = _generate_help_dicts(config_cls)
    return formatter(help_dicts, **kwargs)
