import matplotlib.pyplot as plt
import pandas as pd
import io

from django.http import  HttpResponse
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view
from exploration.constants import FILENAME, DIR_NAME, COL_ORDERS, COL_EARNINGS, LOOKBACK, PREDICTION_HORIZON, FILENAME_ORDER_VALUES, FILENAME_ORDERS
from exploration.utils import preprocess_all_data, prepare_model, predict_new_values, preprocess_top_ten_data
from core.utils import get_config

import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def data_viewer(request):
    """
    API request to view plots of the total orders per day, total earnings per day at all the customers
    """

    df_lstm = preprocess_all_data(DIR_NAME, FILENAME)
    
    fig = plt.figure(figsize=(16,6))
    df_lstm.plot(x="created_at", y=["order_id", "total_order_value"])
    buf = io.BytesIO()
    plt.xticks(rotation=30)
    plt.title('Total orders and earnings per day')
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response


@api_view(['GET'])
def data_trainer_orders(request):
    """
    API request to train a generalized LSTM model for the total orders per day for all the customers
    """

    df_lstm = preprocess_all_data(DIR_NAME, FILENAME)

    Y_test, test_predict = prepare_model(df_lstm, COL_ORDERS, 
                                    get_config('NEURONS_GEN_ORDERS', cast=int),
                                    get_config('EPOCHS_GEN_ORDERS', cast=int),
                                    get_config('BATCH_SIZE_GEN_ORDERS', cast=int),  
                                    lookback=LOOKBACK, 
                                    prediction_horizon=PREDICTION_HORIZON)
    
    actual = Y_test[:][0]
    predicted = test_predict[:][0] 

    fig = plt.figure(figsize=(16,6))
    plt.plot(actual, label='Actual orders')
    plt.plot(predicted, label='Predicted orders')
    buf = io.BytesIO()

    plt.ylabel('Orders', size=13)
    plt.xlabel('Time Step (Days)', size=13)
    plt.tight_layout()
    plt.legend(fontsize=13)
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response          


@api_view(['GET'])
def data_trainer_earnings(request):
    """
    API request to train a generalized LSTM model for the total order values per day for all the customers
    """

    df_lstm = preprocess_all_data(DIR_NAME, FILENAME)

    Y_test, test_predict = prepare_model(df_lstm, COL_EARNINGS, 
                                       get_config('NEURONS_GEN_EARNINGS', cast=int), 
                                       get_config('EPOCHS_GEN_EARNINGS', cast=int),
                                       get_config('BATCH_SIZE_GEN_EARNINGS', cast=int), 
                                       lookback=LOOKBACK, 
                                       prediction_horizon=PREDICTION_HORIZON)
    
    actual = Y_test[:][0]
    predicted = test_predict[:][0]

    fig = plt.figure(figsize=(16,6))
    plt.plot(actual, label='Actual earnings')
    plt.plot(predicted, label='Predicted earnings')
    buf = io.BytesIO()

    plt.ylabel('Orders', size=13)
    plt.xlabel('Time Step (Days)', size=13)
    plt.tight_layout()
    plt.legend(fontsize=13)
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response 

@api_view(['GET'])
def data_predict_orders(request):
    """
    API request to predict for the total orders per day for all the customers at N points ahead in time, 
    N is configurable in .env through the parameter NUM_PREDICTION. 
    """

    df_lstm = preprocess_all_data(DIR_NAME, FILENAME)

    prediction_dates, prediction_list = predict_new_values(COL_ORDERS, df_lstm)
    prediction_list=[int(i) for i in prediction_list]


    df_pred = pd.DataFrame([prediction_dates,prediction_list]) #Each list would be added as a row
    df_pred = df_pred.transpose() #To Transpose and make each rows as columns
    df_pred.columns=['created_at', COL_ORDERS] #Rename the columns
    df_total = pd.concat([df_lstm, df_pred], axis=0)

    fig = plt.figure(figsize=(16,6))
    df_total.plot(x="created_at", y=COL_ORDERS)
    buf = io.BytesIO()
    plt.xticks(rotation=30)
    plt.title('Predicted orders untill the end of March 2019')
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response

@api_view(['GET'])
def data_predict_earnings(request):
    """
    API request to predict for the total values of orders per day for all the customers at N points ahead in time, 
    N is configurable in .env through the parameter NUM_PREDICTION. 
    """

    df_lstm = preprocess_all_data(DIR_NAME, FILENAME)

    prediction_dates, prediction_list = predict_new_values(COL_EARNINGS, df_lstm)

    df_pred = pd.DataFrame([prediction_dates,prediction_list]) #Each list would be added as a row
    df_pred = df_pred.transpose() #To Transpose and make each rows as columns
    df_pred.columns=['created_at', COL_EARNINGS] #Rename the columns
    df_total = pd.concat([df_lstm, df_pred], axis=0)

    fig = plt.figure(figsize=(16,6))
    df_total.plot(x="created_at", y=COL_EARNINGS)
    buf = io.BytesIO()
    plt.xticks(rotation=30)
    plt.title('Predicted earnings untill the end of March 2019')
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response    

@api_view(['GET'])
def data_predict_per_customer(request):
    """
    API request to predict the sum of orders and values per given customer at N points ahead in time, 
    N is configurable in .env through the parameter NUM_PREDICTION. 
    """

    df_orders = preprocess_top_ten_data(DIR_NAME, FILENAME_ORDERS, COL_ORDERS, 'count')
    df_values = preprocess_top_ten_data(DIR_NAME, FILENAME_ORDER_VALUES, COL_EARNINGS, 'sum')

    prediction_dates, prediction_list_orders = predict_new_values(get_config('CUSTOMER_order_id'), df_orders)
    prediction_dates, prediction_list_values = predict_new_values(get_config('CUSTOMER_total_order_value'), df_values)

    prediction_list_orders=[int(i) for i in prediction_list_orders]

    logger.info(f"The total number of predicted orders for customer_id {get_config('CUSTOMER_order_id',cast=str)} is {sum(prediction_list_orders)}")
    logger.info(f"The total number of predicted values for customer_id {get_config('CUSTOMER_total_order_value',cast=str)} is {sum(prediction_list_values)}")
    
    response_data = {
            'customer_id_orders': get_config('CUSTOMER_order_id'),
            'total_predicted_orders': sum(prediction_list_orders),
            'customer_id_values': get_config('CUSTOMER_total_order_value'),
            'total_predicted_values': sum(prediction_list_values),
        }
    
    return JsonResponse(response_data) 