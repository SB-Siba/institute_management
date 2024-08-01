from rest_framework import serializers


from users import models

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            'full_name',
            'email',
            'contact',
            'password',

        ]

        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True},
            'contact': {'required': True},
            'password': {'required': True},
            }

    def validate(self, data):
        
        if len(data['password']) < 6:
            raise serializers.ValidationError('Password Length is less than 6..')


        return data
    
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