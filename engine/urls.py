from django.urls import path
from engine.views import SearchView, SearchHistoryView

urlpatterns = [
    path('search/', SearchView.as_view(), name='search'),
    path('search/histories/', SearchHistoryView.as_view(), name='search_history'),
]
