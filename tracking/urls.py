from django.urls import path
from .views import UpdateStatusView, TrackingDataView, TrackingUpdateView, InitRouteView

urlpatterns = [
    path('<int:res_id>/status/', UpdateStatusView.as_view()),
    path('<int:res_id>/tracking/', TrackingDataView.as_view()),
    path('<int:res_id>/tracking/update/', TrackingUpdateView.as_view()),
    path('<int:res_id>/tracking/init-route/', InitRouteView.as_view()),
]
