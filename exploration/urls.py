from django.urls import path
import exploration.views as views

urlpatterns = [
    path('data_viewer/', views.data_viewer, name = 'data_viewer'),
    path('data_trainer_orders/', views.data_trainer_orders, name = 'data_trainer_orders'),
    path('data_trainer_earnings/', views.data_trainer_earnings, name = 'data_trainer_earnings')

]