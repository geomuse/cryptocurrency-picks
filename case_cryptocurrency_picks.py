import requests
import pandas as pd
import numpy as np
import re , time

import os , sys
current_dir = os.path.dirname(os.path.abspath(__file__))
path = '/home/geo/Downloads/geo'
sys.path.append(path)

from password.setting import live_secret , live_api
from notification_bot.g_email import gmail_send
from notification_bot.telegram_chat import send

from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

from loguru import logger 
log = os.path.join(current_dir,'log/error.log')
logger.add(log,level='INFO', rotation='10 MB', format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}')

class collection_all_symbols():
    '''
    1. 每日6点定义主流货币的币种成交量前10
    2. 过滤future,spot方法(?)
    '''
    def __init__(self):
        self.df = None
        
        self.interval = "1h"
        self.limit = 24  # 获取过去1天的数据

        self.interval_5d = "1h"
        self.limit_5d = 24*5  # 获取过去5天的数据

        self.api_key = live_api
        self.api_secret = live_secret
        self.base_url = 'https://api.binance.com'
        self.cal_rs = []
        self.cal_volume = []
        self.cal_symbols = []
        self.main_symbols = ['BTCUSDT','ETHUSDT','BNBUSDT','XRPUSDT','ADAUSDT',
                             'DOGEUSDT','TRXUSDT','SOLUSDT','LTCUSDT','MATICUSDT','DOTUSDT']

    def get_daily_candles(self,symbol,interval,limit):
        url = f'{self.base_url}/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval ,
            'limit': limit 
        }
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        return data
    
    def get_all_symbols(self):
        url = f'{self.base_url}/api/v3/exchangeInfo'
        response = requests.get(url)
        data = response.json()
        symbols = [symbol['symbol'] for symbol in data['symbols']]
        _ = []

        for symbol in symbols :
            if re.search('USDT',symbol):
                _.append(symbol)

        return _

    def initialize_exchange_data(self,data):
        self.df = pd.DataFrame(data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        self.df['Open time'] = pd.to_datetime(self.df['Open time'], unit='ms')
        self.df['Close time'] = pd.to_datetime(self.df['Close time'], unit='ms') 

    def count_rs(self):
        rs = self.df['Close'].astype('float').pct_change().mean() / self.main_data['Close'].astype('float').pct_change().mean()
        return rs 
    
    def count_rs_all(self):
        return self.df['Close'].astype('float').pct_change() / self.main_data5d['Close'].astype('float').pct_change().mean()

    def count_volume(self):
        return self.df['Volume'].astype('float').mean() > 10000 , self.df['Volume'].astype('float').mean()

    def get_strong_5d_rs_above_80(self):
        # self.df['RS'] = self.df['Volume'].astype("float") / self.df['Volume'].astype("float").sum()
        self.df['RS'] = self.count_rs_all()
        self.df['RS_shifted'] = self.df['RS'].shift(1)  # 將RS值向前位移一天
        df = self.df[(self.df['RS'] > self.df['RS_shifted']) & (self.df['RS'] > 0.8)]  # 選擇RS轉強且RS值大於0.8的標的
        return df

    def get_strong_5d_rs(self):
        self.df['RS_mean'] = self.df['RS'].rolling(window=5).mean()  # 計算5日RS均值
        df = self.df[self.df['RS'] > self.df['RS_mean']]  # 選擇RS大於5日均值的標的
        return df

    def main_trend_price(self,btc):
        btc = pd.DataFrame(btc, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        btc = btc['Close']
        return btc

    def main_symbols_data(self):
        main_data = pd.DataFrame({})
        main_data5d = pd.DataFrame({})

        for symbol in self.main_symbols :
            symbol = str(symbol)
            btc = self.get_daily_candles(symbol,self.interval,self.limit)
            if len(btc) > 0 :
                btc = self.main_trend_price(btc)
            else :
                logger.error(f"len(data) == 0.")

            btc5d = self.get_daily_candles(symbol,self.interval_5d,self.limit_5d)
            if len(btc5d) > 0:
                btc5d = self.main_trend_price(btc5d)
            else :
                logger.error(f"len(data) == 0.")
            
            try :
                main_data = pd.concat([main_data,btc],axis=1)
                main_data5d = pd.concat([main_data5d,btc5d],axis=1)
            except Exception as e :
                logger.error(f'{e}')

        return main_data , main_data5d

    def scarpe(self):
        symbols = np.array([self.get_all_symbols()])[0]
        self.main_data , self.main_data5d = self.main_symbols_data()
        '''
        三个过滤条件来过滤,符合的就保留这个symbol.
        '''
        for symbol in symbols:
            symbol = str(symbol)
            data = self.get_daily_candles(symbol,self.interval,self.limit)
            if len(data) > 0:
                self.initialize_exchange_data(data)
                rs = self.count_rs()
                # self.cal_symbols.append(symbol)
            else :
                logger.error(f"len(data) == 0.")

            data = self.get_daily_candles(symbol,self.interval_5d,self.limit_5d)
            if len(data) > 0:
                self.initialize_exchange_data(data)

                df = self.get_strong_5d_rs_above_80()
                if df.empty :
                    continue
                else :
                    ...

                df = self.get_strong_5d_rs()
                if df.empty :
                    continue
                else :
                    ...

                df , volume = self.count_volume()
                if df is False :
                    continue
                else : 
                    ...

            else :
                logger.error(f"len(data) == 0.")
            
            self.cal_symbols.append(symbol)
            self.cal_rs.append(rs)
            self.cal_volume.append(volume)
            
        results = {'symbols':self.cal_symbols,'rs':np.array(self.cal_rs),'volume':np.array(self.cal_volume)}
        results = pd.DataFrame(data=results)
        results = results.sort_values('rs', ascending=False)
        
        text = f'''
            Daily RS top twenty signals.
            {results.head(20)}
            '''
        
        return text , results

def schedule_scrape_print():
    scrape = collection_all_symbols()
    # telegram.send_message(f'Loading.')
    text , symbols = scrape.scarpe()
    # send.send_email(text=text)
    # telegram.send_message(text)
    logger.info(f'Well done about the get symbols code.')

def schedule_scrape():
    scrape , send , telegram = collection_all_symbols() , gmail_send() , send()
    telegram.send_message(f'Loading.')
    text , symbols = scrape.scarpe()
    send.send_email(text=text)
    telegram.send_message(text)
    logger.info(f'Well done about the get symbols code.')

if __name__ == '__main__':
    
    print(f'code loading.')

    # scheduler.add_job(schedule_scrape,'cron',hour=8, minute=0)
    # try :
    #     scheduler.start()
    #     while True :
    #         print(f'Loading. {time.strftime("%Y-%m-%d %H:%M:%S")}') 
    #         time.sleep(60) 
    # except KeyboardInterrupt:
    #     print("\nKeyboard interrupt received. Stopping scheduler.")
    #     scheduler.shutdown()
    
    schedule_scrape_print()
