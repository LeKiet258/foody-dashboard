from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"), 
    path('/<str:page>/', views.home), 
    path('dashboard/<int:res_id>', views.dashboard, name='dashboard'),
]
