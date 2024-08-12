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
        
class LoginApi(APIView):
    parser_classes = [FormParser, MultiPartParser]
    model= models.User
    serializer_class = serializers.LoginSerializer

    @swagger_auto_schema(
        tags=["authentication"],
        operation_description="Login API",
        manual_parameters=swagger_documentation.login_post,
    )
    def post(self, request):
        resp = {}
        contact= request.data['email']
        password= request.data['password']
        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            user = None
            return Response({
                "status":400,
                "error":[
                    "Login Failed..",
                ]
            })

        if user.check_password(password):
            pass  # Credentials are valid
        else:
            user = None  # Incorrect password
    
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            resp['token']= str(token.key)
            resp['status']= 200
            resp['user']= serializers.UserSerializer(user).data
        else:
            resp['status']= 400
            resp['message']= "Invalid email or password"
        
        return Response(resp)


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
    