import numpy as np
import pandas as pd

import os , sys , joblib
current_dir = os.path.dirname(os.path.abspath(__file__))
path = '/home/geo/Downloads/gspace'
path = r'c:\Users\boonh\Downloads\gspace\devscape'

sys.path.append(path)

from notification_bot.loguru_notification import loguru_notf
from notification_bot.telegram_chat import telegram_send

from ml_bot.feature_engineering import df_feature_eng , df_select
from ml_bot.model_evaluation import df_reports
from gtrade_bot.cryptocurrency_forecast_bar import judging_fbar_probability

logger = loguru_notf(current_dir)
logger.add('bar_forecast_for_dep')

filename = f'{current_dir}/trade_data/ETHUSDT.csv'

import warnings
with warnings.catch_warnings():
    # warnings.filterwarnings("ignore",category=pd.errors.SettingWithCopyWarning)
    warnings.filterwarnings("ignore")
    # 结构有误.

# class 
if __name__ == '__main__':

    pddf = df_select()
    ml_report = df_reports()
    m = judging_fbar_probability()
    dm = df_feature_eng()
    send_chat = telegram_send()

    df = pddf.read_csv(filename)
    df['returns'] = (df['close']
                     .pct_change()
                     .apply(lambda x:np.log(1+x))
                     )
    
    df.dropna(inplace=True)
    standard_profit = df['returns'].mean()
    
    df_75_percent , df_25_percent = pddf.select_df(df,0.75)
    
    df_75_percent['bars_cumsum'] = m.calculate_cumsum_every_many_bar(df_75_percent['returns'])
    x = m.feature_filter(df_75_percent,feature=['open','close','volume'])
    y = df_75_percent['label'] = (df_75_percent['bars_cumsum']
                                    .apply(lambda x: x>standard_profit if 1 else -1)
                                    .apply(lambda x: 1 if x else -1)
                                    )

    print(df_75_percent.head())

