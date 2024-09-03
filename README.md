# *environ-config*: Application Configuration With Env Variables

[![Documentation](https://img.shields.io/badge/Docs-Read%20The%20Docs-black)](https://environ-config.readthedocs.io/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-C06524)](https://github.com/hynek/environ-config/blob/main/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/environ-config)](https://pypi.org/project/environ-config/)
[![Downloads / Month](https://static.pepy.tech/personalized-badge/environ-config?period=month&units=international_system&left_color=grey&right_color=blue&left_text=Downloads%20/%20Month)](https://pepy.tech/project/environ-config)

<!-- teaser-begin -->

*environ-config* allows you to load your application's configuration from environment variables – as recommended in [*The Twelve-Factor App*](https://12factor.net/config) methodology – with elegant, boilerplate-free, and declarative code:

```pycon
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

```

`AppConfig.from_environ({...})` is equivalent to the code above, depending on your taste.


## Features

- Declarative & boilerplate-free.

- Nested configuration from flat environment variable names.

- Default & mandatory values: enforce configuration structure without writing a line of code.

- Built on top of [*attrs*](https://www.attrs.org/) which gives you data validation and conversion for free.

- Pluggable secrets extraction.
  Ships with:

  - [HashiCorp Vault](https://www.vaultproject.io) support via [*envconsul*](https://github.com/hashicorp/envconsul).
  - [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) (needs [*boto3*](https://pypi.org/project/boto3/))
  - INI files, because secrets in env variables are [icky](https://blog.diogomonica.com//2017/03/27/why-you-shouldnt-use-env-variables-for-secret-data/).

- Helpful debug logging that will tell you which variables are present and what *environ-config* is looking for.

- Built-in dynamic help documentation generation.

<!-- teaser-end -->

You can find the full documentation including a step-by-step tutorial on [Read the Docs](https://environ-config.readthedocs.io/).


## Project Information

*environ-config* is maintained by [Hynek Schlawack](https://hynek.me/) and is released under the [Apache License 2.0](https://github.com/hynek/environ-config/blob/main/LICENSE) license.
Development takes place on [GitHub](https://github.com/hynek/environ-config).

The development is kindly supported by [Variomedia AG](https://www.variomedia.de/) and all my amazing [GitHub Sponsors](https://github.com/sponsors/hynek).

*environ-config* wouldn't be possible without the [*attrs* project](https://www.attrs.org).


## *environ-config* for Enterprise

Available as part of the [Tidelift Subscription](https://tidelift.com/?utm_source=lifter&utm_medium=referral&utm_campaign=hynek).

The maintainers of *environ-config* and thousands of other packages are working with Tidelift to deliver commercial support and maintenance for the open source packages you use to build your applications.
Save time, reduce risk, and improve code health, while paying the maintainers of the exact packages you use.
