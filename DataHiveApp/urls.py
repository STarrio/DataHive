from django.urls import path

from . import views

urlpatterns = [
    path('configurations', views.config, name='config'),
    path('', views.index, name='index'),
]