import secrets
import string
import json
from django.http import Http404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q
from django.db import transaction

# Encryption
from django.contrib.auth.tokens import default_token_generator

# IMPORTS
from apps.base.utils.utils import CustomPagination
from .models import User
from .serializers import *

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


#---------------------------------------------------------------#
# TODO: USER - VIEW
#---------------------------------------------------------------#
class UsersView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    dynamic_serializer_class = UserDynamicFieldsSerializer
    model = User

    def validate_not_trashed(self, instance, data):
        if getattr(instance, 'status', None) == 0 and 'status' not in data:
            raise ValidationError(
                "Acción prohibida: El registro está en la papelera. Restáuralo primero."
            )

    def get_object(self, uuid):
        try:
            return self.model.objects.get(uuid=uuid)
        except self.model.DoesNotExist:
            raise Http404

    def get(self, request, uuid=None, format=None):
        fields_str = request.GET.get('fields', '[]')
        try:
            fields = json.loads(fields_str)
        except json.JSONDecodeError:
            fields = []

        if uuid is None:
            instances = self.model.objects.all()
            serializer = self.dynamic_serializer_class(instances, many=True, fields=fields)
        else:
            instance = self.get_object(uuid=uuid)
            serializer = self.dynamic_serializer_class(instance, fields=fields)

        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            with transaction.atomic():
                instance = serializer.save()
            return Response({'uuid': instance.uuid, 'message': 'Registro creado con éxito.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, uuid, format=None):
        instance = self.get_object(uuid)

        self.validate_not_trashed(instance, request.data)

        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
            return Response({'message': 'Registro actualizado con éxito.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid, format=None):
        instance = self.get_object(uuid)
        instance.status = 0
        instance.save()
        return Response({'message': 'Registro enviado a la papelera.'}, status=status.HTTP_200_OK)

#---------------------------------------------------------------#
# TODO: USERS FILTER PAGINATED - VIEW
#---------------------------------------------------------------#
class PaginatedUsersView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDynamicFieldsSerializer
    model = User
    pagination_class = CustomPagination

    def get(self, request, format=None):
        try:
            status_val = int(request.GET.get('status', '1'))
        except ValueError:
            status_val = 1

        data_search = request.GET.get('data_search', '')

        fields_str = request.GET.get('fields', '[]')
        try:
            fields = json.loads(fields_str)
        except json.JSONDecodeError:
            fields = []

        if not fields:
            fields = None

        queryset = self.model.objects.filter(status=status_val)

        if data_search:
            search_terms = data_search.split()
            q_objects = Q()
            for term in search_terms:
                q_objects &= (
                    Q(first_name__unaccent__icontains=term) |
                    Q(last_name__unaccent__icontains=term)
                )
            queryset = queryset.filter(q_objects)

        queryset = queryset.order_by('-created_at')

        pager = self.pagination_class()
        users_data = pager.paginate_queryset(queryset, request, view=self)

        serializer = self.serializer_class(users_data, many=True, fields=fields)
        return pager.get_paginated_response(serializer.data)

#---------------------------------------------------------------#
# TODO: DOCTORS LIST - VIEW
#---------------------------------------------------------------#
class DoctorsListView(APIView):
    permission_classes = [IsAuthenticated]
    dynamic_serializer_class = UserDynamicFieldsSerializer
    model = User

    def get(self, request, format=None):
        fields_str = request.GET.get('fields', '[]')
        try:
            fields = json.loads(fields_str)
        except json.JSONDecodeError:
            fields = []

        doctors = self.model.objects.filter(
            role__in=[User.Role.DOCTOR],
            status=User.RecordStatus.ACTIVE
        ).order_by('first_name', 'last_name')

        serializer = self.dynamic_serializer_class(doctors, many=True, fields=fields)
        return Response(serializer.data)

