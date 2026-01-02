# Developer Cookbook

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Design Patterns](#design-patterns)
4. [Building Features](#building-features)
5. [Code Standards](#code-standards)

## Architecture Overview

### Technology Stack
- **Framework**: Django 5.2 + Django REST Framework
- **Database**: MongoDB with MongoEngine ODM
- **Cache**: Redis with django-redis
- **Container**: Docker + Docker Compose

### Layered Architecture

```
┌─────────────────────────────────────┐
│         View Layer (APIView)        │  ← HTTP Request/Response
├─────────────────────────────────────┤
│      Serializer Layer (DRF)         │  ← Validation
├─────────────────────────────────────┤
│      Service Layer (Business)       │  ← Business Logic
├─────────────────────────────────────┤
│    Repository Layer (Data Access)   │  ← Database Operations
├─────────────────────────────────────┤
│      Model Layer (MongoEngine)      │  ← Data Structure
└─────────────────────────────────────┘
```

### Key Principles
- **Separation of Concerns**: Each layer has a single responsibility
- **Dependency Injection**: Services receive dependencies via constructor
- **Exception-Driven Flow**: Use custom exceptions instead of error dictionaries
- **Repository Pattern**: Abstract data access from business logic
- **Service Result Pattern**: Consistent response structure

## Project Structure

```
app_name/
├── models.py              # MongoDB document models
├── exceptions.py          # Custom exception classes
├── result.py             # ServiceResult class
├── serializers.py        # DRF serializers (validation only)
├── repositories/
│   ├── __init__.py
│   └── entity_repository.py
├── services/
│   ├── __init__.py
│   └── entity_service.py
├── views.py              # API endpoints
└── urls.py               # URL routing
```

## Design Patterns

### 1. Model Design (MongoDB Documents)

**Location**: `app_name/models.py`

**Rules**:
- Use MongoEngine Document classes
- Define collection name in meta
- Create indexes for frequently queried fields
- Use proper field types with validation
- Add timestamps (created_at, updated_at)

**Example**:

```python
from mongoengine import Document, StringField, BooleanField, EmailField, DateTimeField, ReferenceField
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


class RelatedModel(Document):
    user = ReferenceField(User, required=True)
    title = StringField(required=True, max_length=200)
    description = StringField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'related_models',
        'indexes': [
            'user',
            'is_active',
            '-created_at'
        ]
    }
```

**Field Types**:
- `StringField` - text data
- `EmailField` - email with validation
- `IntField` - integers
- `FloatField` - decimals
- `BooleanField` - true/false
- `DateTimeField` - timestamps
- `ReferenceField` - foreign key
- `ListField` - arrays
- `DictField` - objects

**Auto-create Indexes**:

```python
# app_name/apps.py
from django.apps import AppConfig


class AppNameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_name'

    def ready(self):
        from app_name.models import User, RelatedModel
        try:
            User.ensure_indexes()
            RelatedModel.ensure_indexes()
        except Exception as e:
            pass
```

### 2. Custom Exceptions

**Location**: `app_name/exceptions.py`

**Rules**:
- Create domain-specific exceptions
- Inherit from base exception classes
- Use descriptive names ending with "Exception"
- Group related exceptions

**Example**:

```python
class EntityException(Exception):
    pass


class EntityNotFoundException(EntityException):
    pass


class EntityAlreadyExistsException(EntityException):
    pass


class InvalidEntityDataException(EntityException):
    pass


class EntityPermissionDeniedException(EntityException):
    pass
```

**When to Create New Exceptions**:
- Distinct error scenarios that need different HTTP status codes
- Business rule violations
- Authorization/permission failures
- Resource not found cases

### 3. Repository Pattern

**Location**: `app_name/repositories/entity_repository.py`

**Rules**:
- One repository per model
- Handle ONLY database operations
- NO business logic
- Methods return model instances or None
- Use descriptive method names

**Template**:

```python
from app_name.models import Entity
from app_name.exceptions import EntityNotFoundException
from datetime import datetime


class EntityRepository:

    def __init__(self):
        pass

    def find_by_id(self, entity_id):
        return Entity.objects(id=entity_id).first()

    def find_by_field(self, field_value):
        return Entity.objects(field_name=field_value).first()

    def find_all(self, filters=None):
        if filters:
            return Entity.objects(**filters)
        return Entity.objects.all()

    def exists_by_field(self, field_value):
        return Entity.objects(field_name=field_value).count() > 0

    def create(self, **kwargs):
        entity = Entity(**kwargs)
        entity.save()
        return entity

    def update(self, entity):
        entity.updated_at = datetime.utcnow()
        entity.save()
        return entity

    def delete(self, entity):
        entity.delete()

    def get_by_id_or_fail(self, entity_id):
        entity = self.find_by_id(entity_id)
        if not entity:
            raise EntityNotFoundException(f"Entity with id {entity_id} not found")
        return entity

    def count(self, filters=None):
        if filters:
            return Entity.objects(**filters).count()
        return Entity.objects.count()
```

**Common Methods**:
- `find_by_*()` - Returns entity or None
- `get_by_*_or_fail()` - Returns entity or raises exception
- `exists_by_*()` - Returns boolean
- `create()` - Creates and returns entity
- `update()` - Updates and returns entity
- `delete()` - Deletes entity
- `find_all()` - Returns queryset
- `count()` - Returns count

### 4. Service Layer

**Location**: `app_name/services/entity_service.py`

**Rules**:
- One service per business domain
- Use dependency injection
- Raise exceptions for errors
- Return data dictionaries on success
- Handle ALL business logic here

**Template**:

```python
from app_name.repositories import EntityRepository
from app_name.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    InvalidEntityDataException
)
from datetime import datetime


class EntityService:

    def __init__(self, entity_repository=None):
        self.entity_repository = entity_repository or EntityRepository()

    def create_entity(self, field1, field2, field3):
        if self.entity_repository.exists_by_field(field1):
            raise EntityAlreadyExistsException("Entity already exists")

        entity = self.entity_repository.create(
            field1=field1,
            field2=field2,
            field3=field3
        )

        return {
            'entity_id': str(entity.id),
            'field1': entity.field1,
            'field2': entity.field2,
            'created_at': entity.created_at.isoformat()
        }

    def get_entity(self, entity_id):
        entity = self.entity_repository.get_by_id_or_fail(entity_id)

        return {
            'entity_id': str(entity.id),
            'field1': entity.field1,
            'field2': entity.field2,
            'is_active': entity.is_active,
            'created_at': entity.created_at.isoformat()
        }

    def update_entity(self, entity_id, **update_data):
        entity = self.entity_repository.get_by_id_or_fail(entity_id)

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        entity = self.entity_repository.update(entity)

        return {
            'entity_id': str(entity.id),
            'message': 'Entity updated successfully'
        }

    def delete_entity(self, entity_id):
        entity = self.entity_repository.get_by_id_or_fail(entity_id)
        self.entity_repository.delete(entity)

        return {
            'entity_id': str(entity_id),
            'message': 'Entity deleted successfully'
        }

    def list_entities(self, filters=None):
        entities = self.entity_repository.find_all(filters)

        return {
            'entities': [
                {
                    'entity_id': str(e.id),
                    'field1': e.field1,
                    'field2': e.field2,
                    'created_at': e.created_at.isoformat()
                }
                for e in entities
            ],
            'total': entities.count()
        }
```

**Service Method Rules**:
- Accept primitive types as parameters (str, int, bool)
- Raise exceptions for failures
- Return dictionaries with serializable data
- Convert ObjectId to string
- Convert DateTime to ISO format
- NO database queries directly (use repository)

### 5. Service Result Pattern

**Location**: `app_name/result.py`

**Standard Implementation**:

```python
class ServiceResult:

    def __init__(self, success, data=None, message=None, errors=None):
        self.success = success
        self.data = data
        self.message = message
        self.errors = errors

    @classmethod
    def ok(cls, data=None, message=None):
        return cls(success=True, data=data, message=message)

    @classmethod
    def fail(cls, message, errors=None):
        return cls(success=False, message=message, errors=errors)

    def to_dict(self):
        result = {'success': self.success}

        if self.message:
            result['message'] = self.message

        if self.data:
            result['data'] = self.data

        if self.errors:
            result['errors'] = self.errors

        return result
```

**Usage**: Import once per app, reuse across all views.

### 6. Serializers

**Location**: `app_name/serializers.py`

**Rules**:
- Use ONLY for request validation
- NO business logic
- NO database queries
- Simple field validation only

**Example**:

```python
from rest_framework import serializers


class CreateEntitySerializer(serializers.Serializer):
    field1 = serializers.CharField(required=True, max_length=100)
    field2 = serializers.EmailField(required=True)
    field3 = serializers.IntegerField(required=False, default=0)
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_field1(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Field1 must be at least 3 characters")
        return value

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return data


class UpdateEntitySerializer(serializers.Serializer):
    field1 = serializers.CharField(required=False, max_length=100)
    field2 = serializers.EmailField(required=False)
    is_active = serializers.BooleanField(required=False)


class EntityFilterSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False)
    created_after = serializers.DateTimeField(required=False)
    limit = serializers.IntegerField(required=False, default=50)
    offset = serializers.IntegerField(required=False, default=0)
```

**Validation Methods**:
- `validate_<field_name>()` - Validate single field
- `validate()` - Cross-field validation

### 7. View Layer (API Endpoints)

**Location**: `app_name/views.py`

**Rules**:
- Use APIView from DRF
- Inject service in `__init__`
- Validate with serializers
- Handle exceptions with try-catch
- Return ServiceResult responses
- Map exceptions to HTTP status codes

**Template**:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app_name.serializers import CreateEntitySerializer, UpdateEntitySerializer
from app_name.services import EntityService
from app_name.result import ServiceResult
from app_name.exceptions import (
    EntityNotFoundException,
    EntityAlreadyExistsException,
    InvalidEntityDataException
)


class CreateEntityView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_service = EntityService()

    def post(self, request):
        serializer = CreateEntitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = self.entity_service.create_entity(
                field1=serializer.validated_data['field1'],
                field2=serializer.validated_data['field2'],
                field3=serializer.validated_data.get('field3', 0)
            )
            result = ServiceResult.ok(data=data, message="Entity created successfully")
            return Response(result.to_dict(), status=status.HTTP_201_CREATED)

        except EntityAlreadyExistsException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_400_BAD_REQUEST)

        except InvalidEntityDataException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_400_BAD_REQUEST)


class GetEntityView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_service = EntityService()

    def get(self, request, entity_id):
        try:
            data = self.entity_service.get_entity(entity_id)
            result = ServiceResult.ok(data=data)
            return Response(result.to_dict(), status=status.HTTP_200_OK)

        except EntityNotFoundException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_404_NOT_FOUND)


