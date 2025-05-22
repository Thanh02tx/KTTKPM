from pathlib import Path
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-@!*fd3h37t+#u7ut_dl_o$*(b_f15!$^^wkj*f5+0br+1n@n*t'

DEBUG = True

ALLOWED_HOSTS = []

# CORS setup
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",   # Frontend React
    "http://localhost:8002",   # schedule_service
    "http://localhost:8003",   # patient_service
    "http://localhost:8001", 
    "http://localhost:8004",
    "http://localhost:8005",# nếu có thêm service khác
    "http://localhost:8006",
    "http://localhost:8007"
]
CORS_ALLOW_CREDENTIALS = True

# CSRF setup (quan trọng để PUT/POST không bị 403)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',  
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # App của bạn
    'laboratory',
    
    # Third-party packages
    'rest_framework',
    'corsheaders',
    'djongo',
    'cloudinary',
    'cloudinary_storage',
]
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUD_NAME'),
    'API_KEY': os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET'),
}

# ✅ Gọi cloudinary.config để cấu hình
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET']
)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS để trên cùng
    'django.middleware.common.CommonMiddleware',  # CommonMiddleware liền sau

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'laboratory_service.urls'

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

WSGI_APPLICATION = 'laboratory_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'laboratory_db',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb://localhost:27017/',
            'serverSelectionTimeoutMS': 5000,
        }
    }
}

# REST Framework cấu hình đơn giản
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024 