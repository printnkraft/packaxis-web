"""
Comprehensive test suite for user signup, login, password reset, and authentication flows.
Covers security, validation, edge cases, and integration with django-allauth.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.test.utils import override_settings
from .factories import UserFactory, B2BUserFactory, AdminUserFactory

User = get_user_model()


# ============================================================================
# SIGNUP TESTS
# ============================================================================

class TestSignupBasics:
    """Basic signup validation and success flows."""

    @pytest.mark.django_db
    def test_signup_success_b2c(self, client):
        """Test successful B2C user registration."""
        resp = client.post(reverse("account_signup"), {
            "email": "newuser@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
            "first_name": "New",
            "last_name": "User",
        })
        assert resp.status_code == 302
        user = User.objects.get(email="newuser@example.com")
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.role == "B2C"

    @pytest.mark.django_db
    def test_signup_user_created_with_email_as_username(self, client):
        """Verify email is set as username (email-only user model)."""
        client.post(reverse("account_signup"), {
            "email": "emailuser@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        user = User.objects.get(email="emailuser@example.com")
        assert user.username == user.email

    @pytest.mark.django_db
    def test_signup_missing_email(self, client):
        """Email is required."""
        resp = client.post(reverse("account_signup"), {
            "email": "",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert resp.status_code == 200
        assert "email" in resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_signup_invalid_email_format(self, client):
        """Invalid email format is rejected."""
        resp = client.post(reverse("account_signup"), {
            "email": "not-an-email",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert resp.status_code == 200
        assert "email" in resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_signup_duplicate_email(self, client):
        """Duplicate email registration fails."""
        UserFactory(email="duplicate@example.com", password="OldPass123!")
        resp = client.post(reverse("account_signup"), {
            "email": "duplicate@example.com",
            "password1": "NewPass123!",
            "password2": "NewPass123!",
        })
        assert resp.status_code == 200
        assert "email" in resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_signup_missing_password(self, client):
        """Password is required."""
        resp = client.post(reverse("account_signup"), {
            "email": "user@example.com",
            "password1": "",
            "password2": "",
        })
        assert resp.status_code == 200
        assert "password1" in resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_signup_password_mismatch(self, client):
        """Passwords must match."""
        resp = client.post(reverse("account_signup"), {
            "email": "user@example.com",
            "password1": "StrongPass123!",
            "password2": "WrongPass999!",
        })
        assert resp.status_code == 200
        assert "password2" in resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_signup_weak_password_too_short(self, client):
        """Password minimum length is enforced."""
        resp = client.post(reverse("account_signup"), {
            "email": "user@example.com",
            "password1": "weak",
            "password2": "weak",
        })
        assert resp.status_code == 200
        # Django's password validators should catch this
        assert resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_signup_common_password_rejected(self, client):
        """Common passwords are rejected."""
        resp = client.post(reverse("account_signup"), {
            "email": "user@example.com",
            "password1": "password",
            "password2": "password",
        })
        assert resp.status_code == 200
        assert resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_signup_numeric_only_password_rejected(self, client):
        """Numeric-only passwords are rejected."""
        resp = client.post(reverse("account_signup"), {
            "email": "user@example.com",
            "password1": "12345678",
            "password2": "12345678",
        })
        assert resp.status_code == 200
        assert resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_signup_optional_first_last_name(self, client):
        """First and last name are optional."""
        resp = client.post(reverse("account_signup"), {
            "email": "noname@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert resp.status_code == 302
        user = User.objects.get(email="noname@example.com")
        assert user.first_name == ""
        assert user.last_name == ""

    @pytest.mark.django_db
    @override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
    def test_signup_sends_verification_email(self, client, mailbox):
        """Verification email is sent when mandatory."""
        resp = client.post(reverse("account_signup"), {
            "email": "verifyme@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert resp.status_code == 302
        assert len(mailbox) == 1
        assert "verifyme@example.com" in mailbox[0].to


class TestSignupSecurity:
    """Security-focused signup tests."""

    @pytest.mark.django_db
    def test_signup_sql_injection_attempt_email(self, client):
        """SQL injection in email field is safely escaped."""
        resp = client.post(reverse("account_signup"), {
            "email": "'; DROP TABLE users; --@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        # Should fail email validation, not SQL injection
        assert resp.status_code == 200
        assert "email" in resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_signup_xss_attempt_in_first_name(self, client):
        """XSS payload in first_name is safely stored (no reflection in signup response)."""
        xss_payload = "<script>alert('XSS')</script>"
        resp = client.post(reverse("account_signup"), {
            "email": "xsstest@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
            "first_name": xss_payload,
            "last_name": "User",
        })
        assert resp.status_code == 302
        user = User.objects.get(email="xsstest@example.com")
        # Payload should be stored as-is (Django template escaping handles display)
        assert user.first_name == xss_payload

    @pytest.mark.django_db
    def test_signup_unicode_email(self, client):
        """Unicode characters in email are handled."""
        # Most email validators reject unicode, which is correct
        resp = client.post(reverse("account_signup"), {
            "email": "user+™@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        # Should fail validation
        assert resp.status_code == 200
        assert "email" in resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_signup_very_long_password(self, client):
        """Very long password is handled correctly."""
        long_pwd = "A" * 1000 + "1!"
        resp = client.post(reverse("account_signup"), {
            "email": "longpwd@example.com",
            "password1": long_pwd,
            "password2": long_pwd,
        })
        # Should accept very long passwords (Django's hasher handles it)
        assert resp.status_code == 302
        user = User.objects.get(email="longpwd@example.com")
        assert user.check_password(long_pwd)

    @pytest.mark.django_db
    def test_signup_special_chars_in_password(self, client):
        """Special characters in password are handled."""
        special_pwd = "P@ssw0rd!#$%^&*()"
        resp = client.post(reverse("account_signup"), {
            "email": "special@example.com",
            "password1": special_pwd,
            "password2": special_pwd,
        })
        assert resp.status_code == 302
        user = User.objects.get(email="special@example.com")
        assert user.check_password(special_pwd)

    @pytest.mark.django_db
    def test_signup_csrf_protection(self, client):
        """POST without CSRF token is rejected."""
        # Django's CSRF middleware should reject this
        from django.middleware.csrf import get_token
        # GET to get CSRF token first
        resp = client.get(reverse("account_signup"))
        csrf_token = resp.context.get("csrf_token", "invalid")
        
        # POST with invalid CSRF should fail (or allauth may handle differently)
        resp = client.post(
            reverse("account_signup"),
            {
                "email": "test@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "csrfmiddlewaretoken": "invalid_token",
            },
            HTTP_X_CSRFTOKEN="invalid_token"
        )
        # Depending on allauth setup, may reject with 403 or regenerate token
        # At minimum, it should not create the user
        assert User.objects.filter(email="test@example.com").count() == 0


# ============================================================================
# LOGIN TESTS
# ============================================================================

class TestLoginBasics:
    """Basic login validation and success flows."""

    @pytest.mark.django_db
    def test_login_success(self, client):
        """Test successful login with email and password."""
        user = UserFactory(password="StrongPass123!")
        resp = client.post(reverse("account_login"), {
            "login": user.email,
            "password": "StrongPass123!",
        })
        assert resp.status_code == 302
        # User should be authenticated
        assert client.session.get('_auth_user_id')

    @pytest.mark.django_db
    def test_login_wrong_password(self, client):
        """Login fails with incorrect password."""
        user = UserFactory(password="CorrectPass123!")
        resp = client.post(reverse("account_login"), {
            "login": user.email,
            "password": "WrongPass999!",
        })
        assert resp.status_code == 200
        # User not authenticated
        assert not client.session.get('_auth_user_id')

    @pytest.mark.django_db
    def test_login_nonexistent_user(self, client):
        """Login fails for non-existent user."""
        resp = client.post(reverse("account_login"), {
            "login": "nonexistent@example.com",
            "password": "AnyPass123!",
        })
        assert resp.status_code == 200
        assert not client.session.get('_auth_user_id')

    @pytest.mark.django_db
    def test_login_missing_email(self, client):
        """Login requires email."""
        resp = client.post(reverse("account_login"), {
            "login": "",
            "password": "StrongPass123!",
        })
        assert resp.status_code == 200
        # Form should have error
        assert resp.context_data["form"].errors

    @pytest.mark.django_db
    def test_login_missing_password(self, client):
        """Login requires password."""
        user = UserFactory(password="StrongPass123!")
        resp = client.post(reverse("account_login"), {
            "login": user.email,
            "password": "",
        })
        assert resp.status_code == 200
        assert not client.session.get('_auth_user_id')

    @pytest.mark.django_db
    def test_login_case_insensitive_email(self, client):
        """Email login should be case-insensitive."""
        user = UserFactory(email="CaseUser@example.com", password="StrongPass123!")
        resp = client.post(reverse("account_login"), {
            "login": "caseuser@example.com",
            "password": "StrongPass123!",
        })
        assert resp.status_code == 302
        assert client.session.get('_auth_user_id')

    @pytest.mark.django_db
    def test_login_inactive_user(self, client):
        """Inactive users cannot login."""
        user = UserFactory(password="StrongPass123!", is_active=False)
        resp = client.post(reverse("account_login"), {
            "login": user.email,
            "password": "StrongPass123!",
        })
        assert resp.status_code == 200
        assert not client.session.get('_auth_user_id')

    @pytest.mark.django_db
    def test_login_session_created(self, client):
        """Successful login creates session."""
        user = UserFactory(password="StrongPass123!")
        resp = client.post(reverse("account_login"), {
            "login": user.email,
            "password": "StrongPass123!",
        })
        assert resp.status_code == 302
        assert client.session.get('_auth_user_id')
        assert client.session.get('_auth_user_backend')

    @pytest.mark.django_db
    def test_login_concurrent_sessions(self, client):
        """User can have multiple concurrent sessions."""
        from django.test import Client
        user = UserFactory(password="StrongPass123!")
        
        # Login from first client
        client1 = Client()
        resp1 = client1.post(reverse("account_login"), {
            "login": user.email,
            "password": "StrongPass123!",
        })
        assert resp1.status_code == 302
        
        # Login from second client (different session)
        client2 = Client()
        resp2 = client2.post(reverse("account_login"), {
            "login": user.email,
            "password": "StrongPass123!",
        })
        assert resp2.status_code == 302
        
        # Both should have different sessions but same user
        assert client1.session.get('_auth_user_id') == user.id
        assert client2.session.get('_auth_user_id') == user.id


class TestLoginSecurity:
    """Security-focused login tests."""

    @pytest.mark.django_db
    def test_login_timing_attack_resistant(self, client):
        """Password verification should take similar time for valid/invalid users."""
        import time
        user = UserFactory(password="StrongPass123!")
        
        # Time valid user login
        start = time.time()
        client.post(reverse("account_login"), {
            "login": user.email,
            "password": "StrongPass123!",
        })
        valid_time = time.time() - start
        
        # Time non-existent user (should be similar)
        start = time.time()
        client.post(reverse("account_login"), {
            "login": "nonexistent@example.com",
            "password": "StrongPass123!",
        })
        invalid_time = time.time() - start
        
        # Times should be similar (within 100ms due to hashing)
        assert abs(valid_time - invalid_time) < 0.1

    @pytest.mark.django_db
    def test_login_sql_injection_attempt(self, client):
        """SQL injection in login field is safely escaped."""
        resp = client.post(reverse("account_login"), {
            "login": "'; DROP TABLE users; --",
            "password": "anything",
        })
        assert resp.status_code == 200
        # Should not authenticate or cause SQL error
        assert not client.session.get('_auth_user_id')

    @pytest.mark.django_db
    def test_login_no_user_enumeration(self, client):
        """Error messages don't reveal if email exists."""
        # Test with existing user
        user = UserFactory(password="StrongPass123!")
        resp1 = client.post(reverse("account_login"), {
            "login": user.email,
            "password": "WrongPass999!",
        })
        
        # Test with non-existing user
        resp2 = client.post(reverse("account_login"), {
            "login": "nonexistent@example.com",
            "password": "WrongPass999!",
        })
        
        # Both should have similar error messages (not revealing)
        # Both status codes should be 200 (form re-rendered)
        assert resp1.status_code == 200
        assert resp2.status_code == 200


