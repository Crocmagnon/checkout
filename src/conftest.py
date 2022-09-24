import pytest
from django.core.management import call_command


@pytest.fixture(scope="session")
def _collectstatic():
    call_command("collectstatic", interactive=False, verbosity=0)


@pytest.fixture()
def live_server(settings, live_server):
    settings.STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
    return live_server


@pytest.fixture()
def selenium(selenium):
    selenium.implicitly_wait(3)
    return selenium
