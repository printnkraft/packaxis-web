from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Roles(models.TextChoices):
        B2C = "B2C", _("B2C")
        B2B = "B2B", _("B2B")
        ADMIN = "ADMIN", _("Admin")

    username = None
    email = models.EmailField(unique=True)
    google_oauth_id = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.B2C)
    company_name = models.CharField(max_length=255, blank=True)
    tax_id = models.CharField(max_length=30, blank=True, validators=[RegexValidator(r"^[A-Za-z0-9\-]+$")])
    is_verified = models.BooleanField(default=False)
    preferences = models.JSONField(default=dict, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Address(models.Model):
    """User-saved addresses for checkout (separate from order snapshot)."""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='addresses')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=255, blank=True)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=2, default="CA")
    phone = models.CharField(max_length=20, blank=True)

    is_default_shipping = models.BooleanField(default=False)
    is_default_billing = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default_shipping', '-is_default_billing', '-updated_at']

    def __str__(self):
        return f"{self.address1}, {self.city} {self.province} {self.postal_code}"
