from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('otp-generate/', views.admin_otp, name='admin-otp'),  # Change to a unique path
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_user, name='logout_user'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('action/<str:action>/', views.employee_action, name='employee-action'),
    path('user-list/', views.user_list, name='user-list'),  # List of users
    path('user-attendance/<int:user_id>/', views.user_attendance, name='user-attendance'),  # User attendance details
]
