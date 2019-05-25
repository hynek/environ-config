from __future__ import absolute_import, division, print_function

import pytest

import environ


@environ.config(prefix="APP")
class AppConfig(object):
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")


@environ.config(prefix="APP", generate_help="gen_help")
class ConfigRenamed(object):
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")


@environ.config(prefix="APP", generate_help="")
class ConfigEmptyName(object):
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")


@environ.config(prefix="APP", generate_help=None)
class ConfigNoneName(object):
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")


def test_has_classmethod():
    """
    Class based `generate_help` classmethod exists
    """
    assert hasattr(AppConfig, "generate_help")
    assert hasattr(ConfigRenamed, "gen_help")
    assert not hasattr(ConfigEmptyName, "generate_help")
    assert not hasattr(ConfigNoneName, "generate_help")


def test_generated_helps_equals():
    """
    Text by classmethod and environ.generate_help equals
    """
    assert environ.generate_help(AppConfig) == AppConfig.generate_help()
    assert environ.generate_help(ConfigRenamed) == ConfigRenamed.gen_help()


@pytest.mark.parametrize("display_defaults", [True, False])
def test_generated_helps_equals_display_defaults(display_defaults):
    """
    Text by classmethod and environ.generate_help equals with display_defaults
    """
    assert environ.generate_help(
        AppConfig, display_defaults=display_defaults
    ) == AppConfig.generate_help(display_defaults=display_defaults)
    assert environ.generate_help(
        ConfigRenamed, display_defaults=display_defaults
    ) == ConfigRenamed.gen_help(display_defaults=display_defaults)
