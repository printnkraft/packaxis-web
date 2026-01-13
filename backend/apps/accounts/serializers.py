from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Address


class UserSerializer(serializers.ModelSerializer):
    """User profile and authentication response."""
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "company_name",
            "tax_id",
            "is_verified",
            "preferences",
        ]
        read_only_fields = ["id", "is_verified", "role"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration with email and password validation."""
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "role",
            "company_name",
            "tax_id",
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'company_name': {'required': False},
            'tax_id': {'required': False},
        }
    
    def validate(self, data):
        """Validate password match and email uniqueness."""
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered'})
        
        # Validate B2B requirements
        if data.get('role') == 'B2B':
            if not data.get('company_name'):
                raise serializers.ValidationError({'company_name': 'Company name required for B2B accounts'})
            if not data.get('tax_id'):
                raise serializers.ValidationError({'tax_id': 'Tax ID required for B2B accounts'})
        
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """User login with email and password."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        """Authenticate user."""
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password')
        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile update with company and preference management."""
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "company_name",
            "tax_id",
            "role",
            "is_verified",
            "preferences",
        ]
        read_only_fields = ["id", "email", "role", "is_verified"]


class ChangePasswordSerializer(serializers.Serializer):
    """Password change validation."""
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    
    def validate(self, data):
        """Validate password requirements."""
        if data['new_password'] != data.pop('new_password_confirm'):
            raise serializers.ValidationError({'new_password': 'Passwords do not match'})
        return data


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for user addresses with default flag management."""
    class Meta:
        model = Address
        fields = [
            'id', 'first_name', 'last_name', 'company', 'address1', 'address2',
            'city', 'province', 'postal_code', 'country', 'phone',
            'is_default_shipping', 'is_default_billing', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        addr = Address.objects.create(user=user, **validated_data)
        # Ensure single default flags
        if addr.is_default_shipping:
            Address.objects.filter(user=user, is_default_shipping=True).exclude(id=addr.id).update(is_default_shipping=False)
        if addr.is_default_billing:
            Address.objects.filter(user=user, is_default_billing=True).exclude(id=addr.id).update(is_default_billing=False)
        return addr

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        user = self.context['request'].user
        if instance.is_default_shipping:
            Address.objects.filter(user=user, is_default_shipping=True).exclude(id=instance.id).update(is_default_shipping=False)
        if instance.is_default_billing:
            Address.objects.filter(user=user, is_default_billing=True).exclude(id=instance.id).update(is_default_billing=False)
        return instance
