from user.models import UserActivation
from datetime import datetime


class ActivationRepository:

    def __init__(self):
        pass

    def create(self, user, code, expiry):
        activation = UserActivation(
            user=user,
            code=code,
            expiry=expiry,
            is_used=False
        )
        activation.save()
        return activation

    def find_by_user_and_code(self, user, code):
        return UserActivation.objects(
            user=user,
            code=code,
            is_used=False
        ).first()

    def mark_as_used(self, activation):
        activation.is_used = True
        activation.save()
        return activation

    def is_expired(self, activation):
        return activation.expiry < datetime.utcnow()
