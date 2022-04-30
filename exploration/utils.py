import numpy as np
import pandas as pd
import logging
import os, re
import datetime

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_percentage_error
import h5py
from core.utils import get_config
from exploration.constants import LOOKBACK


logger = logging.getLogger(__name__)


def load_data(dir_name, filename):
    """
    Read input csv data.
    """

    with open(os.path.join(os.getcwd(), dir_name, filename)) as f:
        data = pd.read_csv(f)
    return data

def find_missing_dates(df):
    """
    If there are missing dates in the dataset, the missing values are imputed.
    """

    # drop time
    df['created_at']=[i.split('T')[0] for i in df['created_at']]
    # get all days from min to max; just in case a day is missing...
    days = [datetime.datetime.strptime(i, '%Y-%m-%d') for i in set(df['created_at'])]
    all_days = []
    for i in range((max(days) - min(days)).days+1):
        all_days.append(str(min(days) + datetime.timedelta(days=i)).split()[0])
    return all_days        

def preprocess_top_ten_data(dir_name, filename, col, operation_type):
    """
    Preprocess data regarding the per customer predictions.
    """

    df = load_data(dir_name, filename)
    all_days = find_missing_dates(df)
    
    output = []
    # loop on unique customer ids
    for unique_customer in [str(i) for i in set(df['customer_id'])]:
        current_customer_data = df[(df.customer_id == int(unique_customer))].groupby('created_at')[col].agg(operation_type).to_dict()
        # prepare data dict for all days with 0 value and overwrite when you find a non-zero day entry
        final_customer_data = {i:0.0 for i in all_days}
        for i,j in current_customer_data.items():
            if i in final_customer_data:
                final_customer_data[i] = j
        # prepare dataframe for current customer
        final_customer_dataframe = pd.DataFrame.from_dict(final_customer_data, orient='index', columns=[unique_customer])
        output.append(final_customer_dataframe)

    # join dataframes
    output = pd.concat([i for i in output], axis=1)
    output.reset_index(inplace=True)
    output = output.rename(columns = {'index':'created_at'})

    logger.info(" Dataframe with unique customers as columns successfully transformed.")


    return output    

def preprocess_all_data(dir_name, filename):
    """
    Preprocess data regarding the whole customer portfolio.
    """

    df = load_data(dir_name, filename)

    # Find duplicate rows if any and drop them
    duplicate = df[df.duplicated()]
    number_of_dups = len(duplicate)
    if number_of_dups:
        df = df.drop_duplicates()
        logger.info(f"There are {number_of_dups} duplicate rows for this dataset.")

    # Returning customers
    # We will only keep in the dataset the customers that have an order history (visitor_type=returning)     
    df1 = df.dropna(subset=['visitor_type'])
    df_ret = df1.loc[df1["visitor_type"].str.contains('returning', case=False)]

    # We will remove these columns as they do not contribute in the features of the prediction problem
    df_minimal = df_ret.drop(columns=['platform', 'vendor_id', 'business_type', 'zipcode', 'cash', 'has_coupon', 'channel'])
    
    # Convert the x column to date
    df_minimal['created_at'] = pd.to_datetime(df_minimal['created_at'])
    df_minimal['created_at'] = df_minimal['created_at'].apply(lambda x: x.date())

    # Calculate orders and earnings per day
    total_orders_per_day = df_minimal.groupby('created_at',as_index=False)['order_id'].count()
    total_earnings_per_day = df_minimal.groupby('created_at',as_index=False)['total_order_value'].sum()
    total_earnings_per_day = total_earnings_per_day.drop(columns='created_at')
    
    # Create the dataset for the LSTM model and add one more feature related to weekday-weekend
    df_lstm = pd.concat([total_orders_per_day, total_earnings_per_day], axis=1)
    df_lstm['weekday'] = df_lstm['created_at'].apply(lambda x: x.weekday()>=5)
    
    logger.info(" Input dataframe successfully transformed.")

    return df_lstm


def prepare_lstm_data(df, lookback=1, prediction_horizon=1):
    """
    Preprocess data and prepare the input for LSTM.
    """

    X, Y = [], []
    for i in range(lookback, len(df)-lookback):
        X.append(df[i-lookback : i, 0])
        Y.append(df[i : i + prediction_horizon, 0])

    logger.info("LSTM model input successfully constructed.")
    
    return np.array(X), np.array(Y)


def prepare_model(df, col, neurons, epochs, batch_size, lookback=1, prediction_horizon=1):
    """
    Create the LSTM model and save it in h5d5 format.
    """

    data = df[col].values
    data = data.reshape((-1,1))
    data.shape
    scaler = MinMaxScaler(feature_range=(0,1))
    data = scaler.fit_transform(data)
    train_size = int(len(data) * 0.7)
    train, test = data[:train_size], data[train_size:]

    X_train, Y_train = prepare_lstm_data(train, lookback, prediction_horizon)
    X_test, Y_test = prepare_lstm_data(test, lookback, prediction_horizon)

    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test  = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    model = Sequential()
    model.add(LSTM(neurons, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dense(prediction_horizon))
    model.compile(optimizer='adam', loss='mean_squared_error')

    print(model.summary())

    history = model.fit(X_train, Y_train, 
                        epochs=epochs, 
                        batch_size=batch_size,
                        verbose=0,
                        shuffle=False)

    model.save('model_' + col +'.h5')
    # Make the predictions on the test set and compare them with the actual readings
    test_predict  = model.predict(X_test)

    # Invert the predictions to original scale
    test_predict  = scaler.inverse_transform(test_predict)
    Y_test = scaler.inverse_transform(Y_test)
    
    logger.info(f"LSTM model for {col} successfully prepared.")
    logger.debug(f"MAPE score for {col}: {mean_absolute_percentage_error(Y_test, test_predict)}")                    
    return Y_test, test_predict


def predict_new_values(col, df):
    """
    Generalised function for future predictions. 
    Predictions can be for total_orders for a given/or all customers, total_order_values for a given/or all customers.
    """
    
    # Load LSTM model

    if re.search("order_id", col):
        model = load_model('model_' + 'order_id' +'.h5')
    elif re.search("total_order_value", col):
        model = load_model('model_' + 'total_order_value' +'.h5')
    else:
        logger.error("No model found")

    if ':' in col:
        col = col.split(':')[0]

    # Prepare the N-points future dataset
    data = df[col].values
    data = data.reshape((-1,1))
    data.shape
    scaler = MinMaxScaler(feature_range=(0,1))
    data = scaler.fit_transform(data)

    prediction_list = data[-LOOKBACK:]
    num_prediction = get_config('NUM_PREDICTION', cast=int) 


    for _ in range(num_prediction):
        x = prediction_list[-LOOKBACK:]
        x = x.reshape((1, LOOKBACK, 1))
        out = model.predict(x)[0][0]
        prediction_list = np.append(prediction_list, out)
    prediction_list = prediction_list[LOOKBACK-1:]

    prediction_list = prediction_list.reshape((-1,1))
    prediction_list  = scaler.inverse_transform(prediction_list)
    prediction_list = [i[0] for i in prediction_list]

    last_date = df['created_at'].values[-1]
    prediction_dates = pd.date_range(last_date, periods=num_prediction+1).tolist()


    return prediction_dates, prediction_list 

