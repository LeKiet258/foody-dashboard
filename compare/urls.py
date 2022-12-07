from django.urls import path
from .views import compare


urlpatterns = [
    path('compare/', compare, name="compare")
]