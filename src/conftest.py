import pytest
from django.core.management import call_command


@pytest.fixture(scope="session")
def _collectstatic():
    call_command("collectstatic", interactive=False, verbosity=0)


@pytest.fixture
def live_server(settings, live_server):
    settings.STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
    return live_server


@pytest.fixture
def firefox_options(firefox_options):
    firefox_options.add_argument("-headless")
    return firefox_options


@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(3)
    selenium.set_window_size(3860, 2140)
    return selenium
