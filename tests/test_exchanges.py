import unittest
from src.exchanges.binance import BinanceExchange
from src.exchanges.coinbase import CoinbaseExchange
from src.exchanges.kraken import KrakenExchange

class TestExchanges(unittest.TestCase):

    def setUp(self):
        self.binance = BinanceExchange()
        self.coinbase = CoinbaseExchange()
        self.kraken = KrakenExchange()

    def test_binance_get_market_data(self):
        market_data = self.binance.get_market_data()
        self.assertIsNotNone(market_data)
        self.assertIn('BTCUSDT', market_data)

    def test_coinbase_get_market_data(self):
        market_data = self.coinbase.get_market_data()
        self.assertIsNotNone(market_data)
        self.assertIn('BTC-USD', market_data)

    def test_kraken_get_market_data(self):
        market_data = self.kraken.get_market_data()
        self.assertIsNotNone(market_data)
        self.assertIn('XXBTZUSD', market_data)

    def test_binance_execute_trade(self):
        result = self.binance.execute_trade('BTCUSDT', 0.01, 'buy')
        self.assertTrue(result['success'])

    def test_coinbase_execute_trade(self):
        result = self.coinbase.execute_trade('BTC-USD', 0.01, 'buy')
        self.assertTrue(result['success'])

    def test_kraken_execute_trade(self):
        result = self.kraken.execute_trade('XXBTZUSD', 0.01, 'buy')
        self.assertTrue(result['success'])

if __name__ == '__main__':
    unittest.main()