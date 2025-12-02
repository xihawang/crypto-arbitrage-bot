from exchanges.binance import Binance
from exchanges.coinbase import Coinbase
from exchanges.kraken import Kraken

class ArbitrageBot:
    def __init__(self):
        self.exchanges = {
            'binance': Binance(),
            'coinbase': Coinbase(),
            'kraken': Kraken()
        }

    def get_prices(self, symbol):
        prices = {}
        for name, exchange in self.exchanges.items():
            prices[name] = exchange.get_price(symbol)
        return prices

    def find_arbitrage_opportunity(self, symbol):
        prices = self.get_prices(symbol)
        max_price = max(prices.values())
        min_price = min(prices.values())

        if max_price > min_price:
            for exchange, price in prices.items():
                if price == max_price:
                    sell_exchange = exchange
                if price == min_price:
                    buy_exchange = exchange
            return buy_exchange, sell_exchange, min_price, max_price
        return None

    def execute_arbitrage(self, symbol):
        opportunity = self.find_arbitrage_opportunity(symbol)
        if opportunity:
            buy_exchange, sell_exchange, buy_price, sell_price = opportunity
            # Execute buy and sell logic here
            print(f"Buying {symbol} on {buy_exchange} at {buy_price} and selling on {sell_exchange} at {sell_price}")
        else:
            print("No arbitrage opportunity found.")

# Example usage
if __name__ == "__main__":
    bot = ArbitrageBot()
    bot.execute_arbitrage('BTC/USD')  # Replace with the desired trading pair