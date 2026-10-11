from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.base.utils.serializers import DynamicFieldsModelSerializer
from apps.customers.models import Customers
from .models import Reservation

User = get_user_model()

#---------------------------------------------------------------#
# TODO: RESERVATION - SERIALIZER
#---------------------------------------------------------------#
class ReservationDynamicFieldsSerializer(DynamicFieldsModelSerializer):
    customer = serializers.SlugRelatedField(slug_field='uuid', read_only=True)
    doctor = serializers.SlugRelatedField(slug_field='uuid', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    state_display = serializers.CharField(source='get_states_display', read_only=True)

    class Meta:
        model = Reservation
        exclude = ['id']


class ReservationSerializer(serializers.ModelSerializer):
    customer = serializers.SlugRelatedField(
        slug_field='uuid', 
        queryset=Customers.objects.all(),
        error_messages={'does_not_exist': 'El paciente con este UUID no existe.'}
    )
    doctor = serializers.SlugRelatedField(
        slug_field='uuid', 
        queryset=User.objects.all(),
        error_messages={'does_not_exist': 'El doctor con este UUID no existe.'}
    )

    class Meta:
        model = Reservation
        fields = '__all__'
