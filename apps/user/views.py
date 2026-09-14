import secrets
import string
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q

# Encryption
from django.contrib.auth.tokens import default_token_generator

# IMPORTS
from apps.base.utils.utils import CustomPagination
from .models import User
from .serializers import CustomTokenObtainPairSerializer

#---------------------------------------------------------------#
# TODO: LOGIN AUTH - VIEW
#---------------------------------------------------------------#
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Faltan credenciales.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            username = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Usuario y/o contraseña son incorrectas.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not username.check_password(password):
            return Response({'error': 'Usuario y/o contraseña son incorrectas.'}, status=status.HTTP_401_UNAUTHORIZED)

        if username.status != username.RecordStatus.ACTIVE:
            return Response({'error': 'La cuenta no está activa o está bloqueada.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

#---------------------------------------------------------------#
# TODO: USER SELECTOR FILTER - VIEW
#---------------------------------------------------------------#
class UserSelectorView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        data_search = request.GET.get('data_search', '')

        queryset = User.objects.filter(is_active=True)

        queryset = queryset.order_by('first_name')

        if data_search:
            search_terms = data_search.split()
            q_objects = Q()
            for term in search_terms:
                q_objects &= (
                    Q(first_name__unaccent__icontains=term) |
                    Q(last_name__unaccent__icontains=term)
                )
            queryset = queryset.filter(q_objects)

        pager = self.pagination_class()
        paginated_data = pager.paginate_queryset(queryset, request, view=self)

        data = [{
            "uuid": u.uuid,
            "full_name": u.full_name
        } for u in paginated_data]

        return pager.get_paginated_response(data)