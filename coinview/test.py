from binance.client import Client
import config
from decimal import Decimal
from binance.enums import *
import math



client = Client(config.API_KEY, config.API_SECRET, tld='us')
TRADE_SYMBOL = 'ETHBTC'
info = client.get_symbol_info(TRADE_SYMBOL)
min_qty = float(info['filters'][2]['minQty'])
min_size = -int(math.log10(min_qty))

# orders = client.get_all_orders(symbol=TRADE_SYMBOL, limit=10)
# print(orders)

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

balance = client.get_asset_balance(asset=TRADE_SYMBOL[:3])
info = client.get_symbol_info('ETHBTC')

print(info)
amount = balance['free']
print(round(float(amount),3))



# print(info['filters'][2])
# print('*'*50)
# print(len(str(float(info['filters'][2]['stepSize'][2:]))))
# print(info['filters'][4]['minNotational'])


# order_succeeded = order(symbol=TRADE_SYMBOL, side=SIDE_SELL,order_type=ORDER_TYPE_MARKET, quantity=(balance['free'][:5]))
# print(order_succeeded)

# info = client.get_symbol_info('ETHUSDT')
# print(info)