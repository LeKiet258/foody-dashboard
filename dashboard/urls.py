from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"), 
    path('/<str:page>/', views.home), 
    path('dashboard/<int:res_id>/', views.dashboard, name='dashboard'),
    path('compare/', views.compare_2_vendors, name='compare')
]
