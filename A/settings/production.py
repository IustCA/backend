"""Production settings: compose every concern module, then prod overrides.

Run with:  DJANGO_SETTINGS_MODULE=A.settings.production
"""

import os

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
from .password_hashers import PROD_PASSWORD_HASHERS  # noqa: F401,F403
from .security import *  # noqa: F401,F403


# Production overrides
DEBUG = False

ALLOWED_HOSTS = [h for h in os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()]

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    raise RuntimeError('DJANGO_SECRET_KEY is required in production.')

PASSWORD_HASHERS = PROD_PASSWORD_HASHERS
