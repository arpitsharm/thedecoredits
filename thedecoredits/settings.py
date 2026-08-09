"""

Django settings for thedecoredits project.

Generated using Django 5.2.x

"""



from pathlib import Path

import os



# ==============================

# BASE DIRECTORY

# ==============================



BASE_DIR = Path(__file__).resolve().parent.parent





# ==============================

# SECURITY SETTINGS

# ==============================



SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'p%w2%f2w5tdu&r_+8-078l&4(o6w+y#(gfe@$^2(n%mn@#v7*&')



DEBUG = False



ALLOWED_HOSTS = ['72.62.129.226', 'www.thedecoredits.com', 'thedecoredits.com']
# ALLOWED_HOSTS = []



DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800   # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800   # 50MB


# ==============================

# APPLICATION DEFINITION

# ==============================



INSTALLED_APPS = [

    'jazzmin',

    'django.contrib.admin',

    'django.contrib.auth',

    'django.contrib.contenttypes',

    'django.contrib.sessions',

    'django.contrib.messages',

    'django.contrib.staticfiles',
    
    'django_extensions',


    'home',

]



MIDDLEWARE = [

    'home.middleware.RateLimitMiddleware',

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]
# When the vps fully works on https://
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
# Production HTTPS settings - ENABLED for Hostinger VPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')



TEMPLATES = [

    {

        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'templates'],

        'APP_DIRS': True,

        'OPTIONS': {

            'context_processors': [

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

            ],

        },

    },

]



ROOT_URLCONF = 'thedecoredits.urls'

WSGI_APPLICATION = 'thedecoredits.wsgi.application'





# ==============================

# DATABASE

# ==============================



DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.sqlite3',

        'NAME': BASE_DIR / 'db.sqlite3',

    }

}




AUTH_PASSWORD_VALIDATORS = [

    {

        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',

    },

    {

        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',

    },

    {

        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',

    },

    {

        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',

    },

]





# ==============================

# INTERNATIONALIZATION

# ==============================



LANGUAGE_CODE = 'en-us'



TIME_ZONE = 'Asia/Kolkata'



USE_I18N = True

USE_TZ = True





# ==============================

# STATIC FILES

# ==============================



STATIC_URL = '/static/'



STATICFILES_DIRS = [

    BASE_DIR / 'static',

]



STATIC_ROOT = BASE_DIR / 'staticfiles'





# ==============================

# MEDIA FILES

# ==============================



MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'





# ==============================

# EMAIL CONFIGURATION

# ==============================



# Development mode (prints email in terminal)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'



# Production Example (Gmail SMTP)

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# EMAIL_HOST = 'smtp.gmail.com'

# EMAIL_PORT = 587

# EMAIL_USE_TLS = True

# EMAIL_HOST_USER = 'your_email@gmail.com'

# EMAIL_HOST_PASSWORD = 'your_app_password'

# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER





# ==============================

# PAYTM CONFIGURATION (TEST MODE)

# ==============================



PAYTM_MERCHANT_ID = 'YOUR_MERCHANT_ID'

PAYTM_MERCHANT_KEY = 'YOUR_MERCHANT_KEY'

PAYTM_WEBSITE = 'WEBSTAGING'

PAYTM_CHANNEL_ID = 'WEB'

PAYTM_INDUSTRY_TYPE_ID = 'Retail'

PAYTM_ENVIRONMENT = 'TEST'





# ==============================

# DEFAULT PRIMARY KEY

# ==============================



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/admin/login/'



# ==============================

# ADDITIONAL SECURITY HEADERS

# ==============================

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

X_FRAME_OPTIONS = 'DENY'

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_AGE = 3600  # 1 hour session expiry

SESSION_EXPIRE_AT_BROWSER_CLOSE = True



# ==============================

# GUNICORN SETTINGS (for VPS deployment)

# ==============================

# Run with: gunicorn thedecoredits.wsgi:application --workers 3 --bind 127.0.0.1:8000

# Workers = (2 x CPU cores) + 1

# For KVM 1 (1-2 CPU cores): use 3 workers max





# ==============================

# JAZZMIN SETTINGS

# ==============================