class UpdateEntityView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_service = EntityService()

    def patch(self, request, entity_id):
        serializer = UpdateEntitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = self.entity_service.update_entity(
                entity_id=entity_id,
                **serializer.validated_data
            )
            result = ServiceResult.ok(data=data, message="Entity updated successfully")
            return Response(result.to_dict(), status=status.HTTP_200_OK)

        except EntityNotFoundException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_404_NOT_FOUND)


class DeleteEntityView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_service = EntityService()

    def delete(self, request, entity_id):
        try:
            data = self.entity_service.delete_entity(entity_id)
            result = ServiceResult.ok(data=data, message="Entity deleted successfully")
            return Response(result.to_dict(), status=status.HTTP_200_OK)

        except EntityNotFoundException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_404_NOT_FOUND)
```

### 8. URL Routing

**Location**: `app_name/urls.py`

```python
from django.urls import path
from app_name.views import (
    CreateEntityView,
    GetEntityView,
    UpdateEntityView,
    DeleteEntityView
)

urlpatterns = [
    path('entities/', CreateEntityView.as_view(), name='create_entity'),
    path('entities/<str:entity_id>/', GetEntityView.as_view(), name='get_entity'),
    path('entities/<str:entity_id>/update/', UpdateEntityView.as_view(), name='update_entity'),
    path('entities/<str:entity_id>/delete/', DeleteEntityView.as_view(), name='delete_entity'),
]
```

**Register in main urls.py**:

```python
# core/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/v1/app_name/', include('app_name.urls')),
]
```

## Response Structure

### Success Response

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    "entity_id": "507f1f77bcf86cd799439011",
    "field1": "value1",
    "field2": "value2"
  }
}
```

