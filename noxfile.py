from __future__ import annotations

import os
import re

from pathlib import Path

import nox


nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True


# Avoid dependencies on YAML / TOML libs using a questionable hacks.
match_docs_python = re.compile(r"\s+python\: \"(\d\.\d\d)\"").fullmatch
for line in Path(".readthedocs.yaml").read_text().splitlines():
    m = match_docs_python(line)
    if m:
        DOCS_PYTHON = m.group(1)
        break

match_oldest_python = re.compile(
    r"requires-python = \">=(\d\.\d+)\""
).fullmatch
match_oldest_attrs = re.compile(r".*\"attrs>=(\d+\.\d+\.\d+)\",.*").match
for line in Path("pyproject.toml").read_text().splitlines():
    m = match_oldest_python(line)
    if m:
        OLDEST_PYTHON = m.group(1)

    m = match_oldest_attrs(line)
    if m:
        OLDEST_ATTRS = m.group(1)
        break  # dependencies always come after requires-python


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


@nox.session(python=OLDEST_PYTHON, tags=["tests"])
def tests_oldest_attrs(session: nox.Session) -> None:
    session.install(".[tests]", f"attrs=={OLDEST_ATTRS}")

    _cov(session)


@nox.session
def coverage_report(session: nox.Session) -> None:
    session.install("coverage[toml]")

    session.run("coverage", "combine")
    session.run("coverage", "report", "--fail-under=100")


@nox.session
def mypy(session: nox.Session) -> None:
    session.install(".", "mypy")

    session.run("mypy", "typing_examples.py")


@nox.session(python=DOCS_PYTHON)
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
