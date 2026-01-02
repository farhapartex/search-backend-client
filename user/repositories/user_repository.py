from user.models import User
from user.exceptions import UserNotFoundException
from datetime import datetime


class UserRepository:

    def __init__(self):
        pass

    def find_by_email(self, email):
        return User.objects(email=email.lower()).first()

    def find_by_id(self, user_id):
        return User.objects(id=user_id).first()

    def exists_by_email(self, email):
        return User.objects(email=email.lower()).count() > 0

    def create(self, email, name, hashed_password):
        user = User(
            email=email.lower(),
            name=name,
            password=hashed_password,
            is_active=False
        )
        user.save()
        return user

    def activate(self, user):
        user.is_active = True
        user.updated_at = datetime.utcnow()
        user.save()
        return user

    def update(self, user):
        user.updated_at = datetime.utcnow()
        user.save()
        return user

    def get_by_id_or_fail(self, user_id):
        user = self.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with id {user_id} not found")
        return user

    def get_by_email_or_fail(self, email):
        user = self.find_by_email(email)
        if not user:
            raise UserNotFoundException(f"User with email {email} not found")
        return user
