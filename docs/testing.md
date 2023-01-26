# Testing Applications

Given that your configuration is usually loaded at module level and thus, at import time, testing applications across varying settings is not straight-forward.

The best way is to isolate the interaction with the environment into one file as well as possible, and then hand around instances of your configurations instead.

Let's use a simple web application that runs using [Gunicorn](https://docs.gunicorn.org/) as example.

A WSGI server needs an entry point from where it's loading the web application.
A good name for that is `wsgi.py`, either at the root of your application or within a directory like `entrypoints` (this is useful if you have more than one entrypoint – for instance a worker process or CLI).

This file needs to create the application and put it into the global namespace, such that Gunicorn can find it.
Conventionally, `application` is a good name and allows you to run the web application like this: `gunicorn your_app.wsgi`


## Entry Points

How much logic do you put into your `wsgi.py` entry point?
As little as possible.
Just interact with the runtime environment, possibly run code than must run exactly once like {mod}`logging` configuration, but then call out into other modules as soon as possible.

For example:

```python
import environ

from .app_maker import make_app
from .config import AppConfig
from .logging import setup_logging

app_cfg = environ.to_config(AppConfig)

setup_logging(app_cfg)
application = make_app(app_cfg)
```

Now you only have to write two functions:

- `setup_logging()` that takes a configuration and configures {mod}`logging`.
- `make_app()` that creates a WSGI application based on your configuration.
  Flask calls this an [*Application Factory*](https://flask.palletsprojects.com/en/latest/patterns/appfactories/) and you would instantiate `flask.Flask`, load your [blueprints](https://flask.palletsprojects.com/en/latest/blueprints/), et cetera here.

As you can see: you can now test both `setup_logging` as well as `make_app` without loading the configuration from your environment every single time.

You probably shouldn't touch `wsgi.py` in your tests at all, unless you want to do extensive end-to-end tests using a web driver.
Your most importantly shouldn't import anything from this entry point.
If you need the configuration in your views, simply attach the `app_cfg` object to your Flask application in `make_app()`..


## Fixtures

Instead, assuming you're using *pytest*, you can create a bunch fixtures that drive all your tests:

```python
@pytest.fixture(scope="session")
def _app_cfg():
    return environ.to_config(AppConfig, environ={"APP_ENV": "test"})

@pytest.fixture(name="app")
def _app(app_cfg):
    return make_app(app_cfg)

@pytest.fixture(name="client")
def _client(app):
    return app.test_client()
```

Now you have complete freedom to parametrize your `app` fixture if you need to.
