================================================================
``environ-config``: Configuration with env variables for Python.
================================================================

.. image:: https://travis-ci.org/hynek/environ-config.svg?branch=master
   :target: https://travis-ci.org/hynek/environ-config
   :alt: CI status

.. image:: https://codecov.io/gh/hynek/environ-config/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/hynek/environ-config
   :alt: Test Coverage

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Code style: black

.. begin

``environ-config`` allows you to configure your applications using environment variables – as recommended in `The Twelve-Factor App <https://12factor.net/config>`_ methodology – with elegant, boilerplate-free, and declarative code:

.. code-block:: pycon

  >>> import environ
  >>> # Extracts secrets from Vault-via-envconsul: 'secret/your-app':
  >>> vault = environ.secrets.VaultEnvSecrets(vault_prefix="SECRET_YOUR_APP")
  >>> @environ.config(prefix="APP")
  ... class AppConfig:
  ...    @environ.config
  ...    class DB:
  ...        name = environ.var("default_db")
  ...        host = environ.var("default.host")
  ...        port = environ.var(5432, converter=int)  # Use attrs's converters and validators!
  ...        user = environ.var("default_user")
  ...        password = vault.secret()
  ...
  ...    env = environ.var()
  ...    lang = environ.var(name="LANG")  # It's possible to overwrite the names of variables.
  ...    db = environ.group(DB)
  ...    awesome = environ.bool_var()
  >>> cfg = environ.to_config(
  ...     AppConfig,
  ...     environ={
  ...         "APP_ENV": "dev",
  ...         "APP_DB_HOST": "localhost",
  ...         "LANG": "C",
  ...         "APP_AWESOME": "yes",  # true and 1 work too, everything else is False
  ...         # Vault-via-envconsul-style var name:
  ...         "SECRET_YOUR_APP_DB_PASSWORD": "s3kr3t",
  ... })  # Uses os.environ by default.
  >>> cfg
  AppConfig(env='dev', lang='C', db=AppConfig.DB(name='default_db', host='localhost', port=5432, user='default_user', password=<SECRET>), awesome=True)
  >>> cfg.db.password
  's3kr3t'

``AppConfig.from_environ({...})`` is equivalent to the code above, depending on your taste.

``@environ.config(from_environ="different_name_for_from_environ", generatef_help="different_name_for_generate_help")`` allows to rename generated classmethods or to prevent it's creation by passing ``None`` instead of a name.


Features
========

- Declarative & boilerplate-free.
- Nested config from flat env variable names.
- Default & mandatory values: enforce configuration structure without writing a line of code.
- Helpful debug logging that will tell you which variables are present and what ``environ-config`` is looking for.
- Built on top of `attrs <https://www.attrs.org/>`_ which gives you data validation and conversion for free.
- Pluggable secrets extraction.
  Ships with:

  * `HashiCorp Vault <https://www.vaultproject.io>`_ support via `envconsul <https://github.com/hashicorp/envconsul>`_.
  * INI files, because secrets in env variables are `icky <https://diogomonica.com/2017/03/27/why-you-shouldnt-use-env-variables-for-secret-data/>`_.
- Pass any dict into ``environ.to_config(AppConfig, {"your": "config"})`` instead of loading from the environment.
- Built in dynamic help documentation generation via ``environ.generate_help``.

.. code-block:: pycon

  >>> import environ
  >>> @environ.config(prefix="APP")
  ... class AppConfig:
  ...     @environ.config
  ...     class SubConfig:
  ...         sit = environ.var(help="Another example message.")
  ...         amet = environ.var()
  ...     lorem = environ.var('ipsum')
  ...     dolor = environ.bool_var(True, help="An example message.")
  ...     subconfig = environ.group(SubConfig)
  ...
  >>> print(environ.generate_help(AppConfig))
  APP_LOREM (Optional)
  APP_DOLOR (Optional): An example message.
  APP_SUBCONFIG_SIT (Required): Another example message.
  APP_SUBCONFIG_AMET (Required)
  >>> print(environ.generate_help(AppConfig, display_defaults=True))
  APP_LOREM (Optional, Default=ipsum)
  APP_DOLOR (Optional, Default=True): An example message.
  APP_SUBCONFIG_SIT (Required): Another example message.
  APP_SUBCONFIG_AMET (Required)

``AppConfig.generate_help({...})`` is equivalent to the code above, depending on your taste.


Project Information
===================

``environ-config`` is released under the `Apache License 2.0 <https://choosealicense.com/licenses/apache-2.0/>`_ license.
It targets Python 2.7, 3.5 and newer, and PyPy.
