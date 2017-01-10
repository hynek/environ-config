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
  >>> @environ.config(prefix="APP", vault_prefix="APP_{env}")
  ... class AppConfig:
  ...    @environ.config
  ...    class DB:
  ...        name = environ.var("default_db")
  ...        host = environ.var("default.host")
  ...        port = environ.var(5432, convert=int)
  ...        user = environ.var("default_user")
  ...        password = environ.vault_var()
  ...
  ...    env = environ.var()
  ...    db = environ.group(DB)
  >>> cfg = environ.to_config(AppConfig, environ={
  ...     "APP_ENV": "dev",
  ...     "APP_DB_HOST": "localhost",
  ...     "SECRET_APP_DEV_DB_PASSWORD": "s3kr3t",  # Vault-via-envconsul-style var name.
  ... })  # Uses os.environ by default.
  >>> cfg
  AppConfig(env='dev', db=AppConfig.DB(name='default_db', host='localhost', port=5432, user='default_user', password=<SECRET>))
  >>> cfg.db.password
  's3kr3t'


Features
========

- Declarative & boilerplate-free.
- Nested config from flat env variable names..
- Default & mandatory values: enforce configuration structure without writing a line of code.
- Built on top of `attrs <http://www.attrs.org/>`_ which gives you data validation and conversion for free.
- Built-in `HashiCorp Vault <https://www.vaultproject.io>`_ support via `envconsul <https://github.com/hashicorp/envconsul>`_.


Project Information
===================

``environ_config`` is released under the `MIT <http://choosealicense.com/licenses/mit/>`_ license.
It targets Python 2.7, 3.4 and newer, and PyPy.