### Error Response

```json
{
  "success": false,
  "message": "Entity not found"
}
```

### Validation Error Response (DRF Auto-generated)

```json
{
  "field1": ["This field is required."],
  "field2": ["Enter a valid email address."]
}
```

## HTTP Status Code Mapping

| Exception | Status Code | When to Use |
|-----------|-------------|-------------|
| `EntityNotFoundException` | 404 | Resource not found |
| `EntityAlreadyExistsException` | 400 | Duplicate resource |
| `InvalidCredentialsException` | 401 | Authentication failed |
| `AccountNotActiveException` | 403 | Permission denied |
| `InvalidEntityDataException` | 400 | Business rule violation |
| `ValidationError` (DRF) | 400 | Input validation failed |
| Generic Exception | 500 | Unexpected server error |

## Building Features

### Step-by-Step Guide

#### 1. Define Model

```python
# app_name/models.py
from mongoengine import Document, StringField, DateTimeField
from datetime import datetime


class Product(Document):
    name = StringField(required=True, max_length=200)
    description = StringField()
    price = FloatField(required=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'products',
        'indexes': ['name', 'is_active', '-created_at']
    }
```

#### 2. Create Exceptions

```python
# app_name/exceptions.py
class ProductException(Exception):
    pass


class ProductNotFoundException(ProductException):
    pass


class ProductAlreadyExistsException(ProductException):
    pass
```

