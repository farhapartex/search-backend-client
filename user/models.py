from mongoengine import Document, StringField, BooleanField, EmailField, DateTimeField
from datetime import datetime


class User(Document):
    email = EmailField(required=True, unique=True)
    name = StringField(required=True, max_length=255)
    password = StringField(required=True)
    is_active = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'users',
        'indexes': [
            'email',
            'is_active',
            '-created_at'
        ]
    }
