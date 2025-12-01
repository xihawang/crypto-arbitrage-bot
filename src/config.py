import os

class Config:
    def __init__(self):
        self.API_KEYS = {
            'binance': os.getenv('BINANCE_API_KEY'),
            'coinbase': os.getenv('COINBASE_API_KEY'),
            'kraken': os.getenv('KRAKEN_API_KEY')
        }
        self.EXCHANGE_URLS = {
            'binance': 'https://api.binance.com',
            'coinbase': 'https://api.coinbase.com',
            'kraken': 'https://api.kraken.com'
        }
        self.TRADE_SETTINGS = {
            'slippage': 0.01,
            'min_profit': 0.01
        }
        self.LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')

config = Config()