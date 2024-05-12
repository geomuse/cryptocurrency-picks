import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split , cross_val_score
from dataclasses import dataclass

import os , sys 
current_dir = os.path.dirname(os.path.abspath(__file__))
path = '/home/geo/Downloads/geo'
sys.path.append(path)

from notification_bot.loguru_notification import loguru_notf
from notification_bot.telegram_chat import telegram_send
import warnings

from meachine_learning_bot.feature_engineering import df_feature_eng , df_select
from meachine_learning_bot.model_evaluation import df_reports
from gtrade_bot.cryptocurrency_forecast_bar import judging_fbar_probability

logger = loguru_notf(current_dir)
logger.add('bar_forecast_for_dep')

with warnings.catch_warnings():
    warnings.filterwarnings("ignore")

def model(returns):
    # ...
    if len(returns) % 3 == 0 :
        return returns[0] + returns[1] + returns[2]
        # returns[0,0,profit]
    else :
        return 0 

if __name__ == '__main__':
    
    filename = f'{current_dir}/trade_data/ETHUSDT.csv'
    df = pd.read_csv(filename)
    """
    具有明显问题...
    x , y 设计有问题. 
    
    y 定义的问题.
    """
    df['returns'] = (df['close']
                     .pct_change()
                     .apply(lambda x:np.log(1+x))
                    )
    
    df.dropna(inplace=True)
    standard_profit = df['returns'].mean()

    df['bar']= (
        df['close']
        .apply(lambda x : model(x))
        )

    print(df.head())
