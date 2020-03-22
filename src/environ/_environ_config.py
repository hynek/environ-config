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


CNF_KEY = "environ_config"
log = logging.getLogger(CNF_KEY)


@attr.s
class Raise(object):
    pass


RAISE = Raise()


def config(
    maybe_cls=None,
    prefix="APP",
    from_environ="from_environ",
    generate_help="generate_help",
    frozen=False,
):
    """
    Make a class a configuration class.

    :param str prefix: The prefix that is used for the env variables.  If you
        have an `var` attribute on the class and your leave the default
        *prefix* of ``APP``, *environ-config* will look for an environment
        variable called ``APP_VAR``.
    :param str from_environ: If not `None`, attach a config loading method with
        the name *from_environ* to the class.  See `to_config` for more
        information.
    :param str generate_help: If not `None`, attach a config loading method
        with the name *generate_help* to the class.  See `generate_help` for
        more information.
    :param bool frozen: The configuration will be immutable after
        instantiation, if `True`.

    .. versionadded:: 19.1.0
       *from_environ*
    .. versionadded:: 19.1.0
       *generate_help*
    .. versionadded:: 20.1.0
       *frozen*
    """

    def wrap(cls):
        def from_environ_fnc(cls, environ=os.environ):
            return __to_config(cls, environ)

        def generate_help_fnc(cls, **kwargs):
            return __generate_help(cls, **kwargs)

        cls._prefix = prefix
        if from_environ is not None:
            setattr(cls, from_environ, classmethod(from_environ_fnc))
        if generate_help is not None:
            setattr(cls, generate_help, classmethod(generate_help_fnc))
        return attr.s(cls, frozen=frozen, slots=True)

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
    """
    Declare a configuration attribute on the body of `config`-decorated class.

    It will be attempted to be filled from an environment variable based on the
    prefix and *name*.

    :param default: Setting this to a value makes the config attribute
        optional.
    :param str name: Overwrite name detection with a string.  If not set, the
        name of the attribute is used.
    :param converter: A callable that is run with the found value and
        its return value is used.  Please not that it is also run for default
        values.
    :param validator: A callable that is run with the final value.
        See ``attrs``'s `chapter on validation
        <https://www.attrs.org/en/stable/init.html#validators>`_ for details.
        You can also use any validator that is `shipped with attrs
        <https://www.attrs.org/en/stable/api.html#validators>`_.
    :param str help: A help string that is used by `generate_help`.
    """
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
    """
    Like `var`, but converts the value to a `bool`.

    The following values are considered `True`:

    - ``True`` (if you set a *default*)
    - ``"1"``
    - ``"true"``
    - ``"yes"``

    Every other value is interpreted as `False`.  Leading and trailing
    whitespace is ignored.
    """
    return var(default=default, name=name, converter=_env_to_bool, help=help)


def group(cls):
    """
    A configuration attribute that is another configuration class.

    This way you can nest your configuration hierarchically although the values
    are coming from a flat source.

    The group's name is used to build a namespace::

       @environ.config
       class Cfg:
           @environ.config
           class Sub:
               x = environ.var()

           sub = environ.group(Sub)

    The value of ``x`` is looked up using ``APP_SUB_X``.

    You can nest your configuration as deeply as you wish.
    """
    return attr.ib(
        default=None, metadata={CNF_KEY: _ConfigEntry(None, None, cls, True)}
    )


def to_config(config_cls, environ=os.environ):
    """
    Load the configuration as declared by *config_cls* from *environ*.

    :param config_cls: The configuration class to fill.
    :param dict environ: Source of the configuration.  `os.environ` by default.

    :returns: An instance of *config_cls*.

    This is equivalent to calling ``config_cls.from_environ()``.
    """
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


def generate_help(config_cls, formatter=None, **kwargs):
    """
    Autogenerate a help string for a config class.

    :param formatter: A callable that will be called with the help dictionaries
       as an argument and the remaining *kwargs*.  It should return the help
       string.
    :param bool display_defaults: When using the default formatter, passing
       `True` for *display_defaults* makes the default values part of the
       output.

    :returns: A help string that can be printed to the user.

    This is equivalent to calling ``config_cls.generate_help()``.

    .. versionadded:: 19.1.0
    """
    if formatter is None:
        formatter = _format_help_dicts
    help_dicts = _generate_help_dicts(config_cls)

    return formatter(help_dicts, **kwargs)


# We need these aliases because of a name clash with a function argument.
__generate_help = generate_help
__to_config = to_config
