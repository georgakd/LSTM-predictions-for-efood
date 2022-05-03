from django.urls import path
import exploration.views as views

urlpatterns = [
    path('data_viewer/', views.data_viewer, name = 'data_viewer'),
    path('data_trainer_orders/', views.data_trainer_orders, name = 'data_trainer_orders'),
    path('data_trainer_earnings/', views.data_trainer_earnings, name = 'data_trainer_earnings'),
    path('data_predict_orders/', views.data_predict_orders, name = 'data_predict_orders'),
    path('data_predict_earnings/', views.data_predict_earnings, name = 'data_predict_earnings'),
    path('data_predict_per_customer/', views.data_predict_per_customer, name = 'data_predict_per_customer'),
    path('data_predict_per_customer_all_returning_customers/', views.data_predict_per_customer_all_returning_customers, name = 'data_predict_per_customer_all_returning_customers')

]