import numpy as np
import pandas as pd
import logging
import os

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_percentage_error
import h5py
from core.utils import get_config
from exploration.constants import LOOKBACK


logger = logging.getLogger(__name__)


def load_data(dir_name, filename):
    with open(os.path.join(os.getcwd(), dir_name, filename)) as f:
        data = pd.read_csv(f)
    return data

def preprocess_data(dir_name, filename):
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
    X, Y = [], []
    for i in range(lookback, len(df)-lookback):
        X.append(df[i-lookback : i, 0])
        Y.append(df[i : i + prediction_horizon, 0])

    logger.info("LSTM model input successfully constructed.")
    
    return np.array(X), np.array(Y)


def prepare_model(df, col, neurons, epochs, batch_size, lookback=1, prediction_horizon=1):
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
    
    # Load LSTM model
    model = load_model('model_' + col +'.h5')

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

