from django.urls import path
from .views import ReservationListView, ReservationReceiptView

urlpatterns = [
    path('', ReservationListView.as_view()),
    path('<int:reservation_id>/receipt/', ReservationReceiptView.as_view()),
]
