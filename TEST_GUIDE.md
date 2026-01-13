# Test-running guide for PackAxis authentication

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Running Tests

### Run all authentication tests:
```bash
pytest apps/accounts/tests -v
```

### Run specific test class:
```bash
pytest apps/accounts/tests/test_signup_login.py::TestSignupBasics -v
```

### Run single test:
```bash
pytest apps/accounts/tests/test_signup_login.py::TestSignupBasics::test_signup_success_b2c -v
```

### Run with coverage:
```bash
coverage run -m pytest apps/accounts/tests
coverage report
coverage html  # generates htmlcov/index.html
```

### Run only security tests:
```bash
pytest apps/accounts/tests/test_signup_login.py::TestSignupSecurity -v
```

### Run only edge cases:
```bash
pytest apps/accounts/tests/test_signup_login.py::TestEdgeCases -v
```

## Test Categories

### Signup Tests (12 tests)
- Valid B2C registration
- Email as username verification
- Missing/invalid email
- Duplicate email prevention
- Missing/mismatched passwords
- Weak/common/numeric password rejection
- Optional name fields
- Email verification flow

### Login Tests (11 tests)
- Successful login
- Wrong password/non-existent user
- Missing email/password
- Case-insensitive email
- Inactive user rejection
- Session creation
- Concurrent sessions

### Security Tests (4 signup + 2 login)
- SQL injection prevention
- XSS payload handling
- Unicode email handling
- Very long passwords
- Special characters in passwords
- CSRF protection
- Timing attack resistance
- User enumeration prevention

### Password Reset Tests (4 tests)
- Email sent on reset request
- Reset link in email
- Non-existent user handling
- Missing email validation

### Verification & Roles (4 tests)
- Optional vs mandatory verification
- B2B user creation
- Default B2C role

### Edge Cases (4 tests)
- Whitespace in email
- Deleted user login prevention
- Password change session invalidation

## Expected Test Results

All 41 tests should pass on the main branch:
```
PASSED: 41
FAILED: 0
ERRORS: 0
```

## Adding New Tests

Tests use pytest + factory_boy for fixtures:
- `UserFactory` - basic user
- `B2BUserFactory` - B2B company user
- `AdminUserFactory` - superuser

Example:
```python
@pytest.mark.django_db
def test_new_feature(client):
    user = UserFactory(password="TestPass123!")
    resp = client.post(reverse("account_login"), {
        "login": user.email,
        "password": "TestPass123!",
    })
    assert resp.status_code == 302
```

## Fixtures Used

- `client` - Django test client
- `mailbox` - Email outbox (from conftest.py)

## CI/CD Integration

Add to `.github/workflows/test.yml`:
```yaml
- name: Run tests
  run: pytest backend/apps/accounts/tests --cov=backend.apps.accounts
```

## Performance Notes

- All tests use in-memory SQLite (django_db)
- No network calls
- ~2-5 seconds total runtime
- Password hashing adds most time
