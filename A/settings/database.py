"""Database configuration."""

from ._env import BASE_DIR, env_str

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / env_str('DB_NAME', 'db.sqlite3'),
    }
}
