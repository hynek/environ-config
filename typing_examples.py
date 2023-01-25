import environ


@environ.config
class Config:
    @environ.config
    class Sub:
        y: int = environ.var(converter=int)

    x: str = environ.var()
    sub: Sub = environ.group(Sub)


cfg = environ.to_config(Config, {"APP_X": "123"})


def takes_cfg(c: Config) -> str:
    return c.x


def takes_sub(s: Config.Sub) -> int:
    return cfg.sub.y


x: str = takes_cfg(cfg)
y: int = takes_sub(cfg.sub)
