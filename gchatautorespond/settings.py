import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS_DIR = os.path.join(BASE_DIR, 'secrets')


def get_secret(filename):
    with open(os.path.join(SECRETS_DIR, filename)) as f:
        return f.read().strip()

DEBUG = False
SECRET_KEY = get_secret('secret_key.txt')
QUEUE_AUTH_KEY = get_secret('queue_auth_key.txt')

SCHEME = 'https://'
HOST = 'gchat.simon.codes'
ALLOWED_HOSTS = [HOST]
PORT = 8000

CLIENT_SECRETS_PATH = os.path.join(SECRETS_DIR, 'client_secrets.json')
OAUTH_SCOPE = ' '.join(['https://www.googleapis.com/auth/googletalk', 'email'])
OAUTH_REDIRECT_URI = "%s%s/%s" % (SCHEME, HOST, 'autorespond/oauth2callback/')

LOGIN_URL = '/'

# Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Adding this fixes a 1.9 upgrade warning, but also requires that we
    # set up the db to support Sites.
    #'django.contrib.sites',

    'gchatautorespond.apps.autorespond',

    # Putting the admin app after our own prevents overriding
    # password reset templates.
    'django.contrib.admin',

    'djsupervisor',
    'registration',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'gchatautorespond.middleware.ExceptionMiddleware',
)

ROOT_URLCONF = 'gchatautorespond.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gchatautorespond.wsgi.application'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s: %(asctime)s - %(name)s: %(message)s'
        },
        'withfile': {
            'format': '%(levelname)s: %(asctime)s - %(name)s (%(module)s:%(lineno)s): %(message)s'
        },
    },
    'handlers': {
        'console_simple': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console_verbose': {
            'class': 'logging.StreamHandler',
            'formatter': 'withfile',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console_simple'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
        },
        'django.request': {
            'handlers': ['console_simple'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'sleekxmpp': {
            'handlers': ['console_simple'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'gchatautorespond': {
            'handlers': ['console_verbose'],
            'level': 'INFO',
        },
    },
}

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# The code directory gets wiped when deploying, so in prod we want
# the db up a level so it doesn't get deleted.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '..', 'gchat_db.sqlite3')
    }
}

# Email
EMAIL_HOST = 'mail.gandi.net'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'gchat@simon.codes'
EMAIL_HOST_PASSWORD = get_secret('gchat@simon.codes.password')
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ADMINS = (('Simon', 'simon@simonmweber.com'),)
SERVER_EMAIL = DEFAULT_FROM_EMAIL


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'assets')
STATIC_URL = '/assets/'


# Django Registration
ACCOUNT_ACTIVATION_DAYS = 1