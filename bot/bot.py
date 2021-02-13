  
import websocket, json, pprint, talib, numpy, twitter
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethbtc@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHBTC'
TRADE_QUANTITY = 0.03

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')
info = client.get_symbol_info(TRADE_SYMBOL)
min_qty = float(info['filters'][2]['minQty'])

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    json_message = json.loads(message)
    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    balance = client.get_asset_balance(asset=TRADE_SYMBOL[:3])['free']
                    trade_qty = round(balance, (len(str(min_qty)) - 2))
                    order_succeeded = order(SIDE_SELL, trade_qty, TRADE_SYMBOL)
                    t = Twitter(auth=OAuth(config.twitter_token,
                                            config.twitter_token_secret,
                                            config.twitter_consumer_key,
                                            config.twitter_consumer_secret))
                    t.statuses.update(status=f"Trigger {SIDE_BUY} {TRADE_SYMBOL} at {close}")

                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    t = Twitter(auth=OAuth(config.twitter_token,
                                            config.twitter_token_secret,
                                            config.twitter_consumer_key,
                                            config.twitter_consumer_secret))
                    t.statuses.update(status=f"Trigger {SIDE_SELL} {TRADE_SYMBOL} at {close}")
                    if order_succeeded:
                        in_position = True

                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()