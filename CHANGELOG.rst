Changelog
=========

Versions follow `CalVer <http://calver.org>`_ with *no* backward-compatibility guarantees whatsoever.


20.1.0 (2020-03-23)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- Configurations can be immutable now.
  `#12 <https://github.com/hynek/environ-config/issues/12>`_


----


19.1.0 (2019-09-02)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Changed license from MIT to Apache License 2.


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- Added ``AppConfig.from_environ()`` to instantiate the configuration class.
  This is an alternative to ``environ.from_environ(AppConfig)``.
  `#5 <https://github.com/hynek/environ-config/issues/5>`_
- Added ``environ.generate_help(AppConfig)`` and ``AppConfig.generate_help()`` to create a help string based on the configuration.
- Allow passing customization of the ``"from_environ"`` and ``"generate_help"`` class methods.
  `#7 <https://github.com/hynek/environ-config/issues/7>`_
- If ``environ.var`` is passed an ``attr.Factory``, the callable is used to generate the default value.
  `#10 <https://github.com/hynek/environ-config/issues/10>`_


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
