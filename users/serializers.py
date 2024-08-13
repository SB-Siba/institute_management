from rest_framework import serializers


from users import models

class SignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = models.User
        fields = ['full_name', 'email', 'contact', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
            
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        
        if len(data['password']) < 6:
            raise serializers.ValidationError('Password Length is less than 6..')

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = models.User(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.save()
        return user
from django.contrib.auth import authenticate
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if user and user.is_active:
            data['user'] = user
        else:
            raise serializers.ValidationError('Invalid credentials or inactive account')
        return data
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        exclude = ["password"]



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not models.User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value