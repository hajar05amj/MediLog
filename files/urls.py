from django.urls import path
from .views import FileUploadView

urlpatterns = [
    path('upload/<int:res_id>/', FileUploadView.as_view()),
]
