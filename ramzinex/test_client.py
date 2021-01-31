from unittest import TestCase

from ramzinex.client import RamzinexPrivate, RamzinexPublic


class test_RamzinexPublic(TestCase):
    ramzinex_user = RamzinexPublic()

    def test_order_book(self):
        resp = self.ramzinex_user.order_book('btcirr')
        self.assertTrue('buys' in resp and 'sells' in resp)

    def test_order_book_buy(self):
        resp = self.ramzinex_user.order_book_buys('btcirr')
        self.assertTrue('buys' in resp)

    def test_order_book_sell(self):
        resp = self.ramzinex_user.order_book_sells('btcirr')
        self.assertTrue('sells' in resp)

