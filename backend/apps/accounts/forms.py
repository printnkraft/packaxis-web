from allauth.account.forms import SignupForm, LoginForm
from django import forms


class CustomSignupForm(SignupForm):
    """Signup form without username, capturing first/last name."""

    first_name = forms.CharField(max_length=30, required=False, label="First name")
    last_name = forms.CharField(max_length=30, required=False, label="Last name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field if present (our User model is email-only)
        self.fields.pop("username", None)
        # Make email the primary login label
        if "email" in self.fields:
            self.fields["email"].label = "Email"

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.save()
        return user


class CustomLoginForm(LoginForm):
    """Login form without username field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username if it exists; allauth may include it by default
        self.fields.pop("username", None)
        if "login" in self.fields:
            self.fields["login"].label = "Email"