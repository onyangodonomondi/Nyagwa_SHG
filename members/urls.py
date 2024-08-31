from django.urls import path
from . import views
from .views import member_contribution_chart

urlpatterns = [
    path('', views.home, name='home'),  # This maps the root URL to the home view
    path('register/', views.register_member, name='register_member'),
    path('admin/member_contribution_chart/', member_contribution_chart, name='member_contribution_chart'),
    
    # Add other URL patterns as needed
]
