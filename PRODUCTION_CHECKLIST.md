# Production Deployment Security Checklist

## Pre-Deployment

### 1. Environment Variables
- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` - Strong random 50+ character string (not in version control)
- [ ] `ALLOWED_HOSTS` - Set to production domain(s) only
- [ ] `EMAIL_BACKEND` - SMTP (not console)
- [ ] `EMAIL_HOST_PASSWORD` - Securely stored in `.env` (not in code)
- [ ] `DATABASE_URL` - PostgreSQL connection (not SQLite)

### 2. Security Settings
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SECURE_HSTS_SECONDS = 31536000` (1 year)
- [ ] `SESSION_COOKIE_HTTPONLY = True`
- [ ] `SESSION_COOKIE_SAMESITE = "Lax"`
- [ ] `X_FRAME_OPTIONS = "DENY"`
- [ ] Content Security Policy headers configured

### 3. Authentication
- [ ] `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`
- [ ] Custom account adapter enabled (`ACCOUNT_ADAPTER = "apps.accounts.adapters.CustomAccountAdapter"`)
- [ ] django-axes installed for rate limiting
- [ ] `AXES_FAILURE_LIMIT = 5`
- [ ] `AXES_COOLOFF_DURATION = 3600` (1 hour)

### 4. Database
- [ ] Migrate to PostgreSQL (not SQLite)
- [ ] Run `python manage.py migrate`
- [ ] Create superuser with strong password
- [ ] Enable database backups
- [ ] Test backup/restore process

### 5. Static Files & Media
- [ ] Collect static files: `python manage.py collectstatic --no-input`
- [ ] Configure static files serving (WhiteNoise or CDN)
- [ ] Set up media files storage
- [ ] Enable gzip compression
- [ ] Consider CloudFlare or CDN for caching

### 6. Email Configuration
- [ ] Hostinger SMTP credentials secure
- [ ] Test email sending: `python manage.py shell < test_email.py`
- [ ] Verify SPF/DKIM records for domain
- [ ] Test password reset email flow
- [ ] Test order confirmation emails

### 7. Logging & Monitoring
- [ ] Set up log aggregation (Sentry recommended)
- [ ] Configure security logging (see SECURITY_HARDENING.md)
- [ ] Set up error email alerts for admins
- [ ] Enable audit logging for admin actions
- [ ] Monitor failed login attempts (via django-axes admin)

### 8. SSL/TLS Certificate
- [ ] Obtain SSL certificate (Let's Encrypt recommended)
- [ ] Configure HTTPS (port 443)
- [ ] Redirect HTTP to HTTPS
- [ ] Set certificate auto-renewal
- [ ] Test SSL with SSL Labs

### 9. Testing
- [ ] Run full test suite: `pytest backend/apps/accounts/tests -v`
- [ ] All 41 authentication tests pass
- [ ] Load testing with realistic user volume
- [ ] Security scanning:
  - [ ] `python manage.py check --deploy`
  - [ ] `bandit -r backend/`
  - [ ] `pip-audit`
  - [ ] OWASP Top 10 review

### 10. Deployment Infrastructure
- [ ] Web server configured (Gunicorn + Nginx recommended)
- [ ] Process manager (systemd or supervisor)
- [ ] Reverse proxy (Nginx) properly configured
- [ ] Load balancer (if multiple servers)
- [ ] Auto-scaling configured (if cloud-hosted)

### 11. Backup & Disaster Recovery
- [ ] Daily database backups
- [ ] Weekly full system backups
- [ ] Test backup restoration
- [ ] Disaster recovery plan documented
- [ ] Recovery Time Objective (RTO) defined
- [ ] Recovery Point Objective (RPO) defined

### 12. Monitoring & Alerts
- [ ] CPU/Memory monitoring
- [ ] Disk space alerts
- [ ] Database connection monitoring
- [ ] Failed login attempt alerts
- [ ] Error rate monitoring
- [ ] Uptime monitoring (external)
- [ ] Daily health checks

### 13. Access Control
- [ ] Admin panel restricted by IP (if possible)
- [ ] SSH key-based authentication (no passwords)
- [ ] VPN access for team
- [ ] Principle of least privilege
- [ ] Regular access audits

### 14. Third-Party Integrations
- [ ] Payment gateway (Stripe) configured securely
- [ ] API keys stored in environment variables
- [ ] API rate limiting configured
- [ ] Webhook signatures validated

## Post-Deployment

### Week 1
- [ ] Monitor error logs daily
- [ ] Check performance metrics
- [ ] Verify email delivery
- [ ] Test all user flows (signup, login, checkout, password reset)
- [ ] Monitor failed login attempts

### Week 2-4
- [ ] Review security logs
- [ ] Analyze performance data
- [ ] Check backup integrity
- [ ] Plan optimizations based on metrics

### Monthly
- [ ] Security patch updates
- [ ] Dependency updates (`pip-audit`)
- [ ] Penetration testing plan
- [ ] Review access logs
- [ ] Password rotation for service accounts

### Quarterly
- [ ] Security audit
- [ ] Compliance review (GDPR, PCI-DSS if handling payments)
- [ ] Disaster recovery drill
- [ ] Architecture review

## Security Incident Response

### If Breach Detected
1. [ ] Immediately notify security team
2. [ ] Isolate affected systems
3. [ ] Preserve logs and evidence
4. [ ] Notify affected users (within required timeframe)
5. [ ] Contact legal/compliance team
6. [ ] Post-incident analysis and prevention

### Failed Login Attacks
1. [ ] Monitor django-axes lockout events
2. [ ] Increase `AXES_FAILURE_LIMIT` temporarily if false positives
3. [ ] Implement CAPTCHA if attacks continue
4. [ ] Consider IP blocking at firewall level

### Email Compromise
1. [ ] Reset all passwords in email account
2. [ ] Review SMTP settings
3. [ ] Check email logs for unauthorized sends
4. [ ] Notify affected users if leaked
5. [ ] Reset application email credentials

## Useful Commands

```bash
# Check deployment security
python manage.py check --deploy

# Run security tests
pytest backend/apps/accounts/tests -v

# Security scanning
bandit -r backend/
pip-audit
safety check

# Collect static files
python manage.py collectstatic --no-input

# Create superuser
python manage.py createsuperuser

# Check database migrations
python manage.py showmigrations

# Test email configuration
python manage.py shell -c "from django.core.mail import send_mail; send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])"

# View failed login attempts
python manage.py shell
>>> from axes.models import AccessAttempt
>>> AccessAttempt.objects.filter(failures_since_start__gte=3)
```

## Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Security Headers](https://securityheaders.com/)
- [SSL Configuration](https://ssl-config.mozilla.org/)
- [django-axes Documentation](https://django-axes.readthedocs.io/)
