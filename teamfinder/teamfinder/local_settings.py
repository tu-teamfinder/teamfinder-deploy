import dj_database_url
from environ import Env
env = Env()
Env.read_env()

SECRET_KEY = env('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': dj_database_url.parse(env('DATABASE_URL'))
}

CSRF_TRUSTED_ORIGINS = ['https://teamfinder.pythonanywhere.com']

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(env('REDIS_URL'))],
        },
    },
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUD_NAME'),
    'API_KEY': env('API_KEY_CLOUD'),
    'API_SECRET': env('API_SECRET')
}
