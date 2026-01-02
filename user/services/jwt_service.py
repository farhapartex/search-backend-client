import jwt
from datetime import datetime, timedelta
from django.conf import settings


class JwtService:

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    def generate_access_token(self, user_id, email):
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            'iat': datetime.utcnow(),
            'type': 'access'
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def generate_refresh_token(self, user_id, email):
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

    def verify_token(self, token):
        try:
            payload = self.decode_token(token)
            return {
                'user_id': payload.get('user_id'),
                'email': payload.get('email'),
                'type': payload.get('type')
            }
        except Exception as e:
            raise e
