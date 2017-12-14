from . import secrets
from ._environ_config import bool_var, config, group, to_config, var
from .exceptions import MissingEnvValueError


__version__ = "17.1.0"

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
