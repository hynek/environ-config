from __future__ import annotations

import os

import nox


nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True


@nox.session
def pre_commit(session: nox.Session) -> None:
    session.install("pre-commit")

    session.run("pre-commit", "run", "--all-files")


def _cov(session: nox.Session) -> None:
    session.run("coverage", "run", "-m", "pytest", *session.posargs)

    if os.environ.get("CI") != "true":
        session.notify("coverage_report")


@nox.session(python=["3.7", "3.11"], tags=["tests"])
def tests_cov(session: nox.Session) -> None:
    session.install(".[tests]")

    _cov(session)


@nox.session(python=["3.8", "3.9", "3.10", "3.12"], tags=["tests"])
def tests(session: nox.Session) -> None:
    session.install(".[tests]")

    session.run("pytest", *session.posargs)


@nox.session(python="3.7", tags=["tests"])
def tests_oldestAttrs(session: nox.Session) -> None:
    # Keeps attrs pin in sync with pyproject.toml/dependencies.
    session.install(".[tests]", "attrs==17.4.0")

    _cov(session)


@nox.session
def coverage_report(session: nox.Session) -> None:
    session.install("coverage[toml]")

    session.run("coverage", "combine")
    session.run("coverage", "report")


@nox.session
def mypy(session: nox.Session) -> None:
    session.install(".", "mypy")

    session.run("mypy", "typing_examples.py")


# Keep python in sync with ci.yml/docs and .readthedocs.yaml.
@nox.session(python="3.10")
def docs(session: nox.Session) -> None:
    session.install(".[docs]")

    for cmd in ["html", "doctest"]:
        session.run(
            # fmt: off
            "python", "-m", "sphinx",
            "-T", "-E",
            "-W", "--keep-going",
            "-b", cmd,
            "-d", "docs/_build/doctrees",
            "-D", "language=en",
            "docs",
            "docs/_build/html",
            # fmt: on
        )
    session.run("python", "-m", "doctest", "README.md")