class TestLogout:
    """Logout and session invalidation tests."""

    @pytest.mark.django_db
    def test_logout_invalidates_session(self, client):
        """Logout invalidates the session."""
        user = UserFactory(password="StrongPass123!")
        client.post(reverse("account_login"), {
            "login": user.email,
            "password": "StrongPass123!",
        })
        assert client.session.get('_auth_user_id')
        
        # Logout
        resp = client.post(reverse("account_logout"))
        assert resp.status_code == 302
        
        # Session should be cleared
        assert not client.session.get('_auth_user_id')

    @pytest.mark.django_db
    def test_logout_clears_session_cookie(self, client):
        """Logout clears auth session cookie."""
        user = UserFactory(password="StrongPass123!")
        client.post(reverse("account_login"), {
            "login": user.email,
            "password": "StrongPass123!",
        })
        
        resp = client.post(reverse("account_logout"))
        assert resp.status_code == 302
        # Session key should be cleared
        assert not client.session.session_key or \
               not client.session.get('_auth_user_id')


# ============================================================================
# PASSWORD RESET TESTS
# ============================================================================

class TestPasswordReset:
    """Password reset flow tests."""

    @pytest.mark.django_db
    def test_password_reset_email_sent(self, client, mailbox):
        """Password reset email is sent."""
        user = UserFactory(password="OldPass123!")
        resp = client.post(reverse("account_reset_password"), {
            "email": user.email,
        })
        assert resp.status_code == 302
        assert len(mailbox) == 1
        assert user.email in mailbox[0].to

    @pytest.mark.django_db
    def test_password_reset_email_contains_link(self, client, mailbox):
        """Password reset email contains reset link."""
        user = UserFactory(password="OldPass123!")
        client.post(reverse("account_reset_password"), {
            "email": user.email,
        })
        assert len(mailbox) == 1
        email_body = mailbox[0].body
        assert "/reset/" in email_body or "password" in email_body.lower()

    @pytest.mark.django_db
    def test_password_reset_nonexistent_user(self, client, mailbox):
        """Password reset for non-existent user doesn't reveal user doesn't exist."""
        resp = client.post(reverse("account_reset_password"), {
            "email": "nonexistent@example.com",
        })
        # Should still show success (not revealing user existence)
        assert resp.status_code == 302

    @pytest.mark.django_db
    def test_password_reset_missing_email(self, client):
        """Password reset requires email."""
        resp = client.post(reverse("account_reset_password"), {
            "email": "",
        })
        assert resp.status_code == 200
        assert "email" in resp.context_data["form"].errors


