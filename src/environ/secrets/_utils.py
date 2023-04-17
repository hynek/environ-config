import codecs

import attr

from environ._environ_config import Raise
from environ.exceptions import MissingSecretError


def _get_default_secret(var, default):
    """
    Get default or raise MissingSecretError.
    """
    if isinstance(default, attr.Factory):
        return attr.NOTHING

    if isinstance(default, Raise):
        raise MissingSecretError(var)

    return default


def _open_file(path):
    return codecs.open(path, mode="r", encoding="utf-8")
