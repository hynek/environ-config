from __future__ import absolute_import, division, print_function

import attr
import pytest

import environ

from environ._environ_config import _SecretStr


class TestEnvironConfig(object):
    def test_empty(self):
        """
        Empty config is accepted.
        """
        @environ.config
        class Empty(object):
            pass

        cfg = environ.to_config(Empty)

        assert "Empty()" == repr(cfg)

    def test_flat(self):
        """
        Flat config is extracted.
        """
        @environ.config(prefix="APP")
        class Flat(object):
            x = environ.var()
            y = environ.var()

        cfg = environ.to_config(Flat, environ={
            "APP_X": "foo",
            "APP_Y": "bar",
        })

        assert Flat(x="foo", y="bar") == cfg

    def test_nested(self):
        """
        Nested config is extracted, prefix and vault_prefix are propagated.
        """
        @environ.config(prefix="XYZ", vault_prefix="ABC")
        class Nested(object):
            @environ.config
            class Sub(object):
                y = environ.var()
                z = environ.vault_var()

            x = environ.var()
            sub = environ.group(Sub)

        cfg = environ.to_config(Nested, environ={
            "APP_X": "nope",
            "XYZ_X": "foo",
            "XYZ_SUB_Y": "bar",
            "SECRET_ABC_SUB_Z": "qux",
        })

        assert Nested(x="foo", sub=Nested.Sub(y="bar", z="qux")) == cfg

    def test_missing(self):
        """
        If a var is missing, a human-readable MissingEnvValueError is raised.
        """
        @environ.config
        class Mandatory(object):
            x = environ.var()

        with pytest.raises(environ.MissingEnvValueError) as e:
            environ.to_config(Mandatory, environ={})

        assert ("APP_X",) == e.value.args

    def test_default(self):
        """
        Default values are used iff the vars are missing.
        """
        @environ.config
        class Defaults(object):
            x = environ.var("foo")
            y = environ.var("qux")

        cfg = environ.to_config(Defaults, environ={
            "APP_Y": "bar",
        })

        assert Defaults(x="foo", y="bar") == cfg

    def test_vault_env_template(self):
        """
        {env} in vault_prefix gets recursively replaced by an actual
        uppercased ENV.
        """
        @environ.config(vault_prefix="XYZ_{env}_ABC")
        class WithEnv(object):
            env = environ.var()
            password = environ.vault_var()

        cfg = environ.to_config(WithEnv, environ={
            "APP_ENV": "foo",
            "SECRET_XYZ_FOO_ABC_PASSWORD": "bar",
        })

        assert "bar" == cfg.password

    def test_secret_str_no_repr(self):
        """
        Outside of reprs, _SecretStr behaves normally.
        """
        s = _SecretStr("abc")

        assert "'abc'" == repr(s)

    def test_secret_str_censors(self):
        """
        _SecretStr censors it's __repr__ if its called from another __repr__.
        """
        s = _SecretStr("abc")

        @attr.s
        class C(object):
            s = attr.ib()

        assert "C(s=<SECRET>)" == repr(C(s))

    @pytest.mark.parametrize("prefix", [None, ""])
    def test_no_prefix(self, prefix):
        """
        If prefix is None or "", don't add a leading _ when adding namespaces.
        """
        @environ.config(prefix=prefix, vault_prefix=prefix)
        class C(object):
            x = environ.var()
            s = environ.vault_var()

        cfg = environ.to_config(C, environ={
            "X": "foo",
            "SECRET_S": "bar",
        })

        assert C("foo", "bar") == cfg
