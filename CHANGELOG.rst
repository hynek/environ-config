Changelog
=========

Versions follow `CalVer <http://calver.org>`_ with *no* backward-compatibility guarantees whatsoever.


19.1.0 (UNRELEASED)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Changed license from MIT to Apache License 2.


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- Added ``environ.generate_help(AppConfig)`` and ``AppConfig.generate_help()`` (two alternatives) to create a help string based on the configuration.
- Added ``AppConfig.from_environ()`` to instantiate the config class. This is alternative to ``environ.config()``.
- ``environ.config(from_environ="fr_env", generate_help="gen_hlp")`` allows passing alternative names for class methods "from_environ" and ``"generate_help"``, or prevent their creation by pasing ``None``.
- If ``environ.var`` is passed an ``attr.Factory``, the callable is used to generate the default value.



----



18.2.0 (2018-01-12)
-------------------

Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Use ``RawConfigParser`` for ini-style secrets to avoid interpolation errors.


Changes:
^^^^^^^^

*none*


----

18.1.0 (2018-01-04)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``convert`` → ``converter``


Changes:
^^^^^^^^

- Fix for ``attrs`` 17.4.0.


----


17.1.0 (2017-12-14)
-------------------

Initial release.
