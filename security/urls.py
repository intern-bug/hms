from django.urls import path
from . import views

app_name= 'security'

urlpatterns = [
    path('home/', views.home, name='home'),
]