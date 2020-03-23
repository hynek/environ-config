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

import attr
import pytest

from attr.exceptions import FrozenInstanceError

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


@environ.config(prefix="FOO")
class Parent(object):
    not_a_var = attr.ib()  # For testing that only environ.var's are processed.
    var1 = environ.var(help="var1, no default")
    var2 = environ.var("bar", help="var2, has default")
    var3 = environ.bool_var(help="var3, bool_var, no default")
    var4 = environ.bool_var(True, help="var4, bool_var, has default")
    var5 = environ.var("canine", name="DOG", help="var5, named, has default")
    var6 = environ.var(name="CAT", help="var6, named, no default")

    @environ.config
    class Child(object):
        var7 = environ.var(help="var7, no default")
        var8 = environ.var("bar", help="var8, has default")
        var9 = environ.bool_var(help="var9, bool_var, no default")
        var10 = environ.bool_var(True, help="var10, bool_var, has default")
        var11 = environ.var(
            "canine", name="DOG2", help="var11, named, has default"
        )
        var12 = environ.var(name="CAT2", help="var12, named, no default")
        var13 = environ.var("default")  # var with default, no help
        var14 = environ.var()  # var without default, no help

    child = environ.group(Child)


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

        cfg = environ.to_config(Flat, environ={"APP_X": "foo", "APP_Y": "bar"})

        assert Flat(x="foo", y="bar") == cfg

    def test_nested(self):
        """
        Nested config is extracted, prefix and vault_prefix are propagated.
        """
        env = {"APP_X": "nope", "XYZ_X": "foo", "XYZ_SUB_Y": "bar"}
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

        cfg = environ.to_config(Defaults, environ={"APP_Y": "bar"})

        assert Defaults(x="foo", y="bar") == cfg

    def test_factory_default(self):
        """
        If the default value is an ``attr.Factory``,
        it used to generate the default value.
        """

        @environ.config
        class Defaults(object):
            x = environ.var(attr.Factory(list))
            y = environ.var(attr.Factory(list))

        cfg = environ.to_config(Defaults, environ={"APP_Y": "bar"})

        assert Defaults(x=[], y="bar") == cfg

    @pytest.mark.parametrize("prefix", [None, ""])
    def test_no_prefix(self, prefix):
        """
        If prefix is None or "", don't add a leading _ when adding namespaces.
        """

        @environ.config(prefix=prefix)
        class Cfg(object):
            x = environ.var()

        cfg = environ.to_config(Cfg, environ={"X": "foo"})

        assert Cfg("foo") == cfg

    def test_overwrite(self):
        """
        The env variable name can be overwritten.
        """

        @environ.config
        class Cfg(object):
            x = environ.var(name="LANG")
            y = environ.var()

        cfg = environ.to_config(
            Cfg, environ={"APP_X": "nope", "LANG": "foo", "APP_Y": "bar"}
        )

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

        cfg = environ.to_config(
            Cfg, environ={"X": "x", "Y": "y", "SUB_Y": "sub_y"}
        )

        assert Cfg("x", "y", Cfg.Sub("sub_y")) == cfg

    @pytest.mark.parametrize("val", ["1", "trUe", "yEs  "])
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

        cfg = environ.to_config(Cfg, environ={"APP_T": val, "APP_F": "nope"})

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

        cfg = environ.to_config(Cfg, environ={"APP_E": "e"})

        assert Cfg("e", 42) == cfg

    def test_generate_help_str(self):
        """
        A help string is generated for a config class.

        Presence of defaults are indicated but they are not shown.
        """
        help_str = environ.generate_help(Parent)
        assert (
            help_str
            == """FOO_VAR1 (Required): var1, no default
FOO_VAR2 (Optional): var2, has default
FOO_VAR3 (Required): var3, bool_var, no default
FOO_VAR4 (Optional): var4, bool_var, has default
DOG (Optional): var5, named, has default
CAT (Required): var6, named, no default
FOO_CHILD_VAR7 (Required): var7, no default
FOO_CHILD_VAR8 (Optional): var8, has default
FOO_CHILD_VAR9 (Required): var9, bool_var, no default
FOO_CHILD_VAR10 (Optional): var10, bool_var, has default
DOG2 (Optional): var11, named, has default
CAT2 (Required): var12, named, no default
FOO_CHILD_VAR13 (Optional)
FOO_CHILD_VAR14 (Required)"""
        )

    def test_generate_help_str_with_defaults(self):
        """
        A help string is generated for a config class.

        display_defaults=True makes the defaults be shown.
        """
        help_str = environ.generate_help(Parent, display_defaults=True)

        assert (
            help_str
            == """FOO_VAR1 (Required): var1, no default
FOO_VAR2 (Optional, Default=bar): var2, has default
FOO_VAR3 (Required): var3, bool_var, no default
FOO_VAR4 (Optional, Default=True): var4, bool_var, has default
DOG (Optional, Default=canine): var5, named, has default
CAT (Required): var6, named, no default
FOO_CHILD_VAR7 (Required): var7, no default
FOO_CHILD_VAR8 (Optional, Default=bar): var8, has default
FOO_CHILD_VAR9 (Required): var9, bool_var, no default
FOO_CHILD_VAR10 (Optional, Default=True): var10, bool_var, has default
DOG2 (Optional, Default=canine): var11, named, has default
CAT2 (Required): var12, named, no default
FOO_CHILD_VAR13 (Optional, Default=default)
FOO_CHILD_VAR14 (Required)"""
        )

    def test_custom_formatter(self):
        """
        Custom formatters can be passed and are used.
        """

        def bad_formatter(help_dicts):
            return "Not a good formatter"

        help_str = environ.generate_help(Parent, formatter=bad_formatter)

        assert help_str == "Not a good formatter"

    def test_frozen(self):
        """
        Frozen configurations are immutable.
        """

        @environ.config(frozen=True)
        class Cfg(object):
            x = environ.var()
            y = environ.var()

        cfg = environ.to_config(Cfg, {"APP_X": "foo", "APP_Y": "bar"})

        with pytest.raises(FrozenInstanceError):
            cfg.x = "next_foo"

        assert cfg.x == "foo"

    def test_frozen_child(self):
        """
        Frozen child groups are immutable.
        """

        @environ.config
        class Cfg(object):
            @environ.config(frozen=True)
            class Sub(object):
                z = environ.var()

            x = environ.var()
            y = environ.var()
            sub = environ.group(Sub)

        cfg = environ.to_config(
            Cfg, {"APP_X": "foo", "APP_Y": "bar", "APP_SUB_Z": "baz"}
        )

        cfg.x = "next_foo"

        assert cfg.x == "next_foo"

        with pytest.raises(FrozenInstanceError):
            cfg.sub.z = "next_baz"

        assert cfg.sub.z == "baz"