#### 3. Build Repository

```python
# app_name/repositories/product_repository.py
from app_name.models import Product
from app_name.exceptions import ProductNotFoundException
from datetime import datetime


class ProductRepository:

    def __init__(self):
        pass

    def find_by_id(self, product_id):
        return Product.objects(id=product_id).first()

    def find_by_name(self, name):
        return Product.objects(name=name).first()

    def exists_by_name(self, name):
        return Product.objects(name=name).count() > 0

    def create(self, name, description, price):
        product = Product(
            name=name,
            description=description,
            price=price
        )
        product.save()
        return product

    def get_by_id_or_fail(self, product_id):
        product = self.find_by_id(product_id)
        if not product:
            raise ProductNotFoundException(f"Product with id {product_id} not found")
        return product
```

#### 4. Build Service

```python
# app_name/services/product_service.py
from app_name.repositories import ProductRepository
from app_name.exceptions import ProductAlreadyExistsException


class ProductService:

    def __init__(self, product_repository=None):
        self.product_repository = product_repository or ProductRepository()

    def create_product(self, name, description, price):
        if self.product_repository.exists_by_name(name):
            raise ProductAlreadyExistsException("Product with this name already exists")

        product = self.product_repository.create(name, description, price)

        return {
            'product_id': str(product.id),
            'name': product.name,
            'price': product.price,
            'created_at': product.created_at.isoformat()
        }

    def get_product(self, product_id):
        product = self.product_repository.get_by_id_or_fail(product_id)

        return {
            'product_id': str(product.id),
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'is_active': product.is_active
        }
```

#### 5. Create Serializer

```python
# app_name/serializers.py
from rest_framework import serializers


class CreateProductSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.FloatField(required=True, min_value=0)
```

#### 6. Build View

```python
# app_name/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app_name.serializers import CreateProductSerializer
from app_name.services import ProductService
from app_name.result import ServiceResult
from app_name.exceptions import ProductAlreadyExistsException


class CreateProductView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_service = ProductService()

    def post(self, request):
        serializer = CreateProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = self.product_service.create_product(
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description', ''),
                price=serializer.validated_data['price']
            )
            result = ServiceResult.ok(data=data, message="Product created successfully")
            return Response(result.to_dict(), status=status.HTTP_201_CREATED)

        except ProductAlreadyExistsException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_400_BAD_REQUEST)
```

#### 7. Register URLs

```python
# app_name/urls.py
from django.urls import path
from app_name.views import CreateProductView

urlpatterns = [
    path('products/', CreateProductView.as_view(), name='create_product'),
]
```

