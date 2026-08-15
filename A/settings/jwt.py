"""JWT (SimpleJWT) settings."""

from datetime import timedelta

from ._env import env_int

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=env_int('JWT_ACCESS_LIFETIME_DAYS', 1)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env_int('JWT_REFRESH_LIFETIME_DAYS', 7)),
    'ROTATE_REFRESH_TOKENS': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
