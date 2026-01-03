from mongoengine import Document, StringField, IntField, ListField, DateTimeField, ReferenceField
from datetime import datetime
from user.models import User


class SearchHistory(Document):
    user = ReferenceField(User, required=True)
    platforms = ListField(StringField(), required=True)
    query = StringField(required=True, max_length=500)
    max_results = IntField(required=True, default=20)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'search_histories',
        'indexes': [
            'user',
            '-created_at',
            ('user', '-created_at')
        ]
    }