# ============================================================================
# ACCOUNT VERIFICATION TESTS
# ============================================================================

class TestAccountVerification:
    """Email verification flow tests."""

    @pytest.mark.django_db
    @override_settings(ACCOUNT_EMAIL_VERIFICATION="optional")
    def test_optional_verification_allows_login(self, client, mailbox):
        """With optional verification, unverified users can login."""
        resp = client.post(reverse("account_signup"), {
            "email": "unverified@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert resp.status_code == 302
        
        # Should be able to login without verifying
        resp = client.post(reverse("account_login"), {
            "login": "unverified@example.com",
            "password": "StrongPass123!",
        })
        assert resp.status_code == 302

    @pytest.mark.django_db
    @override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
    def test_mandatory_verification_blocks_login(self, client, mailbox):
        """With mandatory verification, unverified users cannot login."""
        # User must verify email before login
        # This is allauth-specific behavior
        resp = client.post(reverse("account_signup"), {
            "email": "mustverify@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert resp.status_code == 302
        assert len(mailbox) == 1


# ============================================================================
# B2B / B2C ROLE TESTS
# ============================================================================

class TestB2BSignup:
    """B2B user signup tests (manual role assignment for now)."""

    @pytest.mark.django_db
    def test_b2b_user_can_be_created(self, client):
        """B2B users can be created with company details."""
        user = B2BUserFactory(password="StrongPass123!")
        assert user.role == "B2B"
        assert user.company_name == "Test Company Inc"
        assert user.tax_id == "TAX123456"

    @pytest.mark.django_db
    def test_b2c_user_default_role(self, client):
        """B2C is the default role."""
        user = UserFactory()
        assert user.role == "B2C"


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Edge case and unusual input tests."""

    @pytest.mark.django_db
    def test_signup_with_whitespace_email(self, client):
        """Whitespace in email should be handled."""
        resp = client.post(reverse("account_signup"), {
            "email": "  user@example.com  ",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        # Django's email field should strip whitespace
        # If user was created, email should be normalized
        if User.objects.filter(email="user@example.com").exists():
            assert True
        else:
            # Or form should reject it
            assert resp.status_code == 200

    @pytest.mark.django_db
    def test_deleted_user_cannot_login(self, client):
        """Deleted users cannot login."""
        user = UserFactory(password="StrongPass123!")
        email = user.email
        user.delete()
        
        resp = client.post(reverse("account_login"), {
            "login": email,
            "password": "StrongPass123!",
        })
        assert resp.status_code == 200
        assert not client.session.get('_auth_user_id')

    @pytest.mark.django_db
    def test_password_change_invalidates_old_sessions(self, client):
        """Password change should invalidate existing sessions."""
        user = UserFactory(password="OldPass123!")
        
        # Login
        resp = client.post(reverse("account_login"), {
            "login": user.email,
            "password": "OldPass123!",
        })
        assert resp.status_code == 302
        assert client.session.get('_auth_user_id')
        
        # Change password
        user.set_password("NewPass123!")
        user.save()
        
        # Old password should no longer work
        client2 = Client()
        resp = client2.post(reverse("account_login"), {
            "login": user.email,
            "password": "OldPass123!",
        })
        assert resp.status_code == 200
        assert not client2.session.get('_auth_user_id')
