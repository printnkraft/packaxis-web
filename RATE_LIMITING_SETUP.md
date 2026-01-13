"""
Rate limiting and brute-force protection configuration.

Install django-axes:
    pip install django-axes

Add to settings.py INSTALLED_APPS (before auth):
    'axes',

Add to settings.py MIDDLEWARE:
    'axes.middleware.AxesMiddleware',

This provides:
- Account lockout after N failed login attempts
- IP-based and user-based tracking
- Automatic cooloff period
- Admin panel integration
"""

# Configuration (paste into settings.py or environment-based)

# django-axes configuration
AXES_FAILURE_LIMIT = 5                                    # Lock after 5 failed attempts
AXES_COOLOFF_DURATION = 3600                              # 1 hour lockout (3600 seconds)
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True          # Track by both user + IP
AXES_USE_USER_AGENT = True                                # Include user agent in tracking
AXES_DISABLE_ACCESS_FAILURE_LOG = False                   # Log failures
AXES_RESET_ON_SUCCESS = True                              # Reset counter on successful login

# Lockout message
AXES_LOCKOUT_TEMPLATE = "axes/lockout.html"               # Custom lockout page
AXES_VERBOSE = True                                       # Verbose logging

# Optional: Custom lockout handling
# AXES_LOCKOUT_HANDLER = "axes.handlers.database.AxesHandler"

"""
Access logs are stored in database (axes_accessattempt, axes_accesslog)

View failed attempts in Django admin:
- http://localhost:8000/admin/axes/accessattempt/
- http://localhost:8000/admin/axes/accesslog/

To reset failed attempts for a user:
    from axes.models import AccessAttempt
    AccessAttempt.objects.filter(username='user@example.com').delete()

To manually lock a user:
    from axes.models import AccessAttempt
    AccessAttempt.objects.create(
        attempt_time=timezone.now(),
        path='/accounts/login/',
        failures_since_start=5,
        failure_count=5,
        ip_address='192.168.1.1',
        user_agent='Mozilla/5.0...',
        username='user@example.com'
    )

Tests with axes:
    @pytest.mark.django_db
    def test_account_lockout_after_failed_attempts(client):
        user = UserFactory(password='StrongPass123!')
        
        # Make 5 failed login attempts
        for i in range(5):
            resp = client.post(reverse('account_login'), {
                'login': user.email,
                'password': 'WrongPass999!',
            })
            assert resp.status_code == 200
        
        # 6th attempt should be locked
        resp = client.post(reverse('account_login'), {
            'login': user.email,
            'password': 'StrongPass123!',  # Even correct password fails
        })
        assert resp.status_code == 429 or 'locked' in resp.content.decode().lower()

    @pytest.mark.django_db
    def test_account_unlock_after_cooloff_period(client):
        from axes.models import AccessAttempt
        from django.utils import timezone
        from datetime import timedelta
        
        user = UserFactory(password='StrongPass123!')
        
        # Lock the account
        AccessAttempt.objects.create(
            username=user.email,
            ip_address='127.0.0.1',
            failures_since_start=5,
            attempt_time=timezone.now() - timedelta(hours=2)  # 2 hours ago
        )
        
        # Should be unlocked now (cooloff passed)
        resp = client.post(reverse('account_login'), {
            'login': user.email,
            'password': 'StrongPass123!',
        })
        assert resp.status_code == 302  # Successful login redirect
"""

# Recommended email notification on lockout:
# pip install django-axes[email]

# Add to settings.py:
AXES_EMAIL_ON_ATTEMPT_FAILED = True
AXES_EMAIL_FAILURE_LIMIT = 3  # Email user after 3 failed attempts
AXES_EMAIL_ADMINS = True       # Email admins of lockout

AXES_EMAIL_TEMPLATE = "axes/email/failed_attempt.txt"
AXES_EMAIL_HTML_TEMPLATE = "axes/email/failed_attempt.html"

# Expected behavior:
# - After 1-2 failed attempts: User sees generic error message
# - After 3 failed attempts: User receives email alert
# - After 5 failed attempts: Account locked, user receives lockout notification
# - After cooloff period (1 hour): Account automatically unlocked
