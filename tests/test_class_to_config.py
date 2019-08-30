from __future__ import absolute_import, division, print_function

import attr

import environ


@environ.config(prefix="APP")
class AppConfig(object):
    host = environ.var("127.0.0.1")
    port = environ.var(5000, converter=int)


@environ.config(prefix="APP", from_environ="from_env")
class ConfigRenamed(object):
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")


@environ.config(prefix="APP", from_environ="")
class ConfigEmptyName(object):
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")


@environ.config(prefix="APP", from_environ=None)
class ConfigNoneName(object):
    host = environ.var("127.0.0.1", help="host help")
    port = environ.var(5000, converter=int, help="port help")


def test_has_classmethod():
    """
    Class based `from_environ` classmethod exists
    """
    assert hasattr(AppConfig, "from_environ")
    assert hasattr(ConfigRenamed, "from_env")
    assert not hasattr(ConfigEmptyName, "from_environ")
    assert not hasattr(ConfigNoneName, "from_environ")


def test_default():
    """
    Class based `from_environ` without `environ` argument.
    """
    cfg = AppConfig.from_environ()

    assert cfg.host == "127.0.0.1"
    assert cfg.port == 5000

    assert environ.to_config(AppConfig) == AppConfig.from_environ()
    assert environ.to_config(ConfigRenamed) == ConfigRenamed.from_env()


def test_env():
    """
    Class based `from_environ`  with explicit `environ` argument.
    """
    env = {"APP_HOST": "0.0.0.0"}
    cfg = AppConfig.from_environ(environ=env)

    assert cfg.host == "0.0.0.0"
    assert cfg.port == 5000

    assert environ.to_config(AppConfig, environ=env) == AppConfig.from_environ(
        environ=env
    )

    assert environ.to_config(
        ConfigRenamed, environ=env
    ) == ConfigRenamed.from_env(environ=env)


def test_factory_default():
    """
    Class based ``from_environ`` allows ``attr.Factory`` defaults.
    """

    @environ.config()
    class FactoryConfig(object):
        x = environ.var(attr.Factory(list))
        y = environ.var("bar")

    cfg = FactoryConfig.from_environ({"APP_Y": "baz"})

    assert cfg.x == []
    assert cfg.y == "baz"
