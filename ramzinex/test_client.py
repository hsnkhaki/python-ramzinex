from unittest import TestCase

from ramzinex.client import RamzinexPrivate, RamzinexPublic




class test_RamzinexPublic(TestCase):
    ramzinex_user = RamzinexPrivate('01GiA0zR4m31N3xNYkFefoN6CYvpr5ueFDnj4R404CC3L3r4t0r99f5b24646250675e8bcb92c49fed7ab')

    url = 'SOME URL'

    headers = {
        'User-Agent': 'pmd_BvyAUCoMdWRwc4iYOOsrN1ENrsvzwv53owBCLiIwYiI-1635230880-0-gqNtZGzNAmWjcnBszQsl',
        # 'From': 'youremail@domain.com'  # This is another valid field
    }

    response = requests.get(url, headers=headers)


    def test_order_book(self):
        resp = self.ramzinex_user.order_book('btcirr')
        self.assertTrue('buys' in resp and 'sells' in resp)

    def test_order_book_buy(self):
        resp = self.ramzinex_user.order_book_buys('btcirr')
        self.assertTrue('buys' in resp)

    def test_order_book_sell(self):
        resp = self.ramzinex_user.order_book_sells('btcirr')
        self.assertTrue('sells' in resp)

    def test_get_available_balance(self):
        resp = self.ramzinex_user.available_fund('btc')
        print(resp)
        self.assertTrue('sells' in resp)
