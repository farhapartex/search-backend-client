import random
from datetime import datetime, timedelta
from user.repositories import ActivationRepository
from user.exceptions import InvalidActivationCodeException, ActivationCodeExpiredException


class ActivationService:

    def __init__(self, activation_repository=None):
        self.activation_repository = activation_repository or ActivationRepository()

    def generate_code(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def create_activation(self, user, expiry_hours=24):
        code = self.generate_code()
        expiry = datetime.utcnow() + timedelta(hours=expiry_hours)

        activation = self.activation_repository.create(user, code, expiry)

        return {
            'code': code,
            'expiry': expiry.isoformat()
        }

    def verify_code(self, user, code):
        activation = self.activation_repository.find_by_user_and_code(user, code)

        if not activation:
            raise InvalidActivationCodeException("Invalid activation code")

        if self.activation_repository.is_expired(activation):
            raise ActivationCodeExpiredException("Activation code has expired")

        self.activation_repository.mark_as_used(activation)
