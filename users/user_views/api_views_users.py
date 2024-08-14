import email
from django.shortcuts import render, redirect
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
        serializer = serializers.LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            if user.is_superuser:
                login(request, user)
                return Response({'message': 'Login successful Admin'}, status=status.HTTP_200_OK)
            else:
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
    