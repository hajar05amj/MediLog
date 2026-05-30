from django.urls import path
from .views import LoginView, RegisterView, ReferenceView, SeedView, AdminStatsView, AdminUserListView, AdminActivityView, AdminUserDetailView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('reference/', ReferenceView.as_view()),
    path('seed/', SeedView.as_view()),
    path('admin/stats/', AdminStatsView.as_view()),
    path('admin/users/', AdminUserListView.as_view()),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view()),
    path('admin/activity/', AdminActivityView.as_view()),
    # Compatibility with non-slash URLs
    path('login', LoginView.as_view()),
    path('register', RegisterView.as_view()),
]
