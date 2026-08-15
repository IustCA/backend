"""Development settings: compose every concern module, then dev overrides.

Run locally with:  DJANGO_SETTINGS_MODULE=A.settings.development
"""

# Compose every concern module so all settings are available.
from .base import *  # noqa: F401,F403
from .apps import *  # noqa: F401,F403
from .middleware import *  # noqa: F401,F403
from .templates import *  # noqa: F401,F403
from .routing import *  # noqa: F401,F403
from .database import *  # noqa: F401,F403
from .authentication import *  # noqa: F401,F403
from .localization import *  # noqa: F401,F403
from .static_media import *  # noqa: F401,F403
from .rest_framework import *  # noqa: F401,F403
from .jwt import *  # noqa: F401,F403
from .cors import *  # noqa: F401,F403
from .swagger import *  # noqa: F401,F403
from .password_hashers import DEV_PASSWORD_HASHERS  # noqa: F401,F403


# Dev overrides
DEBUG = True
ALLOWED_HOSTS = ['*']

PASSWORD_HASHERS = DEV_PASSWORD_HASHERS
