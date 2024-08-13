from drf_yasg import openapi

signup_post = [
    openapi.Parameter("full_name", openapi.IN_QUERY, required=True, type=openapi.TYPE_STRING),
    openapi.Parameter("email", openapi.IN_QUERY, required=True, format=openapi.FORMAT_EMAIL, type=openapi.TYPE_STRING),
    openapi.Parameter("contact", openapi.IN_QUERY, required=True, type=openapi.TYPE_STRING),
    openapi.Parameter("password", openapi.IN_QUERY, format=openapi.FORMAT_PASSWORD, required=True, type=openapi.TYPE_STRING),
    
]



login_post = [
    openapi.Parameter(
        "email",
        openapi.IN_FORM,
        description="Email",
        required=True,
        format=openapi.FORMAT_EMAIL,
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "password",
        openapi.IN_FORM,
        description="Password",
        format=openapi.FORMAT_PASSWORD,
        required=True,
        type=openapi.TYPE_STRING,
    ),
]
send_otp_parameters = [
        openapi.Parameter("contact", openapi.IN_QUERY, required=True, type=openapi.TYPE_STRING),

]
validate_otp_parameters = [
    openapi.Parameter(
        "otp",
        openapi.IN_QUERY,
        description="OTP to validate",
        required=True,
        type=openapi.TYPE_STRING,
    ),
]

forgot_password = [
    openapi.Parameter(
        "email",
        openapi.IN_FORM,
        description="User Email",
        type=openapi.TYPE_STRING,
        required=True,
    ),
]

reset_password = [
    openapi.Parameter(
        "password",
        openapi.IN_FORM,
        description="Password",
        type=openapi.TYPE_STRING,
        required=True,
    ),
    openapi.Parameter(
        "confirm_password",
        openapi.IN_FORM,
        description="Confirm Password",
        type=openapi.TYPE_STRING,
        required=True,
    ),
]