# rcm_app/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

app_name = 'rcm_app'  # Add this line to namespace your URLs

urlpatterns = [
    path('', home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='rcm_app:login'), name='logout'),
    path('upload/', upload_excel, name='upload_excel'),
    path('view/<int:upload_id>/', view_uploaded_data, name='view_data'),
    path('download/<int:upload_id>/', download_filtered_excel, name='download_filtered_excel'),
]