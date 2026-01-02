from django.contrib.auth.hashers import make_password, check_password
from user.models import User
from user.services.activation_service import ActivationService
from datetime import datetime


class UserService:

    @staticmethod
    def create_user(email, name, password):
        email = email.lower()

        if User.objects(email=email).first():
            return {
                'success': False,
                'message': 'User with this email already exists'
            }

        hashed_password = make_password(password)

        user = User(
            email=email,
            name=name,
            password=hashed_password,
            is_active=False
        )
        user.save()

        activation_result = ActivationService.create_activation(user)

        return {
            'success': True,
            'message': 'User created successfully',
            'data': {
                'user_id': str(user.id),
                'email': user.email,
                'name': user.name,
                'is_active': user.is_active,
                'activation_code': activation_result['data']['code'],
                'activation_expiry': activation_result['data']['expiry']
            }
        }

    @staticmethod
    def authenticate_user(email, password):
        email = email.lower()

        user = User.objects(email=email).first()

        if not user:
            return {
                'success': False,
                'message': 'Invalid email or password'
            }

        if not check_password(password, user.password):
            return {
                'success': False,
                'message': 'Invalid email or password'
            }

        if not user.is_active:
            return {
                'success': False,
                'message': 'Account is not active'
            }

        return {
            'success': True,
            'message': 'Authentication successful',
            'data': {
                'user_id': str(user.id),
                'email': user.email,
                'name': user.name,
                'is_active': user.is_active
            }
        }

    @staticmethod
    def activate_user(user_id, code):
        user = User.objects(id=user_id).first()

        if not user:
            return {
                'success': False,
                'message': 'User not found'
            }

        verification_result = ActivationService.verify_code(user, code)

        if not verification_result['success']:
            return verification_result

        user.is_active = True
        user.updated_at = datetime.utcnow()
        user.save()

        return {
            'success': True,
            'message': 'User activated successfully',
            'data': {
                'user_id': str(user.id),
                'email': user.email,
                'is_active': user.is_active
            }
        }

    @staticmethod
    def get_user_by_id(user_id):
        user = User.objects(id=user_id).first()

        if not user:
            return {
                'success': False,
                'message': 'User not found'
            }

        return {
            'success': True,
            'data': {
                'user_id': str(user.id),
                'email': user.email,
                'name': user.name,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat()
            }
        }

    @staticmethod
    def get_user_by_email(email):
        email = email.lower()
        user = User.objects(email=email).first()

        if not user:
            return {
                'success': False,
                'message': 'User not found'
            }

        return {
            'success': True,
            'data': {
                'user_id': str(user.id),
                'email': user.email,
                'name': user.name,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat()
            }
        }
