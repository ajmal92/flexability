import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "smart_physio.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import smart_physio.users.signals  # noqa: F401
