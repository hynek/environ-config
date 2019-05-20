from __future__ import absolute_import, division, print_function

import environ


@environ.config(prefix="APP")
class AppConfig(object):
    host = environ.var("127.0.0.1")
    port = environ.var(5000, converter=int)


def test_default():
    """Class based `from_environ` without `environ` argument.
    """
    cfg = AppConfig.from_environ()
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 5000


def test_env():
    """Class based `from_environ`  with explicit `environ` argument.
    """
    env = {"APP_HOST": "0.0.0.0"}
    cfg = AppConfig.from_environ(environ=env)
    assert cfg.host == "0.0.0.0"
    assert cfg.port == 5000
