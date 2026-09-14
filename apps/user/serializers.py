from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# IMPORTS
from .models import User
from apps.base.utils.serializers import DynamicFieldsModelSerializer

#---------------------------------------------------------------#
# TODO: CUSTOM AUTHENTICATION TOKEN - SERIALIZER
#---------------------------------------------------------------#
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # We append the final data to the token
        token['user_uuid'] = str(user.uuid)
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['role_display'] = user.get_role_display()
        token['permissions'] = user.role

        return token

#---------------------------------------------------------------#
# TODO: USER - SERIALIZER
#---------------------------------------------------------------#
class UserDynamicFieldsSerializer(DynamicFieldsModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = '__all__'
        exclude = ['id']