from pathlib import Path

from invoke import Context, task

BASE_DIR = Path(__file__).parent.resolve(strict=True)
SRC_DIR = BASE_DIR / "src"
COMPOSE_BUILD_FILE = BASE_DIR / "docker-compose-build.yaml"
COMPOSE_BUILD_ENV = {"COMPOSE_FILE": COMPOSE_BUILD_FILE}
TEST_ENV = {"ENV_FILE": BASE_DIR / "envs" / "test-envs.env"}


@task
def update_dependencies(ctx: Context):
    with ctx.cd(BASE_DIR):
        ctx.run("uv lock --upgrade", pty=True, echo=True)


@task
def sync_dependencies(ctx: Context):
    with ctx.cd(BASE_DIR):
        ctx.run("uv sync", pty=True, echo=True)


@task
def makemessages(ctx: Context) -> None:
    with ctx.cd(SRC_DIR):
        ctx.run(
            "./manage.py makemessages -l en -l fr --add-location file",
            pty=True,
            echo=True,
        )


@task
def compilemessages(ctx: Context) -> None:
    with ctx.cd(SRC_DIR):
        ctx.run("./manage.py compilemessages -l en -l fr", pty=True, echo=True)


@task(pre=[compilemessages])
def test(ctx: Context) -> None:
    with ctx.cd(SRC_DIR):
        ctx.run("pytest", pty=True, echo=True)


@task(pre=[compilemessages])
def test_cov(ctx: Context) -> None:
    with ctx.cd(SRC_DIR):
        ctx.run(
            "pytest --cov=. --cov-branch --cov-report term-missing:skip-covered",
            pty=True,
            echo=True,
            env={"COVERAGE_FILE": BASE_DIR / ".coverage"},
        )


@task
def download_db(ctx: Context) -> None:
    with ctx.cd(BASE_DIR):
        ctx.run("scp ubuntu:/mnt/data/checkout/db/db.sqlite3 ./db/db.sqlite3")
        ctx.run("rm -rf src/media/")
        ctx.run("scp -r ubuntu:/mnt/data/checkout/media/ ./src/media")
    with ctx.cd(SRC_DIR):
        ctx.run("./manage.py changepassword gaugendre", pty=True)


@task
def update_fixtures(ctx: Context) -> None:
    with ctx.cd(SRC_DIR):
        ctx.run(
            "./manage.py dumpdata purchase.Product purchase.ProductCategory --natural-primary --natural-foreign -o ./purchase/fixtures/products.json",
            echo=True,
            pty=True,
        )
        ctx.run(
            "./manage.py dumpdata purchase.PaymentMethod --natural-primary --natural-foreign -o ./purchase/fixtures/payment_methods.json",
            echo=True,
            pty=True,
        )
        ctx.run(
            "pre-commit run --files ./purchase/fixtures/products.json ./purchase/fixtures/payment_methods.json",
            echo=True,
            pty=True,
        )
