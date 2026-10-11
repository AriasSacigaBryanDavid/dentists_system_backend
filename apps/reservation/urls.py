from django.urls import path
from .views import *

urlpatterns = [
    #---------------------------------------------------------------#
    # TODO: Reservation - PATH
    #---------------------------------------------------------------#
    path('reservations/filter/paginated/', PaginatedReservationView.as_view(), name='reservation-paginated'),
    path('reservations/', ReservationView.as_view(), name='reservation-crud'),
    path('reservations/<uuid:uuid>/', ReservationView.as_view(), name='reservation-crud'),
]
