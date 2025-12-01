import unittest
from src.strategies.arbitrage import ArbitrageStrategy

class TestArbitrageStrategy(unittest.TestCase):

    def setUp(self):
        self.strategy = ArbitrageStrategy()

    def test_detect_arbitrage_opportunity(self):
        # Mock data for testing
        prices = {
            'exchange_1': 100,
            'exchange_2': 95
        }
        opportunity = self.strategy.detect_arbitrage_opportunity(prices)
        self.assertTrue(opportunity)
        self.assertEqual(opportunity['profit'], 5)

    def test_no_arbitrage_opportunity(self):
        # Mock data for testing
        prices = {
            'exchange_1': 100,
            'exchange_2': 100
        }
        opportunity = self.strategy.detect_arbitrage_opportunity(prices)
        self.assertIsNone(opportunity)

    def test_execute_arbitrage_trade(self):
        # Mock data for testing
        trade_details = {
            'buy_exchange': 'exchange_2',
            'sell_exchange': 'exchange_1',
            'amount': 1
        }
        result = self.strategy.execute_arbitrage_trade(trade_details)
        self.assertTrue(result['success'])
        self.assertEqual(result['profit'], 5)

if __name__ == '__main__':
    unittest.main()