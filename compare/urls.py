from django.urls import path
from .views import select


urlpatterns = [
    path('select/', select, name="select")
]