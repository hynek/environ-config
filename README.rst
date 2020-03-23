==============================================================
*environ-config*: Application Configuration With Env Variables
==============================================================

.. image:: https://readthedocs.org/projects/environ-config/badge/?version=stable
   :target: https://environ-config.readthedocs.io/
   :alt: Documentation Status

.. image:: https://github.com/hynek/environ-config/workflows/CI/badge.svg?branch=master
   :target: https://github.com/hynek/environ-config/actions?workflow=CI
   :alt: CI Status

.. image:: https://codecov.io/gh/hynek/environ-config/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/hynek/environ-config
   :alt: Test Coverage

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Code style: black

.. -teaser-begin-

*environ-config* allows you to configure your applications using environment variables – as recommended in `The Twelve-Factor App <https://12factor.net/config>`_ methodology – with elegant, boilerplate-free, and declarative code:

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


Features
========

- Declarative & boilerplate-free.
- Nested configuration from flat environment variable names.
- Default & mandatory values: enforce configuration structure without writing a line of code.
- Helpful debug logging that will tell you which variables are present and what *environ-config* is looking for.
- Built on top of `attrs <https://www.attrs.org/>`_ which gives you data validation and conversion for free.
- Pluggable secrets extraction.
  Ships with:

  * `HashiCorp Vault <https://www.vaultproject.io>`_ support via `envconsul <https://github.com/hashicorp/envconsul>`_.
  * INI files, because secrets in env variables are icky.
- Pass any dictionary into ``environ.to_config(AppConfig, {"your": "config"})`` instead of loading from the environment.
- Built in dynamic help documentation generation via ``environ.generate_help``.

.. -teaser-end-

You can find the full documentation including a step-by-step tutorial on `Read the Docs <https://environ-config.readthedocs.io/>`_.


Project Information
===================

``environ-config`` is released under the `Apache License 2.0 <https://choosealicense.com/licenses/apache-2.0/>`_ license.
It targets Python 2.7, 3.5 and newer, and PyPy.
Development takes place on `GitHub <https://github.com/hynek/environ-config>`_.
