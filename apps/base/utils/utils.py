import re
import unicodedata
from rest_framework.pagination import PageNumberPagination

#--------------------------------------------------------------------
#------------------------- PAGINATED --------------------------------
#--------------------------------------------------------------------
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

#--------------------------------------------------------------------
#------------------------- CAPITALIZE TEXT ----------------------------
#--------------------------------------------------------------------
def format_instance_fields(instance, fields_map):
    for field, method in fields_map.items():
        value = getattr(instance, field, None)
        if value and isinstance(value, str):
            cleaned_value = value.strip()
            if method == 'title':
                cleaned_value = cleaned_value.title()
            elif method == 'capitalize':
                cleaned_value = cleaned_value.capitalize()
            elif method == 'lower':
                cleaned_value = cleaned_value.lower()
            elif method == 'upper':
                cleaned_value = cleaned_value.upper()
            setattr(instance, field, cleaned_value)