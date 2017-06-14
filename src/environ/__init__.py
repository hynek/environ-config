from ._environ_config import config, var, group, to_config, bool_var
from .exceptions import MissingEnvValueError
from . import secrets


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
    "bool_var",
    "config",
    "group",
    "secrets",
    "to_config",
    "var",
]
