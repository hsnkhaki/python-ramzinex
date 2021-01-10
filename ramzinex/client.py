import requests
import logging
logging.basicConfig(level=logging.INFO)


class RamzinexPublic:
    def __init__(self, verbose=0):
        """

        :param api:
        :param verbose: 0 no log, 1 log responses only, 2 log responses and messages
        """
        self.verbose = verbose
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
        self.resp = self.session.request(method, url, params=params, data=data,
                                         headers=self.auth, timeout=30)
        self.log_info(f'received response: {self.resp.text}', base_log_level + 1)
        if self.resp.status_code == 200:
            self.resp = self.resp.json()
            return True
        else:
            return False

    def _get_price(self):
        url = 'https://ramzinex.com/exchange/api/exchange/prices'
        message = f'{url}'
        self._tear_down_request('_get_price', message, base_log_level=2)
        return self.resp

    def _get_currencies(self):
        url = 'https://ramzinex.com/exchange/api/exchange/prices'
        message = f'{self.url}/currencies'
        self._tear_down_request('_get_currencies', message, base_log_level=2)
        return self.resp

    def _extract_markets(self):
        if self._get_price():
            self.log_info('****extract_markets is done successfully', 1)
            all_info = self.resp['original']
            return {market: {item: info[item] for item in ['pair_id', 'financial']} for market, info in
                    all_info.items()}
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
        message = f'{self.url}/orderbooks/{pair_id}/buys'
        self._tear_down_request('_buys_book', message, base_log_level=2)
        return self.resp

    def _sells_book(self, pair_id):
        message = f'{self.url}/orderbooks/{pair_id}/sells'
        self._tear_down_request('_sells_book', message, base_log_level=2)
        return self.resp

    def order_book(self, market):
        """
        return the order book of requested market

        :param market: a lowercase string for market, e.g., 'btcirr' or 'ethusdt'
        :return: a dictionary with two keys: 'buys' and 'sells' orders
        """
        assert market in self.markets.keys(), f'invalid market: {market}'
        pair_id = self.markets[market]['pair_id']
        buys = self._buys_book(pair_id)
        sells = self._sells_book(pair_id)
        if 'data' in buys:
            self.resp = {
                'buys': buys['data'],
                'sells': sells['data'],
            }
            return self.resp
        else:
            return 0


    def order_book_buys(self, market):
        """
        return the order book of requested market only buys
        :param market: a lowercase string for market, e.g., 'btcirr' or 'ethusdt'
        :return: a dictionary with one key: 'buys' orders
        """
        assert market in self.markets.keys(), f'invalid market: {market}'
        pair_id = self.markets[market]['pair_id']
        buys = self._buys_book(pair_id)
        self.resp = {
            'buys': buys['data'],
        }
        return self.resp


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

    def order_status(self, order_id):
        message = f"{self.url}/users/me/orders2/{order_id}"
        self._tear_down_request('in_order_fund', message)

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