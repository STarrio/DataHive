from django.urls import path

from . import views

urlpatterns = [
    path('dataset/<int:pk>/', views.DataSetDetailView.as_view(), name='dataset.detail'),
    path('dataset/', views.random_dataset, name='dataset.list'),
    path('configurations/', views.config, name='config'),
    path('', views.index, name='index'),
]