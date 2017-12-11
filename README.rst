============================================================
environ_config: Configuration with env variables for Python.
============================================================

.. image:: https://travis-ci.org/hynek/environ_config.svg?branch=master
   :target: https://travis-ci.org/hynek/environ_config
   :alt: CI status

.. image:: https://codecov.io/gh/hynek/environ_config/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/hynek/environ_config
   :alt: Test Coverage

.. begin

``environ_config`` allows you to configure your applications using environment variables – as recommended in `The Twelve-Factor App <https://12factor.net/config>`_ methodology – with elegant, boilerplate-free, and declarative code:

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
  ...        port = environ.var(5432, convert=int)  # Use attrs's converters and validators!
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


Features
========

- Declarative & boilerplate-free.
- Nested config from flat env variable names.
- Default & mandatory values: enforce configuration structure without writing a line of code.
- Helpful debug logging that will tell you which variables are present and what ``environ_config`` is looking for.
- Built on top of `attrs <http://www.attrs.org/>`_ which gives you data validation and conversion for free.
- Plugable secrets extraction.
  Ships with:

  * `HashiCorp Vault <https://www.vaultproject.io>`_ support via `envconsul <https://github.com/hashicorp/envconsul>`_.
  * INI files, because secrets in env variables are `icky <https://diogomonica.com/2017/03/27/why-you-shouldnt-use-env-variables-for-secret-data/>`_.


Project Information
===================

``environ_config`` is released under the `MIT <https://choosealicense.com/licenses/mit/>`_ license.
It targets Python 2.7, 3.5 and newer, and PyPy.
