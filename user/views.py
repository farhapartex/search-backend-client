from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.serializers import SignupSerializer, SigninSerializer, ActivateUserSerializer
from user.services import UserService
from user.result import ServiceResult
from user.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AccountNotActiveException,
    UserNotFoundException,
    InvalidActivationCodeException,
    ActivationCodeExpiredException
)


class SignupView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = self.user_service.create_user(
                email=serializer.validated_data['email'],
                name=serializer.validated_data['name'],
                password=serializer.validated_data['password']
            )
            result = ServiceResult.ok(data=data, message="User created successfully")
            return Response(result.to_dict(), status=status.HTTP_201_CREATED)

        except UserAlreadyExistsException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_400_BAD_REQUEST)


class SigninView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()

    def post(self, request):
        serializer = SigninSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = self.user_service.signin_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            result = ServiceResult.ok(data=data, message="Signin successful")
            return Response(result.to_dict(), status=status.HTTP_200_OK)

        except InvalidCredentialsException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_401_UNAUTHORIZED)

        except AccountNotActiveException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_403_FORBIDDEN)


class ActivateUserView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()

    def post(self, request):
        serializer = ActivateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = self.user_service.activate_user(
                user_id=serializer.validated_data['user_id'],
                code=serializer.validated_data['code']
            )
            result = ServiceResult.ok(data=data, message="User activated successfully")
            return Response(result.to_dict(), status=status.HTTP_200_OK)

        except UserNotFoundException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_404_NOT_FOUND)

        except (InvalidActivationCodeException, ActivationCodeExpiredException) as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_400_BAD_REQUEST)
