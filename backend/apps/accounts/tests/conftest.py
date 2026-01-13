import pytest
from django.urls import reverse
from django.test import Client
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings


@pytest.fixture
def client():
    """Provide Django test client."""
    return Client()


@pytest.fixture
def mailbox():
    """Capture emails during tests."""
    with override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
        yield mail.outbox
