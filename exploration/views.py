import matplotlib.pyplot as plt
import pandas as pd
import io

from django.http import  HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from exploration.constants import FILENAME, DIR_NAME, COL_ORDERS, COL_EARNINGS, LOOKBACK, PREDICTION_HORIZON
from exploration.utils import preprocess_data, prepare_model, predict_new_values
from core.utils import get_config


@api_view(['GET'])
def data_viewer(request):
    df_lstm = preprocess_data(DIR_NAME, FILENAME)
    
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
    df_lstm = preprocess_data(DIR_NAME, FILENAME)

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
    df_lstm = preprocess_data(DIR_NAME, FILENAME)

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

    df_lstm = preprocess_data(DIR_NAME, FILENAME)

    prediction_dates, prediction_list = predict_new_values(COL_ORDERS, df_lstm)

    df_pred = pd.DataFrame([prediction_dates,prediction_list]) #Each list would be added as a row
    df_pred = df_pred.transpose() #To Transpose and make each rows as columns
    df_pred.columns=['created_at', COL_ORDERS] #Rename the columns
    df_total = pd.concat([df_lstm, df_pred], axis=0)

    fig = plt.figure(figsize=(16,6))
    df_total.plot(x="created_at", y=COL_ORDERS)
    buf = io.BytesIO()
    plt.xticks(rotation=30)
    plt.title('Predicted orders untill the end of March 2022')
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response

@api_view(['GET'])
def data_predict_earnings(request):

    df_lstm = preprocess_data(DIR_NAME, FILENAME)

    prediction_dates, prediction_list = predict_new_values(COL_EARNINGS, df_lstm)

    df_pred = pd.DataFrame([prediction_dates,prediction_list]) #Each list would be added as a row
    df_pred = df_pred.transpose() #To Transpose and make each rows as columns
    df_pred.columns=['created_at', COL_EARNINGS] #Rename the columns
    df_total = pd.concat([df_lstm, df_pred], axis=0)

    fig = plt.figure(figsize=(16,6))
    df_total.plot(x="created_at", y=COL_EARNINGS)
    buf = io.BytesIO()
    plt.xticks(rotation=30)
    plt.title('Predicted orders untill the end of March 2022')
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response    

