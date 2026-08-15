"""Cross-environment core: secret key, hosts, default field type."""

from ._env import env_list, env_str

SECRET_KEY = env_str('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production')

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', ['*'])

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
