# API Reference

```{eval-rst}
.. automodule:: environ

.. autofunction:: config

.. autofunction:: var

.. autofunction:: bool_var

.. autofunction:: group

.. autofunction:: to_config(config_cls, environ=os.environ)

.. autofunction:: generate_help
```


## Secrets

```{eval-rst}
.. automodule:: environ.secrets

.. autoclass:: INISecrets
   :members: from_path, from_path_in_env, secret

.. autoclass:: VaultEnvSecrets
   :members: secret

   .. warning::

      Please note that `it's a bad idea to store secrets in environment variables <https://blog.diogomonica.com/2017/03/27/why-you-shouldnt-use-env-variables-for-secret-data/>`_.

.. autoclass:: DirectorySecrets
   :members: from_path, from_path_in_env, secret

.. autoclass:: SecretsManagerSecrets
   :members: secret
```


## Exceptions

```{eval-rst}
.. automodule:: environ.exceptions

.. autoexception:: MissingEnvValueError

.. autoexception:: MissingSecretError
```
