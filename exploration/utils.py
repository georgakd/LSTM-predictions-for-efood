import numpy as np
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

def load_data(dir_name, filename):
    with open(os.path.join(os.getcwd(), dir_name, filename)) as f:
        data = pd.read_csv(f)
    return data

def data_preprocessor(dir_name, filename):
    df = load_data(dir_name, filename)

    # Find duplicate rows if any and drop them
    duplicate = df[df.duplicated('order_id')]
    number_of_dups = len(duplicate)
    if number_of_dups:
        df = df.drop_duplicates()
        logger.info(f"There are {number_of_dups} duplicate rows for this dataset.")

    # Returning customers
    # We will only keep in the dataset the customers that have an order history (visitor_type=returning)     
    df1 = df.dropna(subset=['visitor_type'])
    df_ret = df1.loc[df1["visitor_type"].str.contains('returning', case=False)]

    # We will remove thesse columns as they do not contribute in the features of the prediction problem
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


    return df_lstm
