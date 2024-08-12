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
    
class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            'email',
            'password',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True},
        }
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        exclude = ["password"]



class ForgotPasswordSerializer(serializers.Serializer):

    contact = serializers.CharField(max_length = 10, required =True)
    
class NewPasswordSerializer(serializers.Serializer):

    password1 = serializers.CharField(max_length = 255, required =True)
    password2 = serializers.CharField(max_length = 255, required =True)

    def validate(self, data):
        # Check if the passwords match
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("The passwords do not match.")
        
        if len(data['password1']) < 6:
            raise serializers.ValidationError("Your Password is very weak")
        
        return data