"""
跨交易所套利策略
在不同交易所之间寻找同一资产的价格差异，低买高卖获利
"""

from src.exchanges.binance import Binance
from src.exchanges.coinbase import Coinbase
from src.exchanges.kraken import Kraken
from src.utils.price_fetcher import PriceFetcher
from src.utils.logger import setup_logger
from src.config import ARBITRAGE_THRESHOLD

logger = setup_logger("arbitrage")


class ArbitrageBot:
    """跨交易所套利机器人"""
    
    def __init__(self):
        self.exchanges = {
            'binance': Binance(),
            'coinbase': Coinbase(),
            'kraken': Kraken()
        }
        self.price_fetcher = PriceFetcher()
    
    def get_prices(self, symbol):
        """
        从所有交易所获取价格
        
        Args:
            symbol: 交易对符号 (如: "BTC", "ETH", "SOL")
        
        Returns:
            {exchange_name: price} 格式的价格字典
        """
        try:
            prices = self.price_fetcher.get_price_from_all_exchanges(symbol)
            if prices:
                logger.info(f"✅ 获取 {symbol} 价格: {len(prices)} 个交易所")
            return prices
        except Exception as e:
            logger.error(f"❌ 获取 {symbol} 价格失败: {str(e)}")
            return {}
    
    def find_arbitrage_opportunity(self, symbol):
        """
        寻找套利机会
        
        Args:
            symbol: 交易对符号
        
        Returns:
            (buy_exchange, sell_exchange, min_price, max_price, profit_rate) 或 None
        """
        prices = self.get_prices(symbol)
        
        if not prices or len(prices) < 2:
            return None
        
        max_price = max(prices.values())
        min_price = min(prices.values())
        profit_rate = ((max_price - min_price) / min_price) * 100
        
        # 检查是否超过套利阈值
        if profit_rate < ARBITRAGE_THRESHOLD:
            return None
        
        sell_exchange = None
        buy_exchange = None
        
        for exchange, price in prices.items():
            if price == max_price:
                sell_exchange = exchange
            if price == min_price:
                buy_exchange = exchange
        
        logger.info(f"🚨 发现 {symbol} 套利机会: {buy_exchange}(${min_price:.2f}) -> {sell_exchange}(${max_price:.2f}), 利润率: {profit_rate:.3f}%")
        
        return buy_exchange, sell_exchange, min_price, max_price, profit_rate
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