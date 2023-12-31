from __future__ import annotations

import os

import nox


nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True


RUN_UNDER_COVERAGE = ["3.7", "3.11"]
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


def _cov(session: nox.Session) -> None:
    session.run("coverage", "run", "-m", "pytest", *session.posargs)

    if os.environ.get("CI") != "true":
        session.notify("coverage_report")


@nox.session(python=RUN_UNDER_COVERAGE, tags=["tests"])
def tests_cov(session: nox.Session) -> None:
    session.install(".[tests]")

    _cov(session)


@nox.session(python=NOT_COVERAGE, tags=["tests"])
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

    session.run("mypy", "tests/typing")


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
