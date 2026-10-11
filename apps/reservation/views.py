import json
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.db import transaction

from apps.base.utils.utils import CustomPagination

from .models import *
from .serializers import *

#---------------------------------------------------------------#
# TODO: RESERVATION - VIEW
#---------------------------------------------------------------#
class ReservationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReservationSerializer
    dynamic_serializer_class = ReservationDynamicFieldsSerializer
    model = Reservation

    def get_object(self, uuid):
        try:
            return self.model.objects.get(uuid=uuid)
        except self.model.DoesNotExist:
            raise Http404

    def validate_not_trashed(self, instance, data):
        if getattr(instance, 'status', None) == 0 and 'status' not in data:
            raise ValidationError(
                "Acción prohibida: El registro está en la papelera. Restáuralo primero."
            )

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
# TODO: RESERVATION PAGINATED - VIEW
#---------------------------------------------------------------#
class PaginatedReservationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReservationDynamicFieldsSerializer
    model = Reservation
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
                    Q(customer__first_name__unaccent__icontains=term) |
                    Q(customer__last_name__unaccent__icontains=term) |
                    Q(doctor__first_name__unaccent__icontains=term) |
                    Q(doctor__last_name__unaccent__icontains=term)
                )
            queryset = queryset.filter(q_objects)

        queryset = queryset.order_by('-created_at')

        pager = self.pagination_class()
        reservation_data = pager.paginate_queryset(queryset, request, view=self)

        serializer = self.serializer_class(reservation_data, many=True, fields=fields)
        return pager.get_paginated_response(serializer.data)
