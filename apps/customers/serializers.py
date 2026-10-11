from apps.base.utils.serializers import DynamicFieldsModelSerializer
from rest_framework import serializers
from .models import Customers

#---------------------------------------------------------------#
# TODO: CUSTOMERS - SERIALIZER
#---------------------------------------------------------------#
class CustomersDynamicFieldsSerializer(DynamicFieldsModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Customers
        exclude = ['id']

class CustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = '__all__'