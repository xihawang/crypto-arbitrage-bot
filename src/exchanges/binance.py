import ccxt

class BinanceExchange:
    def __init__(self, api_key, api_secret):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
        })

    def fetch_markets(self):
        return self.exchange.load_markets()

    def fetch_ticker(self, symbol):
        return self.exchange.fetch_ticker(symbol)

    def create_order(self, symbol, order_type, side, amount, price=None):
        if order_type == 'limit':
            return self.exchange.create_limit_order(symbol, side, amount, price)
        elif order_type == 'market':
            return self.exchange.create_market_order(symbol, side, amount)
        else:
            raise ValueError("Invalid order type")

    def fetch_balance(self):
        return self.exchange.fetch_balance()