from __future__ import absolute_import, division, print_function

import attr
import pytest

import environ


@environ.config(prefix="XYZ")
class Nested(object):
    """
    A nested configuration example.
    """
    @environ.config
    class Sub(object):
        y = environ.var()

    x = environ.var()
    sub = environ.group(Sub)


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
        env = {
            "APP_X": "nope",
            "XYZ_X": "foo",
            "XYZ_SUB_Y": "bar",
        }
        cfg = environ.to_config(Nested, environ=env)

        assert Nested(x="foo", sub=Nested.Sub(y="bar")) == cfg

    def test_missing(self):
        """
        If a var is missing, a human-readable MissingEnvValueError is raised.
        """
        @environ.config
        class Mandatory(object):
            x = environ.var()

        with pytest.raises(environ.MissingEnvValueError) as e:
            environ.to_config(Mandatory, environ={"y": "boring"})

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

    @pytest.mark.parametrize("prefix", [None, ""])
    def test_no_prefix(self, prefix):
        """
        If prefix is None or "", don't add a leading _ when adding namespaces.
        """
        @environ.config(prefix=prefix)
        class Cfg(object):
            x = environ.var()

        cfg = environ.to_config(Cfg, environ={
            "X": "foo",
        })

        assert Cfg("foo") == cfg

    def test_overwrite(self):
        """
        The env variable name can be overwritten.
        """
        @environ.config
        class Cfg(object):
            x = environ.var(name="LANG")
            y = environ.var()

        cfg = environ.to_config(Cfg, environ={
            "APP_X": "nope",
            "LANG": "foo",
            "APP_Y": "bar",
        })

        assert Cfg("foo", "bar") == cfg

    def test_no_prefixes(self):
        """
        If no prefixes are wished, nothing is prepended.
        """
        @environ.config(prefix=None)
        class Cfg(object):
            @environ.config
            class Sub(object):
                y = environ.var()

            x = environ.var()
            y = environ.var()
            sub = environ.group(Sub)

        cfg = environ.to_config(Cfg, environ={
            "X": "x",
            "Y": "y",
            "SUB_Y": "sub_y",
        })

        assert Cfg("x", "y", Cfg.Sub("sub_y")) == cfg

    @pytest.mark.parametrize("val", [
        "1", "trUe", "yEs  "
    ])
    def test_bool_var(self, val):
        """
        Truthy strings are converted to True, everything else to False.

        Defaults can be passed as bools.
        """
        @environ.config
        class Cfg(object):
            t = environ.bool_var()
            f = environ.bool_var()
            d = environ.bool_var(True)

        cfg = environ.to_config(Cfg, environ={
            "APP_T": val,
            "APP_F": "nope",
        })

        assert cfg.t is True
        assert cfg.f is False
        assert cfg.d is True

    def test_tolerates_attribs(self):
        """
        Classes are allowed to have plain attr.ibs for e.g.
        __attrs_post_init__.
        """
        @environ.config
        class Cfg(object):
            e = environ.var()
            x = attr.ib(default=42)

        cfg = environ.to_config(Cfg, environ={
            "APP_E": "e",
        })

        assert Cfg("e", 42) == cfg
