"""Noxfile."""

import nox


@nox.session(python="3.8", reuse_venv=True)
def lint(session) -> None:
    session.install("poetry")
    session.run("poetry", "install")
    session.run("ruff", "check", "--config=pyproject.toml", ".")
    session.run("black", "--config=pyproject.toml", "--check", ".")


@nox.session(python="3.8", reuse_venv=True)
def fixlint(session) -> None:
    session.install("poetry")
    session.run("poetry", "install")
    session.run("ruff", "check", "--config=pyproject.toml", ".", "--fix")
    session.run("black", "--config=pyproject.toml", ".")
