"""
Security hardening configuration for production deployment.
Apply these settings to backend/packaxis/settings.py for production environments.
"""

# ============================================================================
# SESSION & COOKIE SECURITY (Production)
# ============================================================================

# Enforce HTTPS-only cookies
SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
CSRF_COOKIE_SECURE = True     # Only send CSRF cookie over HTTPS
SECURE_SSL_REDIRECT = True    # Redirect HTTP to HTTPS

# Session protection
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection (Lax/Strict)
CSRF_COOKIE_HTTPONLY = True      # Prevent JavaScript access to CSRF

# Session timeout (30 minutes of inactivity)
SESSION_COOKIE_AGE = 1800
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# ============================================================================
# PASSWORD VALIDATION (Hardened)
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12}  # Increased from 8
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ============================================================================
# ALLAUTH EMAIL VERIFICATION (Mandatory for production)
# ============================================================================

ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Changed from "optional"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Email confirmation grace period (24 hours)
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

# ============================================================================
# SECURITY HEADERS
# ============================================================================

# HSTS - Force HTTPS for 1 year
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# X-Frame-Options - Prevent clickjacking
X_FRAME_OPTIONS = "DENY"

# Content Security Policy
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'"),  # Consider removing unsafe-inline
    "style-src": ("'self'", "'unsafe-inline'"),   # Consider removing unsafe-inline
    "img-src": ("'self'", "data:", "https:"),
    "font-src": ("'self'",),
    "connect-src": ("'self'",),
}

# ============================================================================
# AUTHENTICATION BACKENDS
# ============================================================================

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

# ============================================================================
# RATE LIMITING / BRUTE FORCE PROTECTION
# ============================================================================

# Install django-axes for lockout protection:
# pip install django-axes

INSTALLED_APPS = [
    # ... other apps ...
    "axes",  # Must be before django.contrib.auth
]

AXES_FAILURE_LIMIT = 5  # Lock after 5 failed attempts
AXES_COOLOFF_DURATION = 3600  # 1 hour lockout
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_USE_USER_AGENT = True

# ============================================================================
# EMAIL SECURITY (Hostinger SMTP)
# ============================================================================

# Already configured in .env:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.hostinger.com
# EMAIL_PORT=465
# EMAIL_USE_SSL=True
# EMAIL_HOST_USER=support@packaxis.ca
# EMAIL_HOST_PASSWORD=<your_secure_password>

EMAIL_TIMEOUT = 10  # Timeout for email sending

# ============================================================================
# CORS & CSRF
# ============================================================================

CORS_ALLOWED_ORIGINS = [
    "https://packaxis.ca",
    "https://www.packaxis.ca",
]

CSRF_TRUSTED_ORIGINS = [
    "https://packaxis.ca",
    "https://www.packaxis.ca",
]

CSRF_FAILURE_VIEW = "frontend.views.csrf_failure"

# ============================================================================
# LOGGING - For security auditing
# ============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/security.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 10,
        },
    },
    "loggers": {
        "django.security": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
        "axes": {
            "handlers": ["file"],
            "level": "INFO",
        },
    },
}

# ============================================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================================

MIDDLEWARE = [
    # ... existing middleware ...
    "django.middleware.security.SecurityMiddleware",  # Should be first
    "whitenoise.middleware.WhiteNoiseMiddleware",      # For static files
    "axes.middleware.AxesMiddleware",                  # For brute force protection
]

# ============================================================================
# DJANGO-REST-FRAMEWORK SECURITY
# ============================================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        # Add JWT if using token auth:
        # "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

# Run before deploying to production:
# python manage.py check --deploy
# This will verify all security settings are in place

# Expected warnings to fix:
# - SECRET_KEY should be strong random string
# - DEBUG must be False
# - ALLOWED_HOSTS must include production domain
# - CSRF_COOKIE_SECURE must be True
# - SESSION_COOKIE_SECURE must be True
# - SECURE_SSL_REDIRECT must be True
# - SECURE_HSTS_SECONDS must be > 0

# ============================================================================
# SUMMARY OF CHANGES FROM DEVELOPMENT
# ============================================================================

"""
Development (DEFAULT):
- DEBUG = True
- SESSION_COOKIE_SECURE = False
- CSRF_COOKIE_SECURE = False
- EMAIL_VERIFICATION = "optional"
- AXES (rate limiting) = Not configured
- HTTPS = Not enforced

Production (REQUIRED):
- DEBUG = False
- SESSION_COOKIE_SECURE = True
- CSRF_COOKIE_SECURE = True
- SECURE_SSL_REDIRECT = True
- EMAIL_VERIFICATION = "mandatory"
- AXES = Configured (5 attempts, 1hr lockout)
- HSTS = Enabled
- X-Frame-Options = DENY
- CSP = Configured
- ALLOWED_HOSTS = Production domain only
- SECRET_KEY = Strong random 50+ character string
- Database = PostgreSQL (not SQLite)
- Static files = WhiteNoise or CDN
- Email = Production SMTP (not console backend)
- Logging = File-based audit logs
"""
