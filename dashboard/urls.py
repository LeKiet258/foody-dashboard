# đây là nơi xử lý vụ: user nhập url, file này có nhiệm vụ gửi tín hiệu tới các views để show ra giao diện
from django.urls import path, include
from . import views # from base project - crm1
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name="home"), 
    path('dashboard/', views.dashboard, name='dashboard')
]
