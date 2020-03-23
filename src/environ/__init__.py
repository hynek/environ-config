# Copyright 2017 Hynek Schlawack

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from . import secrets
from ._environ_config import (
    bool_var,
    config,
    generate_help,
    group,
    to_config,
    var,
)
from .exceptions import MissingEnvValueError


__version__ = "20.1.0"

__title__ = "environ_config"
__description__ = "Boilerplate-free configuration with env variables."
__uri__ = "https://github.com/hynek/environ_config"

__author__ = "Hynek Schlawack"
__email__ = "hs@ox.cx"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2017 " + __author__


__all__ = [
    "MissingEnvValueError",
    "bool_var",
    "config",
    "generate_help",
    "group",
    "secrets",
    "to_config",
    "var",
]
