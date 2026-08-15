"""Settings dispatcher.

Set APP_ENV in your .env (or process env) to switch between modules:

  APP_ENV=development   ->  A.settings.development
  APP_ENV=production    ->  A.settings.production
  APP_ENV=local         ->  A.settings.local  (create from local.py.example)

Anything else falls back to development.

`DJANGO_SETTINGS_MODULE` should be set to `A.settings` so the dispatcher
chooses the right concrete module on import.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env as early as possible so APP_ENV is available.
load_dotenv(BASE_DIR / '.env')


APP_ENV = os.getenv('APP_ENV', 'development').lower()

if APP_ENV == 'production':
    from .production import *  # noqa: F401,F403
elif APP_ENV == 'local':
    from .local import *  # noqa: F401,F403
else:
    from .development import *  # noqa: F401,F403
