from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

# IMPORTS
from .views import *

urlpatterns = [
    #---------------------------------------------------------------#
    # TODO: AUTH - PATH
    #---------------------------------------------------------------#
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #---------------------------------------------------------------#
    # TODO: USER - PATH
    #---------------------------------------------------------------#
    path('users/selector/filter/paginated/', UserSelectorView.as_view(), name='user-selector'),
]