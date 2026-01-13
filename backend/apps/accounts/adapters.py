from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom adapter to handle username-less authentication."""
    
    def populate_username(self, request, user):
        """
        Override to prevent username generation since our User model
        uses email as the identifier and has username=None.
        """
        # Do nothing - we don't use usernames
        pass
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user with email as the primary identifier.
        """
        user = super().save_user(request, user, form, commit=False)
        # Ensure email is persisted and mapped to username (we are email-only)
        email = form.cleaned_data.get("email")
        user.email = email
        user.username = email
        if commit:
            user.save()
        return user
