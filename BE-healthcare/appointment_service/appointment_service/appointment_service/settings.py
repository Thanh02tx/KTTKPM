from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-@!*fd3h37t+#u7ut_dl_o$*(b_f15!$^^wkj*f5+0br+1n@n*t'

DEBUG = True
# CORS setup
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",   # Frontend React
    "http://localhost:8002",   # schedule_service
    "http://localhost:8003",   # patient_service
    "http://localhost:8001",   # nếu có thêm service khác
    "http://localhost:8004",
    "http://localhost:8005",
    "http://localhost:8006",
    "http://localhost:8007"
]
CORS_ALLOW_CREDENTIALS = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',  
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # App của bạn
    'appointment',

    # Third-party packages
    'rest_framework',
    'corsheaders',
    'djongo',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',           # Luôn để trên cùng
    'django.middleware.common.CommonMiddleware',       # Sau CorsMiddleware

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Đường dẫn chuẩn
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'appointment_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  
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

WSGI_APPLICATION = 'appointment_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'appointment_db',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb://localhost:27017/',
            'serverSelectionTimeoutMS': 5000,
        }
    }
}

# REST Framework cấu hình đơn giản, không auth
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}

# Bạn có thể bỏ hẳn nếu không cần user auth
AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
