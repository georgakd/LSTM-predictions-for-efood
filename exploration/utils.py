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

    # Calculate feature importance so as to eliminate the total dimensions of the problem    

    # Find missing values if any. Check if the corresponding columns that contain null values can be used as features for the forecasting model.
    # If the percentage of missing data is less than 20% of the whole dataset, we can use drop rows.
    # TODO: If the percentage is larger, then we can use a more advanced imputation technique.
    missing = df_ret.isnull().sum().sum()
    if round(missing/len(df)) < 0.2:
        # call drop null values
        logger.info(f"There are {missing} missing rows for this dataset.")
 



    return df_ret
