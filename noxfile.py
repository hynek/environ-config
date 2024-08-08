from __future__ import annotations

import os

import nox


nox.needs_version = ">=2024.3.2"
nox.options.default_venv_backend = "uv|virtualenv"
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True


RUN_UNDER_COVERAGE = ["3.8", "3.12"]
ALL_SUPPORTED = [
    # [[[cog
    # for line in open("pyproject.toml"):
    #     if "Programming Language :: Python :: " in line:
    #         cog.outl(f'"{line.rsplit(" ")[-1][:-3]}",')
    # ]]]
    "3.8",
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
    # [[[end]]]
]
OLDEST_PYTHON = ALL_SUPPORTED[0]
NOT_COVERAGE = [v for v in ALL_SUPPORTED if v not in RUN_UNDER_COVERAGE]

# [[[cog
# import yaml
# with open(".readthedocs.yaml") as f:
#     rtd = yaml.safe_load(f)
# cog.outl(f'DOCS_PYTHON = "{rtd["build"]["tools"]["python"]}"')
# ]]]
DOCS_PYTHON = "3.12"
# [[[end]]]

# [[[cog
# import tomllib
# with open("pyproject.toml", "rb") as f:
#     deps = tomllib.load(f)["project"]["dependencies"]
# for dep in deps:
#     if dep.startswith("attrs"):
#         cog.outl(f'OLDEST_ATTRS = "{dep[7:]}"')
#         break
# ]]]
OLDEST_ATTRS = "17.4.0"
# [[[end]]]


@nox.session
def cog(session: nox.Session) -> None:
    session.install("cogapp", "PyYAML")

    session.run(
        "cog", *session.posargs, "-r", "noxfile.py", ".github/workflows/ci.yml"
    )


@nox.session
def pre_commit(session: nox.Session) -> None:
    session.install("pre-commit")

    session.run("pre-commit", "run", "--all-files")


def _get_pkg(posargs: list[str], cov: bool) -> tuple[str, list[str]]:
    """
    Allow `--installpkg path/to/wheel.whl` to be passed.
    """
    posargs = list(posargs)

    try:
        i = posargs.index("--installpkg")
        pkg = posargs[i + 1]
        del posargs[i : i + 2]
    except ValueError:
        pkg = "."

    extra = "cov" if cov else "tests"

    return f"{pkg}[{extra}]", posargs


def _cov(session: nox.Session, posargs: list[str]) -> None:
    session.run("coverage", "run", "-m", "pytest", *posargs)

    if os.environ.get("CI") != "true":
        session.notify("coverage_report")


@nox.session(python=RUN_UNDER_COVERAGE, tags=["tests"])
def tests_cov(session: nox.Session) -> None:
    pkg, posargs = _get_pkg(session.posargs, cov=True)
    session.install(pkg)

    _cov(session, posargs)


@nox.session(python=NOT_COVERAGE, tags=["tests"])
def tests(session: nox.Session) -> None:
    pkg, posargs = _get_pkg(session.posargs, cov=False)
    session.install(pkg)

    session.run("pytest", *posargs)


@nox.session(python=OLDEST_PYTHON, tags=["tests"])
def tests_oldest_attrs(session: nox.Session) -> None:
    pkg, posargs = _get_pkg(session.posargs, cov=True)
    session.install(pkg, f"attrs=={OLDEST_ATTRS}")

    _cov(session, posargs)


@nox.session
def coverage_report(session: nox.Session) -> None:
    session.install("coverage[toml]")

    session.run("coverage", "combine")
    session.run("coverage", "report", "--fail-under=100")


@nox.session
def mypy(session: nox.Session) -> None:
    session.install(".", "mypy")

    session.run("mypy", "tests/typing")


@nox.session(python=DOCS_PYTHON)
def docs(session: nox.Session) -> None:
    if session.posargs and session.posargs[0] == "watch":
        session.install("-e", ".[docs]", "watchfiles")
        session.run(
            "watchfiles",
            "--ignore-paths",
            "docs/_build",
            "python -Im sphinx "
            "-T -E "
            "-W --keep-going "
            "-b html "
            "-d docs/_build/doctrees "
            "-D language=en "
            "-n "
            "docs "
            "docs/_build/html",
        )
        return

    session.install(".[docs]")

    for cmd in (
        [session.posargs[0]] if session.posargs else ["html", "doctest"]
    ):
        session.run(
            # fmt: off
            "python", "-m", "sphinx",
            "-T", "-E",
            "-W", "--keep-going",
            "-b", cmd,
            "-d", "docs/_build/doctrees",
            "-D", "language=en",
            "-n",
            "docs",
            "docs/_build/html",
            # fmt: on
        )
    session.run("python", "-m", "doctest", "README.md")