## Code Standards

### General Rules
1. NO comments in code (self-documenting code)
2. NO emojis in code or responses
3. Use descriptive variable/function names
4. Follow PEP 8 style guide
5. Maximum line length: 120 characters

### Naming Conventions
- **Classes**: PascalCase (UserService, ProductRepository)
- **Functions/Methods**: snake_case (create_user, get_product)
- **Variables**: snake_case (user_id, product_name)
- **Constants**: UPPER_SNAKE_CASE (MAX_RETRY_COUNT)
- **Private methods**: _leading_underscore (_validate_data)

### File Organization
1. Imports at top
2. Constants after imports
3. Classes after constants
4. Functions after classes

### Import Order
1. Python standard library
2. Third-party packages
3. Django/DRF imports
4. Local app imports

```python
import os
from datetime import datetime

from mongoengine import Document, StringField

from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView

from app_name.models import User
from app_name.repositories import UserRepository
```

### Exception Handling
- Always catch specific exceptions
- Never use bare `except:`
- Always provide meaningful error messages

```python
try:
    data = self.service.create_entity()
except EntityAlreadyExistsException as e:
    return Response({'error': str(e)}, status=400)
except Exception as e:
    return Response({'error': 'Unexpected error occurred'}, status=500)
```

### Return Data Guidelines
1. Always return dictionaries from services
2. Convert ObjectId to string: `str(entity.id)`
3. Convert DateTime to ISO string: `entity.created_at.isoformat()`
4. Use consistent field names

### Testing Checklist
Before committing code:
- [ ] All exceptions are caught in views
- [ ] ServiceResult is used for responses
- [ ] No business logic in views or serializers
- [ ] Repository methods tested
- [ ] Service methods tested
- [ ] API endpoints return correct status codes

## Common Patterns

### Pagination

```python
class ListEntitiesView(APIView):

    def get(self, request):
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))

        data = self.entity_service.list_entities(limit, offset)
        result = ServiceResult.ok(data=data)
        return Response(result.to_dict(), status=status.HTTP_200_OK)
```

### Filtering

```python
class FilterEntitiesView(APIView):

    def get(self, request):
        filters = {
            'is_active': request.GET.get('is_active') == 'true',
            'created_after': request.GET.get('created_after')
        }

        data = self.entity_service.filter_entities(filters)
        result = ServiceResult.ok(data=data)
        return Response(result.to_dict(), status=status.HTTP_200_OK)
```

### File Upload

```python
class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


class UploadFileView(APIView):

    def post(self, request):
        serializer = UploadFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']
        data = self.entity_service.process_file(uploaded_file)
        result = ServiceResult.ok(data=data)
        return Response(result.to_dict(), status=status.HTTP_200_OK)
```

## Quick Reference

### MongoDB ObjectId to String
```python
entity_id = str(entity.id)
```

### DateTime to ISO String
```python
created_at = entity.created_at.isoformat()
```

### Password Hashing
```python
from django.contrib.auth.hashers import make_password, check_password

hashed = make_password('plain_password')
is_valid = check_password('plain_password', hashed)
```

### MongoEngine Query Examples
```python
User.objects(email=email).first()
User.objects(is_active=True).count()
User.objects(id=user_id).first()
Product.objects(price__gte=100)
Product.objects(name__icontains='search')
```

### Environment Variables
```python
import os
value = os.getenv('VARIABLE_NAME', 'default_value')
```

## Troubleshooting

### Common Issues

**Issue**: `InvalidURI: Username and password must be escaped`
**Solution**: Use `quote_plus()` for MongoDB credentials in settings.py

**Issue**: Service not found in view
**Solution**: Ensure service is initialized in `__init__` method

**Issue**: Circular import
**Solution**: Move imports inside methods or restructure dependencies

**Issue**: MongoEngine validation error
**Solution**: Check field requirements in model definition

## Summary

Follow this pattern for every feature:
1. Model → 2. Exception → 3. Repository → 4. Service → 5. Serializer → 6. View → 7. URL

Each layer has a specific responsibility. Never skip layers or mix concerns.
