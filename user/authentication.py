from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user.services import JwtService
from user.repositories import UserRepository


class JWTAuthentication(BaseAuthentication):

    def __init__(self):
        self.jwt_service = JwtService()
        self.user_repository = UserRepository()

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:
            token_type, token = auth_header.split(' ')

            if token_type.lower() != 'bearer':
                raise AuthenticationFailed('Invalid token type. Use Bearer token')

        except ValueError:
            raise AuthenticationFailed('Invalid Authorization header format. Use: Bearer <token>')

        try:
            payload = self.jwt_service.verify_token(token)
            user_id = payload.get('user_id')

            if not user_id:
                raise AuthenticationFailed('Invalid token payload')

            user = self.user_repository.find_by_id(user_id)

            if not user:
                raise AuthenticationFailed('User not found')

            if not user.is_active:
                raise AuthenticationFailed('User account is not active')

            return (user, token)

        except Exception as e:
            raise AuthenticationFailed(str(e))

    def authenticate_header(self, request):
        return 'Bearer'
