Changelog
=========

Versions follow `CalVer <http://calver.org>`_ with *no* backward-compatibility guarantees whatsoever.


18.2.0 (2018-01-12)
-------------------

Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Use ``RawConfigParser`` for ini-style secrets to avoid interpolation errors.


Changes:
^^^^^^^^

- Added ``environ.generate_help`` to the public interface. It is implemented by...
  * ``environ._environ_config.generate_help``
  * ``environ._environ_config._generate_help_dicts``
  * ``environ._environ_config._format_help_dicts``


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
