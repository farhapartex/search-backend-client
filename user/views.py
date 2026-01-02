from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.serializers import SignupSerializer, SigninSerializer, ActivateUserSerializer
from user.services import UserService


class SignupView(APIView):

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        result = UserService.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )

        if not result['success']:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_201_CREATED)


class SigninView(APIView):

    def post(self, request):
        serializer = SigninSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        result = UserService.authenticate_user(
            email=validated_data['email'],
            password=validated_data['password']
        )

        if not result['success']:
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)

        return Response(result, status=status.HTTP_200_OK)


class ActivateUserView(APIView):

    def post(self, request):
        serializer = ActivateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        result = UserService.activate_user(
            user_id=validated_data['user_id'],
            code=validated_data['code']
        )

        if not result['success']:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)
