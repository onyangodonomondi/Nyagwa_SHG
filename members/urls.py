from django.urls import path
from . import views
from .views import member_contribution_chart, CustomPasswordResetView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  # Root URL mapped to home view
    path('events/', views.events_page, name='events_page'),
    path('register/', views.register_member, name='register_member'),
    path('admin/member_contribution_chart/', member_contribution_chart, name='member_contribution_chart'),

    # Adding the members URL pattern
    path('members/', views.members_page, name='members'),
    path('contributions/', views.contributions_page, name='contributions_page'),
    path('export/pdf/', views.export_contributions_pdf, name='export_contributions_pdf'),
    path('export/excel/', views.export_contributions_excel, name='export_contributions_excel'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='custom_password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='custom_password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='custom_password_reset_complete.html'), name='password_reset_complete'),
    path('accounts/profile/', views.profile, name='profile'),
]
