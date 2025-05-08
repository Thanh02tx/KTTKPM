from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta

# Load biến môi trường từ file .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Lấy từ file .env
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = True

ALLOWED_HOSTS = []

# Ứng dụng cài đặt
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Đảm bảo thêm cái này
    'rest_framework_simplejwt',  # Đảm bảo thêm cái này
    'corsheaders',  # Thêm để hỗ trợ CORS
    'user',  # Đây là ứng dụng của bạn
]

# Cấu hình JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT Settings (đầy đủ)
SIMPLE_JWT = {
    'ROTATE_REFRESH_TOKENS': False,  # Không sử dụng Refresh Token
    'BLACKLIST_AFTER_ROTATION': True,  # Hủy bỏ token sau khi quay
    'ALGORITHM': 'HS256',  # Sử dụng thuật toán HS256 cho JWT
    'SIGNING_KEY': SECRET_KEY,  # Sử dụng SECRET_KEY từ môi trường
    'AUTH_HEADER_TYPES': ('Bearer',),  # Đảm bảo rằng header là Bearer token
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365 * 100),  # Hạn sử dụng 100 năm cho access token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365 * 100),  # Tương tự cho refresh token
}

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Đảm bảo có cái này
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Đảm bảo có cái này
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS config cho frontend React
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # URL của frontend React
    "http://localhost:8002",  # Các dịch vụ khác có thể được phép truy cập
    "http://localhost:8003", 
    "http://localhost:8001",
    "http://localhost:8004",
    "http://localhost:8005",
    "http://localhost:8006",
    "http://localhost:8007",
]

CORS_ALLOW_METHODS = [
    "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS",
]

CORS_ALLOW_HEADERS = [
    "content-type", "authorization", "x-requested-with",
    "accept", "origin", "accept-encoding", "x-csrftoken",
]

ROOT_URLCONF = 'user_service.urls'

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

WSGI_APPLICATION = 'user_service.wsgi.application'

# Cấu hình cơ sở dữ liệu
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'user_db',  # Tên cơ sở dữ liệu của bạn
        'USER': 'root',  # Tên người dùng MySQL
        'PASSWORD': '123456',  # Mật khẩu người dùng MySQL
        'HOST': 'localhost',  # Địa chỉ host (localhost nếu cài đặt trên máy tính của bạn)
        'PORT': '3306',  # Cổng MySQL
    }
}

# Xác thực mật khẩu
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Quốc tế hoá
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Custom user model
AUTH_USER_MODEL = 'user.User'

# Static
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
