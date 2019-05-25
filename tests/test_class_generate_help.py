from __future__ import absolute_import, division, print_function

import pytest

import environ


@environ.config(prefix="APP")
class AppConfig(object):
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")


def test_has_classmethod():
    """
    Class based `generate_help` classmethod exists
    """
    assert hasattr(AppConfig, "generate_help")


def test_generated_helps_equals():
    """
    Text by classmethod and environ.generate_help equals
    """
    env_text = environ.generate_help(AppConfig)
    cls_text = AppConfig.generate_help()
    assert env_text == cls_text


@pytest.mark.parametrize("display_defaults", [True, False])
def test_generated_helps_equals_display_defaults(display_defaults):
    """
    Text by classmethod and environ.generate_help equals with display_defaults
    """
    env_text = environ.generate_help(AppConfig, display_defaults=display_defaults)
    cls_text = AppConfig.generate_help(display_defaults=display_defaults)
    assert env_text == cls_text
