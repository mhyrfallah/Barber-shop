from django.urls import path
from . import views

app_name = 'barbershop'

urlpatterns = [
    path('', views.day_list, name='day_list'),
    path('day/<int:day_id>/', views.day_detail, name='day_detail'),
]