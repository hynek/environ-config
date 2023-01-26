import environ


ini_secrets: environ.secrets.INISecrets = (
    environ.secrets.INISecrets.from_path_in_env(
        "APP_SECRETS_INI", "/secrets/secrets.ini"
    )
)
ini2: environ.secrets.INISecrets = environ.secrets.INISecrets.from_path(
    "/secrets/secrets.ini", section="foo"
)
dir_secrets: environ.secrets.DirectorySecrets = (
    environ.secrets.DirectorySecrets.from_path_in_env("APP_SECRETS_PATH", ".")
)
dir2: environ.secrets.DirectorySecrets = (
    environ.secrets.DirectorySecrets.from_path(".")
)
vault_secrets: environ.secrets.VaultEnvSecrets = (
    environ.secrets.VaultEnvSecrets("XYZ")
)
aws_secrets: environ.secrets.SecretsManagerSecrets = (
    environ.secrets.SecretsManagerSecrets()
)


@environ.config
class Config:
    @environ.config
    class Sub:
        y: int = environ.var(converter=int)

    x: str = environ.var()
    b: bool = environ.bool_var(name="BOOL")
    sub: Sub = environ.group(Sub)
    secret: str = ini_secrets.secret()
    d_secret: str = dir_secrets.secret(help="help!")
    v_secret: str = vault_secrets.secret()
    a_secret: str = aws_secrets.secret()


h: str = environ.generate_help(Config)

cfg = environ.to_config(Config, {"APP_X": "123"})


def takes_cfg(c: Config) -> str:
    return c.x


def takes_sub(s: Config.Sub) -> int:
    return cfg.sub.y


x: str = takes_cfg(cfg)
b: bool = cfg.b
y: int = takes_sub(cfg.sub)
s: str = cfg.secret
ds: str = cfg.d_secret
vs: str = cfg.v_secret
as_: str = cfg.a_secret
