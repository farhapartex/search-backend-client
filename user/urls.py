from django.urls import path
from user.views import SignupView, SigninView, ActivateUserView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('activate/', ActivateUserView.as_view(), name='activate'),
]
