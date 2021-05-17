# Copyright 2021 Chris Rose

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid

import attr
import boto3
import pytest

from moto import mock_secretsmanager

import environ

from environ.exceptions import MissingSecretError
from environ.secrets import SecretsManagerSecrets, _SecretStr


@pytest.fixture(name="shut_boto_up", autouse=True, scope="session")
def _shut_boto_up():
    import logging

    for name in logging.Logger.manager.loggerDict.keys():
        if ("boto" in name) or ("urllib3" in name):
            logging.getLogger(name).setLevel(logging.WARNING)


@pytest.fixture(name="secretsmanager", autouse=True)
def _secretsmanager():
    with mock_secretsmanager():
        yield boto3.client("secretsmanager", region_name="us-east-2")


@pytest.fixture(name="secret")
def _secret():
    return str(uuid.uuid4())


@pytest.fixture(name="sm")
def _sm(secretsmanager, secret):
    secretsmanager.create_secret(Name=secret)
    secretsmanager.put_secret_value(SecretId=secret, SecretString="foobar")
    return SecretsManagerSecrets(client=secretsmanager)


class TestAWSSMSecret(object):
    def test_missing_default_raises(self, sm):
        """
        Missing values without a default raise an MissingSecretError.
        """

        @environ.config
        class Cfg(object):
            pw = sm.secret()

        with pytest.raises(MissingSecretError):
            environ.to_config(Cfg, {})

    def test_default(self, sm, secret):
        """
        Defaults are used iff the key is missing.
        """

        @environ.config
        class Cfg(object):
            password = sm.secret(default="not used")
            secret = sm.secret(default="used!")

        cfg = environ.to_config(Cfg, {"APP_PASSWORD": secret})

        assert Cfg("foobar", "used!") == cfg

    def test_default_factory(self, sm, secret):
        """
        Defaults are used iff the key is missing.
        """

        def getpass():
            return "a default"

        @environ.config
        class Cfg(object):
            password = sm.secret(default=attr.Factory(getpass))
            secret = sm.secret(default=attr.Factory(getpass))

        cfg = environ.to_config(Cfg, {"APP_PASSWORD": secret})

        assert Cfg("foobar", "a default") == cfg

    def test_name_overwrite(self, sm, secret):
        """
        Passsing a specific key name is respected.
        """
        sm.client.put_secret_value(SecretId=secret, SecretString="foobar")

        @environ.config
        class Cfg(object):
            pw = sm.secret(name="password")

        cfg = environ.to_config(Cfg, {"password": secret})

        assert _SecretStr("foobar") == cfg.pw

    def test_nested(self, sm, secret):
        """
        Prefix building works.
        """
        sm.client.put_secret_value(SecretId=secret, SecretString="nested!")

        @environ.config
        class Cfg(object):
            @environ.config
            class DB(object):
                password = sm.secret()

            db = environ.group(DB)

        cfg = environ.to_config(Cfg, {"APP_DB_PASSWORD": secret})

        assert _SecretStr("nested!") == cfg.db.password
