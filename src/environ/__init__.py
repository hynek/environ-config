from ._environ_config import config, var, group, vault_var, to_config
from .exceptions import MissingEnvValueError


__version__ = "17.0.0.dev0"

__title__ = "environ_config"
__description__ = "Boilerplate-free configuration with env variables."
__uri__ = "https://github.com/hynek/environ_config"

__author__ = "Hynek Schlawack"
__email__ = "hs@ox.cx"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2017 {0}".format(__author__)


__all__ = [
    "MissingEnvValueError",
    "config",
    "to_config",
    "var",
    "vault_var",
    "group",
]
