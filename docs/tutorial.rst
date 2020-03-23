Tutorial
========


Getting Started
---------------

To get started, install *environ-config* using *pip* from PyPI into your project's virtual environment:

.. code:: shell

   $ python -m pip install environ-config


Let's start with a very simple configuration and pick up advanced features iteratively:

.. doctest::

   >>> import environ
   >>> @environ.config
   ... class AppConfig:
   ...     value = environ.var(help="This is a value.")
   ...     flag = environ.bool_var(help="This is a boolean flag.")

Now you can try loading this configuration either using the function `environ.to_config` (mnemonic: "environment to configuration") or using the class method ``AppConfig.from_environ()`` that has been automatically attached to the ``AppConfig`` class.
Both methods are equivalent and we will use them in this tutorial interchangeably.

To do that, *environ-config* will concatenate a common prefix (``APP`` by default, but can be changed) and the attribute names with underscores as separators.
Then it tries to load those values from the process environment (`os.environ`) -- or a dictionary that you can pass to `environ.to_config`/``AppConfig.from_environ()`` instead.
This is what we will do in this tutorial to make things more transparent.

.. note::

   The class and the configuration attributes can have *any* valid Python name.
   The fact that all our configurations are called ``AppConfig`` is just *our* naming convention.

   If you want to use an invalid name for the environment variable, you can overwrite the attribute name using the *name* argument to `environ.to_config`.

So in this case, *environ-config* will look for two environment variables: ``APP_VALUE`` and ``APP_FLAG``.
Let's pass a dictionary to it that contains them:

.. doctest::

   >>> AppConfig.from_environ(environ={
   ...     "APP_VALUE": "42",
   ...     "APP_FLAG": "yes",
   ... })
   AppConfig(value='42', flag=True)

As you can see, since we used `environ.bool_var`, the ``"yes"`` string has been converted to a `bool`.


Defaults
--------

Now let's assume you want to keep ``AppConfig.value`` on 42, but have an option to overwrite it when needed.
Assign a default value for it and that will be used if the variable in question is not present:

.. doctest::

   >>> @environ.config
   ... class AppConfig:
   ...     value = environ.var(default="42")
   ...     flag = environ.bool_var()
   >>> environ.to_config(AppConfig, environ={
   ...     "APP_FLAG": "yes",
   ... })
   AppConfig(value='42', flag=True)

But you can still overwrite it if needed:

.. doctest::

   >>> environ.to_config(AppConfig, environ={
   ...     "APP_VALUE": "23",
   ...     "APP_FLAG": "yes",
   ... })
   AppConfig(value='23', flag=True)


.. warning::

   As a general advice: don't set your defaults to dangerous values.
   For example if your web application has some kind of development mode that activates a debugger view on exceptions, that should be strictly opt-in.

   Otherwise one forgotten or mistyped option name can fully expose your application.


Nesting
-------

Sometimes it makes sense to give your configuration more structure than a flat class.
For that *environ-config* comes with the concept of groups; implemented using `environ.group`:

.. doctest::

   >>> @environ.config
   ... class AppConfig:
   ...     @environ.config
   ...     class SomeService:
   ...         host = environ.var()
   ...         port = environ.var()
   ...     svc = environ.group(SomeService)
   >>> AppConfig.from_environ(environ={
   ...     "APP_SVC_HOST": "localhost",
   ...     "APP_SVC_PORT": "5555",
   ... })
   AppConfig(svc=AppConfig.SomeService(host='localhost', port='5555'))

.. note::

   It's usually better to store access information to servers in URLs in use cases like this.
   Python has great libraries for creating and parsing them (e.g. `yarl <https://yarl.readthedocs.io/>`_) and they allow you to keep all information needed to connect to a service serialized into a single string.

   Some libraries like `SQLAlchemy <https://www.sqlalchemy.org>`_ or the `Redis <https://redis-py.readthedocs.io/>`_ package allow you to pass URL strings directly into them.


Converters
----------

*environ-config* also inherited ``attrs``'s converters.
They are especially useful with integers or `enum` s:

.. doctest::

   >>> import enum
   >>> class Env(enum.Enum):
   ...     PROD = "prod"
   ...     DEV = "DEV"
   ...     STAGING = "staging"
   >>> @environ.config
   ... class AppConfig:
   ...     port = environ.var(converter=int)
   ...     env = environ.var(converter=Env)
   >>> environ.to_config(AppConfig, environ={
   ...     "APP_PORT": "8080",
   ...     "APP_ENV": "prod",
   ... })
   AppConfig(port=8080, env=<Env.PROD: 'prod'>)

As an added benefit, they also validate the values for you.


Validation
----------

You can take validation much further thanks to ``attrs``'s validation system:


.. doctest::

   >>> from pathlib import Path
   >>> @environ.config
   ... class AppConfig:
   ...     path = environ.var(converter=Path)
   ...     @path.validator
   ...     def _ensure_path_exists(self, var, path):
   ...         if not path.exists():
   ...             raise ValueError("Path not found.")
   >>> AppConfig.from_environ(environ={"APP_PATH": "pyproject.toml"})
   AppConfig(path=PosixPath('pyproject.toml'))
   >>> AppConfig.from_environ(environ={"APP_PATH": "foo"})
   Traceback (most recent call last):
      ...
   ValueError: Path not found.

Check out ``attrs``'s `documentation <https://www.attrs.org/en/stable/init.html#validators>`_ for more details.


Secrets
-------

Secrets should be stored in specialized systems and `not passed as environment variables <https://diogomonica.com/2017/03/27/why-you-shouldnt-use-env-variables-for-secret-data/>`_ .
The 12 Factor App manifesto is plain wrong here.

Therefore *environ-config* comes with support for getting secrets from somewhere else.
The simplest way is to safe them into an INI file and tell *environ-config* to load that file on startup, based on an environment variable.

For example this is a common pattern::

   ini_file = environ.secrets.INISecrets.from_path_in_env(
       "APP_SECRETS_INI", "/secrets/secrets.ini"
   )

   @environ.config
   class AppConfig:
       db_url = ini_file.secret()

It looks at the environment variable ``APP_SECRETS_INI`` and loads the file that is specified there.
If the variable is not set, it falls back to reading the secrets from ``/secrets/secrets.ini``.

This allows you in development to set the environment variable ``APP_SECRETS_INI`` to something like ``dev-secrets.ini`` and put the secret in there:

.. code:: ini

   [secrets]
   db_url=postgresql://user@localhost/database-name

And in production it will just work without any further work.


Debugging
---------

*environ-config* comes with two tools to help you to debug your configuration.
Firstly, you can tell it to generate a help string using `environ.generate_help`/``AppConfig.generate_help()``:


.. doctest::

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

The other option is to activate debug-level logging for the ``environ_config`` logger by setting its level to ``logging.WARNING``.
*environ-config* will tell you what its looking for in real time.
