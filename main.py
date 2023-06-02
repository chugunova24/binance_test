# pip install python-binance
# https://python-binance.readthedocs.io/en/latest/

from data import data
from order import Order

key = 'XXX'
secret = 'XXX'


def main(api_key, api_secret):
    """
    :param api_key: key от api Binance
    :param api_secret: secret от api Binance
    :return: Разделенный по ордерам объем
    """

    ord = Order(api_key=api_key,
                api_secret=api_secret)

    volume = data['volume']
    number = data['number']
    amountDif = data['amountDif']
    side = data['side']
    priceMin = data['priceMin']
    priceMax = data['priceMax']
    pair = 'BNB/USDT'
    info_symbols = ord.get_info_symbols(symbol=pair)
    symbol = info_symbols['id']

    split_volumes = ord.split_volume_orders(number=number, amountDif=amountDif, volume=volume, type=side)

    return split_volumes


