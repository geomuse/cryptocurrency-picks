import requests

def get_btc_price():
    # Binance API endpoint for current price
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

    try:
        response = requests.get(url)
        data = response.json()  # 解析返回的JSON数据
        price = data.get('price')
        if price:
            return f"当前 BTC/USDT 的价格是: {price}"
        else:
            return "未能获取价格信息。"
    except Exception as e:
        return f"请求出错: {e}"

# 调用函数并打印结果
print(get_btc_price())
