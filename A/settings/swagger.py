"""drf-spectacular / OpenAPI settings."""


def custom_preprocessing_hook(endpoints, **kwargs):
    """
    Filter endpoints for Swagger documentation:
    1. Only include canonical endpoints mounted under /api/accounts/
    2. Exclude alias endpoint /api/accounts/search/ in favor of /api/accounts/students/
    """
    filtered = []
    for path, path_regex, method, callback in endpoints:
        if not path.startswith('/api/accounts/'):
            continue
        if path == '/api/accounts/search/':
            continue
        filtered.append((path, path_regex, method, callback))
    return filtered


SPECTACULAR_SETTINGS = {
    'TITLE': 'سامانه رزومه و پرتال دانشجویی (IUST CA API)',
    'DESCRIPTION': (
        'مستندات کامل API سامانه رزومه و پورتفولیوی دانشجویی دانشگاه علم و صنعت ایران.\n\n'
        'شامل احراز هویت (شماره دانشجویی و کد ملی/رمز عبور)، مدیریت پروفایل یکپارچه، جستجوی دانشجویان با آفست و CRUD رزومه.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/accounts/',
    'PREPROCESSING_HOOKS': [
        'A.settings.swagger.custom_preprocessing_hook',
    ],
    'SECURITY': [{'BearerAuth': []}],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': "Type 'Bearer <JWT>' (with space)",
            },
        },
    },
}

