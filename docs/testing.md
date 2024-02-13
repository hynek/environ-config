# Testing Applications

Since your configuration is usually loaded at the module level and, thus, at import time, testing applications across varying settings is not straightforward.

The best way is to isolate the interaction with the environment into one file as well as possible and then hand around instances of your configurations instead.

Let's use a simple web application running on top of [Gunicorn](https://docs.gunicorn.org/) as an example.

A WSGI server needs an entry point from where it's loading the web application.
A good name for that is `wsgi.py`, either at the root of your application or within a directory like `entrypoints` (this is useful if you have more than one entrypoint – for instance, a worker process or CLI).

This file needs to create the application and put it into the global namespace so that Gunicorn can find it.
Conventionally, `application` is a good name and allows you to run the web application using `gunicorn your_app.wsgi`.


## Entry Points

How much logic do you put into your `wsgi.py` entry point?
As little as possible.
Only interact with the runtime environment, possibly run code that must run exactly once like {mod}`logging` configuration, but then call out into other modules as soon as possible.

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

Now, you only have to write two functions:

- `setup_logging()` that takes a configuration and configures {mod}`logging`.
- `make_app()` that creates a WSGI application based on your configuration.
  Flask calls this an [*Application Factory*](https://flask.palletsprojects.com/en/latest/patterns/appfactories/), and you would instantiate `flask.Flask`, load your [blueprints](https://flask.palletsprojects.com/en/latest/blueprints/), and so forth here.

As you can see, you can now test both `setup_logging` and `make_app` without loading the configuration from your environment every single time.

You probably shouldn't touch `wsgi.py` in your tests at all, unless you want to do extensive end-to-end tests using a web driver.
Most importantly, you shouldn't import anything from this entry point.
If you need the configuration in your views, attach the `app_cfg` object to your Flask application in `make_app()`.


## Fixtures

Instead, assuming you're using *pytest*, you can create a bunch of fixtures that drive all your tests:

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

Now, you have complete freedom to parametrize your `app` fixture if necessary.
