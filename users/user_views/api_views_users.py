import email
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View

from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema

from django.contrib import messages
from rest_framework.parsers import FormParser, MultiPartParser

from drf_yasg import openapi
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.permissions import IsAuthenticated        
# -------------------------------------------- custom import
from helpers import swagger_documentation
from helpers import utils, api_permission
from users import models

from users import serializers
from users import tasks
from users.forms import UpdateProfileForm
from users.user_views.emails import send_template_email

class RegistrationApi(APIView):
    serializer_class = serializers.SignupSerializer
    parser_classes = [FormParser, MultiPartParser]
    @swagger_auto_schema(
        tags=["authentication"],
        operation_description="signup API",
        manual_parameters=swagger_documentation.signup_post,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            contact = serializer.validated_data.get('contact')
            full_name = serializer.validated_data.get('full_name')

            try:
                # Create a new user
                new_user = models.User(email=email, full_name=full_name, contact=contact)
                new_user.set_password(password)
                new_user.save()

                # Authenticate the new user
                user_login = authenticate(email=email, password=password)
                if user_login is not None:
                    login(request, user_login)

                    # Send confirmation email (you might need to adjust this part)
                    context = {
                        'full_name': full_name,
                        'email': email,
                    }
                    send_template_email(
                        subject='Registration Confirmation',
                        template_name='users/email/register_email.html',
                        context=context,
                        recipient_list=[email]
                    )

                    return Response(
                        {"message": "Registration successful! You are now logged in."},
                        status=status.HTTP_201_CREATED
                    )
                else:
                    return Response(
                        {"error": "Authentication failed. Please try again."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                print(e)
                return Response(
                    {"error": "Something went wrong while registering your account. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginApi(APIView):
    serializer_class = serializers.LoginSerializer
    parser_classes = [FormParser, MultiPartParser]
    @swagger_auto_schema(
            tags=["authentication"],
            operation_description="Login API",
            manual_parameters=swagger_documentation.login_post,
            responses={
                200: openapi.Response('Login successful'),
                400: openapi.Response('Validation error'),
                401: openapi.Response('Login failed / You are not approved yet'),
            }
        )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        "message": "Login successful",
                        "token": token.key
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutApi(APIView):
    permission_classes = [IsAuthenticated]  # Ensure that only authenticated users can access this view
    parser_classes = [FormParser, MultiPartParser]

    @swagger_auto_schema(
        tags=["authentication"],
        operation_description="Logout API",
        manual_parameters=swagger_documentation.logout_get,
        responses={
            200: openapi.Response('Logout successful'),
            400: openapi.Response('Logout cancelled'),
            401: openapi.Response('Unauthorized'),
        }
    )
    def get(self, request, *args, **kwargs):
        # The IsAuthenticated permission class should prevent this,
        # but we add an extra check to be safe.
        if not request.user.is_authenticated:  
            return Response({
                "status": 401,
                "message": "Unauthorized"
            }, status=status.HTTP_401_UNAUTHORIZED)

        confirm = request.query_params.get('confirm')
        cancel = request.query_params.get('cancel')

        if confirm:
            # Log out the user and delete their token
            logout(request)
            Token.objects.filter(user=request.user).delete()
            return Response({
                "status": 200,
                "message": "Logout Successful",
            }, status=status.HTTP_200_OK)

        if cancel:
            if request.user.is_superuser:
                return Response({
                    "status": 200,
                    "message": "Logout Cancelled",
                }, status=status.HTTP_200_OK)
            return Response({
                "status": 200,
                "message": "Logout Cancelled",
            }, status=status.HTTP_200_OK)

        return Response({
            "status": 200,
            "message": "Logout Confirmation Required"
        }, status=status.HTTP_200_OK)
    
class ForgotPasswordAPIView(APIView):
    parser_classes = [FormParser, MultiPartParser]

    @swagger_auto_schema(
        tags=["authentication"],
        operation_description="forgotpassword API",
        manual_parameters=swagger_documentation.forgot_password,
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = models.User.objects.get(email=email)
                token = user.generate_reset_password_token()
                reset_link = f"{settings.SITE_URL}/reset-password/{token}/"
                context = {
                    'full_name': user.full_name,
                    'reset_link': reset_link,
                }
                send_template_email(
                    subject='Reset Your Password',
                    template_name='users/email/reset_password_email.html',
                    context=context,
                    recipient_list=[email]
                )
                return Response({"message": "Password reset email sent successfully."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResetPasswordAPIView(APIView):
    parser_classes = [FormParser, MultiPartParser]

    @swagger_auto_schema(
            tags=["authentication"],
            operation_description="resetpassword API",
            manual_parameters=swagger_documentation.reset_password,
        )
    def post(self, request, token):
        serializer = serializers.ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            user = get_object_or_404(models.User, token=token)
            user.password = make_password(new_password)
            user.token = None  # Clear the token after password reset
            user.save()
            return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileApiView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
            tags=["user"],
            operation_description="Retrieve user profile information.",
            responses={
                200: openapi.Response(
                    description="Profile information retrieved successfully.",
                    schema=serializers.UserProfileSerializer()
                ),
                401: openapi.Response(
                    description="Unauthorized. User must be authenticated."
                )
            }
        )
    def get(self, request, *args, **kwargs):
        user = request.user

        # Create response data
        response_data = {
            'user': serializers.UserProfileSerializer(user).data,  # You need to create this serializer
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
class UpdateProfileApiView(APIView):
    parser_classes = [FormParser, MultiPartParser]

    @swagger_auto_schema(
        tags=["user"],
        operation_description="Update user profile",
        manual_parameters=swagger_documentation.update_profile,
        responses={
            200: openapi.Response('Profile updated successfully'),
            400: openapi.Response('Invalid input'),
        }
    )
    def post(self, request, *args, **kwargs):
        form = UpdateProfileForm(request.data, request.FILES)

        if form.is_valid():
            email = form.cleaned_data["email"]
            full_name = form.cleaned_data["full_name"]
            contact = form.cleaned_data["contact"]
            user = request.user

            try:
                user.email = email
                user.full_name = full_name
                user.contact = contact

                user.save()

                return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": f"Error in updating profile: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)