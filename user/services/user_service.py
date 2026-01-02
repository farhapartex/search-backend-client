from django.contrib.auth.hashers import make_password, check_password
from user.repositories import UserRepository
from user.services.activation_service import ActivationService
from user.services.jwt_service import JwtService
from user.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AccountNotActiveException
)


class UserService:

    def __init__(self, user_repository=None, activation_service=None, jwt_service=None):
        self.user_repository = user_repository or UserRepository()
        self.activation_service = activation_service or ActivationService()
        self.jwt_service = jwt_service or JwtService()

    def create_user(self, email, name, password):
        if self.user_repository.exists_by_email(email):
            raise UserAlreadyExistsException("User with this email already exists")

        hashed_password = make_password(password)
        user = self.user_repository.create(email, name, hashed_password)

        activation_data = self.activation_service.create_activation(user)

        return {
            'user_id': str(user.id),
            'email': user.email,
            'name': user.name,
            'is_active': user.is_active,
            'activation_code': activation_data['code'],
            'activation_expiry': activation_data['expiry']
        }

    def authenticate_user(self, email, password):
        user = self.user_repository.find_by_email(email)

        if not user:
            raise InvalidCredentialsException("Invalid email or password")

        if not check_password(password, user.password):
            raise InvalidCredentialsException("Invalid email or password")

        if not user.is_active:
            raise AccountNotActiveException("Account is not active")

        return {
            'user_id': str(user.id),
            'email': user.email,
            'name': user.name,
            'is_active': user.is_active
        }

    def signin_user(self, email, password):
        user = self.user_repository.find_by_email(email)

        if not user:
            raise InvalidCredentialsException("Invalid email or password")

        if not check_password(password, user.password):
            raise InvalidCredentialsException("Invalid email or password")

        if not user.is_active:
            raise AccountNotActiveException("Account is not active")

        access_token = self.jwt_service.generate_access_token(
            user_id=str(user.id),
            email=user.email
        )

        return {
            'access_token': access_token
        }

    def activate_user(self, user_id, code):
        user = self.user_repository.get_by_id_or_fail(user_id)

        self.activation_service.verify_code(user, code)

        user = self.user_repository.activate(user)

        return {
            'user_id': str(user.id),
            'email': user.email,
            'is_active': user.is_active
        }

    def get_user_by_id(self, user_id):
        user = self.user_repository.get_by_id_or_fail(user_id)

        return {
            'user_id': str(user.id),
            'email': user.email,
            'name': user.name,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat()
        }

    def get_user_by_email(self, email):
        user = self.user_repository.get_by_email_or_fail(email)

        return {
            'user_id': str(user.id),
            'email': user.email,
            'name': user.name,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat()
        }
