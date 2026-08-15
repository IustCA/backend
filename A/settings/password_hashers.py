"""Password hashers.

Development uses the fast MD5 hasher; production switches to Argon2.
The actual selection is done in development.py / production.py.
"""

DEFAULT_PASSWORD_HASHER = 'django.contrib.auth.hashers.PBKDF2PasswordHasher'

DEV_PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

PROD_PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]
