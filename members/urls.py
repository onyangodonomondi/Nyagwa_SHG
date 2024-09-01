from django.urls import path
from . import views
from .views import member_contribution_chart

urlpatterns = [
    path('', views.home, name='home'),  # Root URL mapped to home view
    path('events/', views.events_page, name='events_page'),
    path('register/', views.register_member, name='register_member'),
    path('admin/member_contribution_chart/', member_contribution_chart, name='member_contribution_chart'),

    # Adding the members URL pattern
    path('members/', views.members_page, name='members'),
    path('contributions/', views.contributions_page, name='contributions'),
    path('export/pdf/', views.export_contributions_pdf, name='export_contributions_pdf'),
    path('export/excel/', views.export_contributions_excel, name='export_contributions_excel'),

    # Add other URL patterns as needed
]