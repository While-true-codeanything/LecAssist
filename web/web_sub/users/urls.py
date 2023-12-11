from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('login/', views.open_login),
    path('register/', views.open_register),
    path('upload/', views.open_upload_page)
]
