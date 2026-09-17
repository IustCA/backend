"""Authentication: custom user model and password validators."""

AUTH_USER_MODEL = 'accounts.User'

# Disable password validators so admin panel allows any password (numeric, short, simple, etc.)
AUTH_PASSWORD_VALIDATORS = []
