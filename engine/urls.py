from django.urls import path
from engine.views import SearchView

urlpatterns = [
    path('search/', SearchView.as_view(), name='search'),
]
