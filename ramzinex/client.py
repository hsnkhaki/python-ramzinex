import requests
import json
import logging

logging.basicConfig(level=logging.INFO)


class NotAvailableOrderBook(object):
    pass


def rx_lower(coin):
    return coin.lower() if coin != 'AAVE' else 'AAVE'


class RamzinexPublic:
    def __init__(self, verbose=0, timeout=100):
        """

        :param verbose: 0 no log, 1 log responses only, 2 log responses and messages
        """
        self.verbose = verbose
        self.timeout = timeout
        self.resp = None
        self.url = 'https://ramzinex.com/exchange/api/v1.0/exchange'
        self.auth = None
        self.session = requests.Session()
        self.markets = self._extract_markets()
        assert self.markets, 'The markets are not extracted. Please try again.'
        self.currencies = self._extract_currencies()
        assert self.currencies, 'The currencies are not extracted. Please try again.'

    def log_info(self, message, log_level):
        """

        :param message:
        :param log_level: 0 no log, 1 log responses only, 2 log responses and messages
        :return:
        """
        if log_level <= self.verbose:
            logging.info(message)

    def _tear_down_request(self, fun_name, message, base_log_level=0, *args, **kwargs):
        if self._send_message(message, base_log_level, *args, **kwargs):
            self.log_info(f'****{fun_name} is done successfully', base_log_level + 1)
        else:
            self.log_info(f'!!!!{fun_name} is failed.', base_log_level + 1)

    def _send_message(self, message, base_log_level=0, method='get', params=None, data=None):
        """Send API request.

        Args:
            method (str): HTTP method (get, post, delete, etc.)
            params (Optional[dict]): HTTP request parameters
            data (Optional[str]): JSON-encoded string payload for POST

        Returns:
            dict/list: JSON response

        """
        self.log_info(f'Sending {message} to server', base_log_level + 2)
        url = message
        # try:
        self.resp = self.session.request(method, url, params=params, data=data,
                                         headers=self.auth, timeout=self.timeout)
        # except requests.exceptions.ReadTimeout as e:
        #     self.resp = False
        #     return False
        self.log_info(f'received response: {self.resp.text}', base_log_level + 1)
        if self.resp.status_code == 200:
            self.resp = self.resp.json()
            return True
        else:
            return False

    def _get_price(self):
        message = f'{self.url}/prices'
        self._tear_down_request('_get_price', message, base_log_level=2)
        return self.resp

    def _get_currencies(self):
        message = f'{self.url}/currencies'
        self._tear_down_request('_get_currencies', message, base_log_level=2)
        return self.resp

    def _extract_markets(self):
        if self._get_price():
            self.log_info('****extract_markets is done successfully', 1)
            all_info = self.resp['data']
            return all_info
        else:
            self.log_info('!!!!extract_markets is failed.', 1)
            return None

    def _extract_currencies(self):
        if self._get_currencies():
            self.log_info('****extract_currencies is done successfully', 1)
            all_info = self.resp['data']
            return {info['symbol']: {item: info[item] for item in ['id', 'show_precision']} for info in
                    all_info}
        else:
            self.log_info('!!!!extract_markets is failed.', 1)
            return None

    def _buys_book(self, pair_id):
        url_new = self.url.replace('ramzinex.com', 'publicapi.ramzinex.com')
        # url_new = self.url
        message = f'{url_new}/orderbooks/{pair_id}/buys'
        self._tear_down_request('_buys_book', message, base_log_level=2)
        return self.resp

    def _sells_book(self, pair_id):
        url_new = self.url.replace('ramzinex.com', 'publicapi.ramzinex.com')
        # url_new = self.url
        message = f'{url_new}/orderbooks/{pair_id}/sells'
        self._tear_down_request('_sells_book', message, base_log_level=2)
        return self.resp

    def order_book(self, market):
        """
        return the order book of requested market

        :param market: a string for market, e.g., 'btcirr' or 'ethusdt'
        :return: a dictionary with two keys: 'buys' and 'sells' orders
        """
        assert market in self.markets.keys(), f'invalid market: {market}'
        pair_id = self.markets[market]['pair_id']
        buys = self._buys_book(pair_id)
        sells = self._sells_book(pair_id)
        if 'data' in buys and 'data' in sells:
            self.resp = {
                'buys': buys['data'],
                'sells': sells['data'],
            }
            return self.resp
        else:
            raise ValueError('Ramzinex order book is not available.')

    def order_book_buys(self, market):
        """
        return the order book of requested market only buys
        :param market: a string for market, e.g., 'btcirr' or 'ethusdt'
        :return: a dictionary with one key: 'buys' orders
        """
        assert market in self.markets.keys(), f'invalid market: {market}'
        pair_id = self.markets[market]['pair_id']
        buys = self._buys_book(pair_id)
        if 'data' in buys:
            self.resp = {
                'buys': buys['data'],
            }
            return self.resp
        else:
            ValueError('Ramzinex order book is not available.')

    def order_book_sells(self, market):
        """
        return the order book of requested market only sells
        :param market: a string for market, e.g., 'btcirr' or 'ethusdt'
        :return: a dictionary with one key: 'sells' orders
        """
        assert market in self.markets.keys(), f'invalid market: {market}'
        pair_id = self.markets[market]['pair_id']
        sells = self._sells_book(pair_id)
        if 'data' in sells:
            self.resp = {
                'sells': sells['data'],
            }
            return self.resp
        else:
            ValueError('Ramzinex order book is not available.')


