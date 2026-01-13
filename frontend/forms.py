"""
Checkout forms and validation
Packaxis Checkout System
"""

from django import forms
from django.core.validators import RegexValidator
import re

class CheckoutForm(forms.Form):
    """Main checkout form with all required fields and validation"""
    
    # Contact Information
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'John'
        })
    )
    
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'Doe'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'john@example.com'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': '(555) 123-4567',
            'type': 'tel'
        })
    )
    
    # Shipping Address
    street_address = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': '123 Main Street'
        })
    )
    
    street_address_2 = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'Apartment, suite, etc. (optional)'
        })
    )
    
    city = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'Toronto'
        })
    )
    
    PROVINCE_CHOICES = [
        ('', '-- Select Province --'),
        ('AB', 'Alberta'),
        ('BC', 'British Columbia'),
        ('MB', 'Manitoba'),
        ('NB', 'New Brunswick'),
        ('NL', 'Newfoundland and Labrador'),
        ('NS', 'Nova Scotia'),
        ('NT', 'Northwest Territories'),
        ('NU', 'Nunavut'),
        ('ON', 'Ontario'),
        ('PE', 'Prince Edward Island'),
        ('QC', 'Quebec'),
        ('SK', 'Saskatchewan'),
        ('YT', 'Yukon'),
    ]
    
    province = forms.ChoiceField(
        choices=PROVINCE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
        })
    )
    
    postal_code = forms.CharField(
        max_length=7,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$',
                message='Invalid postal code. Please use format: A1A 1A1',
                code='invalid_postal_code'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'M5V 3A8',
            'maxlength': '7',
            'style': 'text-transform: uppercase;'
        })
    )
    
    # Shipping Method
    SHIPPING_CHOICES = [
        ('economy', 'Economy (5-7 days) - $5.00'),
        ('express', 'Express (2-3 days) - $15.00'),
        ('overnight', 'Overnight (1 day) - $25.00'),
    ]
    
    shipping_method = forms.ChoiceField(
        choices=SHIPPING_CHOICES,
        required=True,
        initial='economy',
        widget=forms.RadioSelect(attrs={
            'class': 'w-4 h-4'
        })
    )
    
    # Payment Information
    PAYMENT_CHOICES = [
        ('card', 'Credit or Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        required=True,
        initial='card',
        widget=forms.RadioSelect()
    )
    
    # Card Information (shown conditionally with JS)
    card_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'Cardholder Name'
        })
    )
    
    card_number = forms.CharField(
        max_length=19,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': '1234 5678 9012 3456',
            'inputmode': 'numeric'
        })
    )
    
    card_expiry = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'MM/YY',
            'inputmode': 'numeric'
        })
    )
    
    card_cvv = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': '123',
            'inputmode': 'numeric'
        })
    )
    
    # Coupon
    coupon_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'Enter coupon code (optional)',
            'style': 'text-transform: uppercase;'
        })
    )
    
    # Terms and Conditions
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 rounded'
        })
    )
    
    def clean_postal_code(self):
        """Validate postal code format and extract province"""
        postal_code = self.cleaned_data.get('postal_code')
        
        if not postal_code:
            return postal_code
        
        # Remove spaces and convert to uppercase
        postal_code = postal_code.replace(' ', '').upper()
        
        # Validate format
        import re
        if not re.match(r'^[A-Z]\d[A-Z]\d[A-Z]\d$', postal_code):
            raise forms.ValidationError(
                'Invalid postal code format. Please use: A1A 1A1'
            )
        
        return postal_code
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        
        if not phone:
            return phone
        
        # Remove common formatting characters
        cleaned = ''.join(filter(str.isdigit, phone))
        
        if len(cleaned) < 10:
            raise forms.ValidationError(
                'Please enter a valid phone number (at least 10 digits)'
            )
        
        return phone
    
    def clean(self):
        """Overall form validation"""
        cleaned_data = super().clean()
        
        # Check card details if card payment selected
        payment_method = cleaned_data.get('payment_method')
        if payment_method == 'card':
            card_name = cleaned_data.get('card_name')
            card_number = cleaned_data.get('card_number')
            card_expiry = cleaned_data.get('card_expiry')
            card_cvv = cleaned_data.get('card_cvv')
            
            if not all([card_name, card_number, card_expiry, card_cvv]):
                raise forms.ValidationError(
                    'Please enter complete card information'
                )
            
            # Validate card number (basic Luhn check)
            if not self._validate_card_number(card_number):
                raise forms.ValidationError(
                    'Invalid card number'
                )
        
        return cleaned_data
    
    @staticmethod
    def _validate_card_number(card_number):
        """Basic Luhn algorithm for card validation"""
        # Remove spaces
        card_number = card_number.replace(' ', '')
        
        # Check if numeric
        if not card_number.isdigit():
            return False
        
        # Check length (13-19 digits)
        if not (13 <= len(card_number) <= 19):
            return False
        
        return True


class CouponForm(forms.Form):
    """Form for coupon validation"""
    coupon_code = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'style': 'text-transform: uppercase;'
        })
    )
