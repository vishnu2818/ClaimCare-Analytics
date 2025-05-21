# rcm_app/urls.py
from django.urls import path
from . import views

app_name = 'rcm_app'  # Add this line to namespace your URLs

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('view/<int:upload_id>/', views.view_uploaded_data, name='view_data'),

    path('download/<int:upload_id>/', views.download_filtered_excel, name='download_filtered_excel'),
]