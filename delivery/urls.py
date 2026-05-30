from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('login/', views.courier_login, name='login'),
    path('register/', views.courier_register, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('missions/', views.livraisons_list, name='livraisons'),
    path('missions/<int:pk>/', views.livraison_detail, name='detail_livraison'),
    path('missions/<int:pk>/accepter/', views.accept_mission, name='accept_mission'),
    path('historique/', views.historique, name='historique'),
    path('profil/', views.profil, name='profil'),
    path('notifications/', views.notifications, name='notifications'),
]
