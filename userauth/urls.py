from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.log_in, name="login"),
    path('logout/', views.log_out, name="logout"),
    path('register/', views.register, name="register"),
    # path('/', include('django.contrib.auth.urls')),
    # # path('password_reset/', views.password_reset, name="password_reset"),
    # # path('lost_password/', views.lost_password, name="lost_password"),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='userauth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="userauth/password_reset_confirm.html"), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='userauth/password_reset_complete.html'), name='password_reset_complete'),      
]