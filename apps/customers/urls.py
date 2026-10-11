from django.urls import path
from .views import *

urlpatterns = [
    #---------------------------------------------------------------#
    # TODO: Customers - PATH
    #---------------------------------------------------------------#
    path('customers/filter/paginated/', PaginatedCustomersView.as_view(), name='customer-paginated'),
    path('customers/', CustomersView.as_view(), name='customer-crud'),
    path('customers/<uuid:uuid>/', CustomersView.as_view(), name='customer-crud'),
]
