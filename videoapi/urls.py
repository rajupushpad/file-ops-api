from django.urls import path
from . import views

urlpatterns = [
    path('', views.new_page, name='new_page'),
]