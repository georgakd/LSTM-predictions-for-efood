from django.urls import path
import exploration.views as views

urlpatterns = [
    path('data_viewer/', views.data_viewer, name = 'data_viewer')
]