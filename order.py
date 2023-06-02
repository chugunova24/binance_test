from binance.spot import Spot as Client
import numpy as np
from numpy.random import rand, uniform
import ccxt
from binance.error import ClientError, ServerError


class Order:
    def __init__(self, api_key, api_secret):
        self.commissions = 0.99
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(base_url='https://testnet.binance.vision',
                             api_key=self.api_key,
                             api_secret=self.api_secret)

    def get_balance(self):
        return self.client.account()

    def get_price_filter(self, symbol):
        data_from_api = self.client.exchange_info()
        symbol_info = next(filter(lambda x: x['symbol'] == symbol, data_from_api['symbols']))

        return next(filter(lambda x: x['filterType'] == 'PRICE_FILTER', symbol_info['filters']))

    def get_availabe_symbols(self):
        exchange_info = self.client.exchange_info()

        for s in exchange_info['symbols']:
            return s['symbol']

    def get_info_symbols(self, symbol: str) -> dict:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'delivery',
            }
        })

        markets = exchange.load_markets()
        return exchange.markets[symbol]

    def get_random_price(self, priceMin: float, priceMax: float) -> float:
        """
        :param priceMin: Нижний диапазон цены, в пределах которого нужно случайным образом выбрать цену.
        :param priceMax: Верхний диапазон цены, в пределах которого нужно случайным образом выбрать цену.
        :return:
        """
        return round(uniform(priceMin, priceMax), 8)

    def split_volume_orders(self, volume: float, number: int, amountDif: float) -> list:
        """
        :param volume: Общий объем
        :param number: Кол-во ордеров, которое должно получиться в итоге.
        :param amountDif: Максимальный разброс между объемами ордеров.
        :return: Список с разделенным общим объемом на неравные части.
        """

        markets = self.get_info_symbols(symbol='BNB/USDT')['precision']
        total = volume
        result = []
        equal_parts = volume / number

        for i in range(number - 1):
            tmp = round(uniform(int(equal_parts) - int(amountDif / 2), int(equal_parts) + int(amountDif / 2)), 8)
            result.append(tmp)
            volume -= tmp

        result.append(total - sum(result))

        return result

    def create_order(self, price: float, pair: str, symbol: str, side: str, type: str, quantity: float, timeInForce=None):
        """
        :param price: Цена за единицу базисной валюты.
        :param pair: Пара валют, например 'BNB/USDT'
        :param symbol:
        :param side: Выбрать продать ('SELL') или купить ('BUY') выбранную валюту.
        :param type: Тип ордера (Рыночный, лимитный и т.д.)
        :param quantity: Кол-во валюты, которую собираетесь купить.
        :param timeInForce: Способ выставления ордера.
        :return: Возвращает словарь, в которой указана информация о созданном ордере.
        """

        markets = self.get_info_symbols(symbol=pair)['precision']

        if side == 'SELL':
            quantity = round(float(quantity), markets['amount'] - 1)
            price = round(float(price) * self.commissions, markets['price'])
        elif side == 'BUY':
            quantity = np.floor(float(quantity), markets['amount'] - 1)
            price = np.floor(float(price) * self.commissions, markets['price'])
        else:
            raise Exception('Неверное значение аргумента side')

        params = {
            'symbol': symbol,
            'side': side,
            'type': type,
            'timeInForce': timeInForce,  # пока ордер не будет выполнен или отменен. обязателен при лимитном ордере
            'quantity': quantity,  # колво base валюты
            'price': price,  # цена за штучку
        }

        try:
            return self.client.new_order(**params)

        except Exception as client_error:  # ИЗМЕНИТЬ!!!

            if isinstance(client_error, ClientError):
                print(f'Ошибка. Ордер не добавлен, причина: {client_error.error_message}')

                return None
            else:
                print(f'Ошибка. Ордер не добавлен, причина: {client_error}')

                return None

    def get_account_orders(self, symbol: str, orderId=None, startTime=None, endTime=None, limit=None):
        """
        :param symbol: Название курса, например 'BTCUSDT'. Является обязательным.
        :param orderId: id ордера. Необязательный.
        :param startTime: Верхняя граница времени. Необязательный.
        :param endTime: Нижняя граница времени. Необязательный.
        :param limit: Максимальное кол-во эелементов для вывода. Необязательный.

        :return: Возвращает отфильтрованный в зависимости от входных аргументов список ордеров аккаунта
        (активные, отмененные и заполненные).
        """
        return self.client.get_orders(symbol=symbol, orderId=orderId, startTime=startTime,
                                      endTime=endTime, limit=limit, recvWindow=10000)