class RamzinexPrivate(RamzinexPublic):
    def __init__(self, token, verbose=0):
        super().__init__(verbose)
        self.auth = {'Authorization': 'Bearer ' + token}

    def total_fund(self, currency):
        assert currency in self.currencies.keys(), f'invalid currency: {currency}'
        message = f"{self.url}/users/me/funds/total/currency/{self.currencies[currency]['id']}"
        self._tear_down_request('total_fund', message)
        return self.resp

    def available_fund(self, currency):
        assert currency in self.currencies.keys(), f'invalid currency: {currency}'
        message = f"{self.url}/users/me/funds/available/currency/{self.currencies[currency]['id']}"
        self._tear_down_request('available_fund', message)
        return self.resp

    def in_order_fund(self, currency):
        assert currency in self.currencies.keys(), f'invalid currency: {currency}'
        message = f"{self.url}/users/me/funds/in_orders/currency/{self.currencies[currency]['id']}"
        self._tear_down_request('in_order_fund', message)
        return self.resp

    def detailed_fund(self, currency):
        assert currency in self.currencies.keys(), f'invalid currency: {currency}'
        message = f"{self.url}/users/me/funds/details/currency/{self.currencies[currency]['id']}"
        self._tear_down_request('detailed_fund', message)
        return self.resp

    def detailed_all_funds(self):
        message = f"{self.url}/users/me/funds/details"
        self._tear_down_request('detailed_all_funds', message)
        return self.resp

    def rial_equ_funds(self):
        message = f"{self.url}/users/me/funds/rial_equivalent"
        self._tear_down_request('detailed_all_funds', message)
        return self.resp

    def usdt_equ_funds(self):
        message = f"{self.url}/users/me/funds/usdt_equivalent"
        self._tear_down_request('detailed_all_funds', message)
        return self.resp

    def submit_order(self, market, amount, price, order_type):
        assert market in self.markets.keys(), f'invalid market: {market}'
        assert order_type in ['buy', 'sell'], f'invalid order type: {order_type}'

        param = {
            'pair_id': int(self.markets[market]['pair_id']),
            'amount': amount,
            'price': price,
            'type': order_type,
        }
        message = f"{self.url}/users/me/orders/limit"
        self._tear_down_request('submit_order', message, params=param, method='post')
        return self.resp

    def cancel_order(self, order_id):
        message = f"{self.url}/users/me/orders/{order_id}/cancel"
        self._tear_down_request('cancel_order', message, method='post')
        return self.resp

    def order_status(self, order_id):
        message = f"{self.url}/users/me/orders2/{order_id}"
        self._tear_down_request('order_status', message, method='get')
        return self.resp

    def get_user_order(self, limit, offset, types, markets, currencies, states, is_buy):
        """
        return the status of specified orders

        :param limit: integer, number of requested orders
        :param offset: integer, offset of requested orders
        :param types: array of integer, 1: limit, 2: market
        :param markets: array of strings, market pairs
        :param currencies: array of strings, 'btc', 'irr', ...
        :param states: arrays of integer, 1: open, 3: 100% filled, 4: canceled
        :param is_buy: boolean
        :return:
        """
        param = {
            'limit': limit,
            'offset': offset,
            'types': types,
            'pairs': [self.markets[market]['pair_id'] for market in markets],
            'currencies': [self.currencies[currency]['id'] for currency in currencies],
            'states': states,
            'is_buy': is_buy,
        }
        message = f"{self.url}/users/me/orders2"
        self._tear_down_request('get_user_order', message, data=json.dumps(param), method='post')
        return self.resp

    # def cancel_all_orders(self):
    #     """
    #     Cancel the last 50 orders if they are open
    #     :return:
    #     """
    #     resp = self.get_user_order(10, 2, [], [], [], [], False)
    #     if 'data' in resp:
    #         open_orders = [data['id'] for data in resp['data'] if data['status_id'] == 1]
    #         for order_id in open_orders:
    #             self.cancel_order(order_id)
    #             self.log_info(f'{order_id} is cancelled.', self.verbose)
    #         return 1
    #     else:
    #         self.log_info('user order is not accessible.', self.verbose + 1)
    #         return 0

    def currency_deposit_list(self, currency):
        assert currency in self.currencies.keys(), f'invalid currency: {currency}'
        message = f"{self.url}/users/me/funds/deposits/currency/{self.currencies[currency]['id']}"
        self._tear_down_request('currency_deposit_list', message, method='get')
        return self.resp

    def withdraws_list(self, limit, currency):
        assert currency in self.currencies.keys(), f'invalid currency: {currency}'
        param = {
            'currency_id': self.currencies[currency]['id'],
            'limit': limit
        }

        message = f"{self.url}/users/me/funds/withdraws"
        self._tear_down_request('withdraws_list', message, method='get', params=param)
        return self.resp

    def submit_withdraw_request(self, currency, param):
        assert 'amount' in param, f'amount key is required in param input'
        assert 'address' in param, f'address key is required in param input'
        assert 'network_id' in param, f'network_id key is required in param input'
        assert currency in self.currencies.keys(), f'invalid currency: {currency}'
        param['currency_id'] = self.currencies[currency]['id']

        param['no_tag'] = True if 'tag' in param else False
        message = f"{self.url}/users/me/funds/withdraws/currency/{param['currency_id']}"
        self._tear_down_request('submit_withdraw_request', message, data=json.dumps(param), method='post')
        return self.resp

    def get_turnover(self, days=30):
        param = {
            'readable': 0,
            'days': days
        }
        message = f"{self.url}/users/me/orders/turnover"
        self._tear_down_request('turnover', message, params=param, method='GET')
        return self.resp
