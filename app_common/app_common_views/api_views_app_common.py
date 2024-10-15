from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from helpers import api_permission, privacy_t_and_c

class ApiPrivacyPolicy(APIView):
    permission_classes = [api_permission.is_authenticated]

    @swagger_auto_schema(
        tags=["privacy policy and t&c & about"],
        operation_description="Privacy Policy",
    )
    def get(self,request ):
        
        return Response({
            'status':200,
            "data": privacy_t_and_c.privacy_policy or None
        })
    
class ApiTermsCondition(APIView):
    permission_classes = [api_permission.is_authenticated]

    @swagger_auto_schema(
        tags=["privacy policy and t&c & about"],
        operation_description="Terms and Condition",
    )
    def get(self,request ):
        
        return Response({
            'status':200,
            "data": privacy_t_and_c.t_and_c or None
        })

class ApiAboutUs(APIView):
    permission_classes = [api_permission.is_authenticated]

    @swagger_auto_schema(
        tags=["privacy policy and t&c & about"],
        operation_description="About Us",
    )
    def get(self,request ):
        
        return Response({
            'status':200,
            "data": privacy_t_and_c.about_us or None
        })


class ApiReturnPolicy(APIView):
    permission_classes = [api_permission.is_authenticated]

    @swagger_auto_schema(
        tags=["privacy policy and t&c & about"],
        operation_description="Return Policy",
        responses={200: 'Success'}
    )
    def get(self, request):
        return Response({
            'status': 200,
            'data': privacy_t_and_c.return_policy or None
        }, status=status.HTTP_200_OK)