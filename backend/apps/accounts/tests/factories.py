import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = "Test"
    last_name = "User"
    role = "B2C"
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after user creation."""
        pwd = extracted or "StrongPass123!"
        obj.set_password(pwd)
        if create:
            obj.save()


class B2BUserFactory(UserFactory):
    """Factory for creating B2B test users."""

    role = "B2B"
    company_name = "Test Company Inc"
    tax_id = "TAX123456"


class AdminUserFactory(UserFactory):
    """Factory for creating admin test users."""

    is_staff = True
    is_superuser = True
    role = "ADMIN"
