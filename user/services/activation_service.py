import random
from datetime import datetime, timedelta
from user.models import UserActivation


class ActivationService:

    @staticmethod
    def generate_code():
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    @staticmethod
    def create_activation(user, expiry_hours=24):
        code = ActivationService.generate_code()
        expiry = datetime.utcnow() + timedelta(hours=expiry_hours)

        activation = UserActivation(
            user=user,
            code=code,
            expiry=expiry,
            is_used=False
        )
        activation.save()

        return {
            'success': True,
            'data': {
                'code': code,
                'expiry': expiry.isoformat()
            }
        }

    @staticmethod
    def verify_code(user, code):
        activation = UserActivation.objects(
            user=user,
            code=code,
            is_used=False
        ).first()

        if not activation:
            return {
                'success': False,
                'message': 'Invalid activation code'
            }

        if activation.expiry < datetime.utcnow():
            return {
                'success': False,
                'message': 'Activation code has expired'
            }

        activation.is_used = True
        activation.save()

        return {
            'success': True,
            'message': 'Activation code verified successfully'
        }
