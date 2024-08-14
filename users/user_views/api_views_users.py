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


# -------------------------------------------- custom import
from helpers import swagger_documentation
from helpers import utils, api_permission
from users import models

from users import serializers
from users import tasks
from users.user_views.emails import send_template_email

class SignupApi(APIView):

    serializer_class= serializers.SignupSerializer
    model=models.User

    @swagger_auto_schema(
        tags=["authentication"],
        operation_description="signup API",
        manual_parameters=swagger_documentation.signup_post,
    )
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            serializer.save(
                password = make_password(request.data.get("password"))
            )
            return Response(
               {
                "status":200,
                "message":"Your account is created, Please login..",
               }
            )
        else:
            error_list = utils.serilalizer_error_list(serializer.errors)
            return Response(
               {
                "status":200,
                "error": error_list,
               }
            )
from drf_yasg import openapi
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
        
class LoginApi(APIView):
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
        print("sghkjsdaj")
        serializer = serializers.LoginSerializer(data=request.data)
        print("sghkjsthydthtdaj")

        if serializer.is_valid():
            user = serializer.validated_data['user']
            if user.is_superuser:
                login(request, user)
                return Response({'message': 'Login successful Admin'}, status=status.HTTP_200_OK)
            else:
                print("elseee")
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'message': 'Login successful, Hi User', 'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LogOut(APIView):

    permission_classes = [api_permission.is_authenticated]
    model= models.User

    @swagger_auto_schema(
        tags=["authentication"],
        operation_description="Logout Api",
    )

    def get(self, request):
        Token.objects.get_or_create(user= request.user).delete()
        return Response({
            "status":200,
            "message":"Logout Successful",
        })

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