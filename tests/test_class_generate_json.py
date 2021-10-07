import json

import environ


@environ.config(prefix="APP")
class AppConfig:
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")
    user = environ.var(help="user help")


@environ.config(prefix="APP", generate_json="gen_json")
class ConfigRenamed:
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")
    user = environ.var(help="user help")


@environ.config(prefix="APP", generate_json="")
class ConfigEmptyName:
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")
    user = environ.var(help="user help")


@environ.config(prefix="APP", generate_json=None)
class ConfigNoneName:
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")
    user = environ.var(help="user help")


def test_has_classmethod_for_json():
    """
    Class based `generate_json` classmethod exists
    """
    sentinel = object()
    # getattr returning default sentinel value means the att is missing
    # some attributes are expected
    assert getattr(AppConfig, "generate_json", sentinel) is not sentinel
    assert getattr(ConfigRenamed, "gen_json", sentinel) is not sentinel
    # another attributes shall be missing
    assert getattr(ConfigEmptyName, "generate_json", sentinel) is sentinel
    assert getattr(ConfigNoneName, "generate_json", sentinel) is sentinel


def test_generated_jsons_equals():
    """
    Text by classmethod and environ.generate_json is the same.
    """
    assert environ.generate_json(AppConfig) == AppConfig.generate_json()
    assert environ.generate_json(ConfigRenamed) == ConfigRenamed.gen_json()


def test_generated_jsons_equals_expected_value():
    """
    Text by classmethod and environ.generate_json equals with display_defaults
    """
    expected_app_config_json = json.dumps(
        {
            "APP_HOST": "(Optional): host help",
            "APP_PORT": "(Optional): port help",
            "APP_USER": "(Required): user help",
        },
        indent=4,
    )
    assert (
        environ.generate_json(
            AppConfig,
        )
        == AppConfig.generate_json()
    )
    assert expected_app_config_json == AppConfig.generate_json()
    assert (
        environ.generate_json(
            ConfigRenamed,
        )
        == ConfigRenamed.gen_json()
    )
    assert expected_app_config_json == ConfigRenamed.gen_json()
