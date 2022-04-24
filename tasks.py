"""
Invoke management tasks for the project.

The current implementation with type annotations is not compatible
with invoke 1.6.0 and requires manual patching.

See https://github.com/pyinvoke/invoke/pull/458/files
"""


import time
from pathlib import Path

import requests
from invoke import Context, task

BASE_DIR = Path(__file__).parent.resolve(strict=True)
SRC_DIR = BASE_DIR / "src"
COMPOSE_BUILD_FILE = BASE_DIR / "docker-compose-build.yaml"
COMPOSE_BUILD_ENV = {"COMPOSE_FILE": COMPOSE_BUILD_FILE}


@task
def test(ctx: Context) -> None:
    with ctx.cd(SRC_DIR):
        ctx.run("pytest", pty=True, echo=True)


@task
def test_cov(ctx: Context) -> None:
    with ctx.cd(SRC_DIR):
        ctx.run(
            "pytest --cov=. --cov-branch --cov-report term-missing:skip-covered",
            pty=True,
            echo=True,
            env={"COVERAGE_FILE": BASE_DIR / ".coverage"},
        )


@task
def pre_commit(ctx: Context) -> None:
    with ctx.cd(BASE_DIR):
        ctx.run("pre-commit run --all-files", pty=True)


@task
def mypy(ctx: Context) -> None:
    with ctx.cd(BASE_DIR):
        ctx.run("pre-commit run --all-files mypy", pty=True)


@task(pre=[pre_commit, test_cov])
def check(ctx: Context) -> None:
    pass


@task
def build(ctx: Context) -> None:
    with ctx.cd(BASE_DIR):
        ctx.run(
            "docker-compose build django", pty=True, echo=True, env=COMPOSE_BUILD_ENV
        )


@task
def publish(ctx: Context) -> None:
    with ctx.cd(BASE_DIR):
        ctx.run(
            "docker-compose push django", pty=True, echo=True, env=COMPOSE_BUILD_ENV
        )


@task
def deploy(ctx: Context) -> None:
    ctx.run("ssh ubuntu /home/gaugendre/checkout/update", pty=True, echo=True)


@task
def check_alive(ctx: Context) -> None:
    exception = None
    for _ in range(5):
        try:
            res = requests.get("https://gabnotes.org")
            res.raise_for_status()
            print("Server is up & running")
            return
        except requests.exceptions.HTTPError as e:
            time.sleep(2)
            exception = e
    raise RuntimeError("Failed to reach the server") from exception


@task(pre=[check, build, publish, deploy], post=[check_alive])
def beam(ctx: Context) -> None:
    pass


@task
def download_db(ctx: Context) -> None:
    with ctx.cd(BASE_DIR):
        ctx.run("scp ubuntu:/home/gaugendre/checkout/db/db.sqlite3 ./db/db.sqlite3")
        ctx.run("rm -rf src/media/")
        ctx.run("scp -r ubuntu:/home/gaugendre/checkout/media/ ./src/media")
    with ctx.cd(SRC_DIR):
        ctx.run("./manage.py changepassword gaugendre", pty=True)
