"""
公开价格获取器 - 使用公开API端点获取价格
不需要API密钥，用于演示功能
"""

import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, List
from src.utils.logger import logger


class PublicPriceFetcher:
    """公开价格获取器 - 使用免费API"""

    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_binance_price(self, crypto: str) -> float:
        """获取币安价格（公开API）"""
        try:
            symbol = f"{crypto.lower()}usdt"
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"

            async with self.session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data["price"])
        except Exception as e:
            logger.debug(f"币安 {crypto} 价格获取失败: {e}")
        return None

    async def fetch_coinbase_price(self, crypto: str) -> float:
        """获取Coinbase价格（公开API）"""
        try:
            url = f"https://api.coinbase.com/v2/exchange-rates?currency={crypto}"

            async with self.session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data["data"]["rates"]["USD"])
        except Exception as e:
            logger.debug(f"Coinbase {crypto} 价格获取失败: {e}")
        return None

    async def fetch_coingecko_price(self, crypto: str) -> float:
        """获取CoinGecko价格（公开API）"""
        try:
            coin_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
                "USDT": "tether",
                "USDC": "usd-coin"
            }

            coin_id = coin_map.get(crypto.upper())
            if not coin_id:
                return None

            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

            async with self.session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data[coin_id]["usd"])
        except Exception as e:
            logger.debug(f"CoinGecko {crypto} 价格获取失败: {e}")
        return None

    async def fetch_binance_avg_price(self, crypto: str) -> float:
        """获取币安平均价格（备用API）"""
        try:
            symbol = f"{crypto.upper()}USDT"
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"

            async with self.session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data["lastPrice"])
        except Exception as e:
            logger.debug(f"币安平均价格 {crypto} 获取失败: {e}")
        return None

    async def fetch_all_prices_for_crypto(self, crypto: str) -> Dict[str, float]:
        """获取指定币种在多个源的价格"""
        sources = {
            "binance": self.fetch_binance_price,
            "coinbase": self.fetch_coinbase_price,
            "coingecko": self.fetch_coingecko_price,
            "binance_avg": self.fetch_binance_avg_price
        }

        tasks = []
        for name, fetcher in sources.items():
            task = asyncio.create_task(fetcher(crypto))
            tasks.append((name, task))

        results = {}
        for name, task in tasks:
            try:
                price = await task
                if price and price > 0:
                    results[name] = price
                    logger.info(f"✅ {name}: {crypto} = ${price:,.2f}")
            except Exception as e:
                logger.debug(f"❌ {name}: {crypto} 错误 - {e}")

        return results

    async def fetch_all_prices(self, cryptos: List[str]) -> Dict[str, Dict[str, float]]:
        """获取所有币种的价格"""
        logger.info(f"🔍 获取 {len(cryptos)} 个币种的价格...")

        all_prices = {}
        tasks = []

        for crypto in cryptos:
            task = asyncio.create_task(self.fetch_all_prices_for_crypto(crypto))
            tasks.append((crypto, task))

        for crypto, task in tasks:
            try:
                prices = await task
                all_prices[crypto] = prices
                count = len(prices)
                logger.info(f"✅ {crypto}: {count} 个价格源")
            except Exception as e:
                logger.error(f"❌ {crypto} 价格获取失败: {e}")
                all_prices[crypto] = {}

        return all_prices

    def analyze_price_diff(self, crypto: str, prices: Dict[str, float] = None) -> Dict:
        """分析价格差异"""
        if prices is None:
            if not hasattr(self, '_last_prices') or not self._last_prices.get(crypto):
                return {"status": "error", "message": f"没有找到 {crypto} 的价格数据"}
            prices = self._last_prices[crypto]

        if len(prices) < 2:
            return {
                "status": "error",
                "message": f"{crypto} 价格数据不足"
            }

        # 计算价格差异
        max_price = max(prices.values())
        min_price = min(prices.values())
        price_diff = max_price - min_price
        diff_rate = (price_diff / min_price) * 100

        # 找出最高和最低价格的交易所
        max_exchange = None
        min_exchange = None

        for exchange, price in prices.items():
            if price == max_price:
                max_exchange = exchange
            if price == min_price:
                min_exchange = exchange

        arbitrage_possible = diff_rate >= 0.5  # 0.5%以上显示为机会

        return {
            "status": "success",
            "crypto": crypto,
            "prices": prices,
            "max_price": max_price,
            "min_price": min_price,
            "max_exchange": max_exchange,
            "min_exchange": min_exchange,
            "price_diff": price_diff,
            "diff_rate": round(diff_rate, 3),
            "arbitrage_possible": arbitrage_possible,
            "timestamp": datetime.now().isoformat()
        }


# 全局实例
public_price_fetcher = PublicPriceFetcher()


async def get_public_prices(cryptos: List[str]) -> Dict[str, Dict[str, float]]:
    """获取公开价格的便捷函数"""
    async with public_price_fetcher as fetcher:
        return await fetcher.fetch_all_prices(cryptos)


if __name__ == "__main__":
    # 测试代码
    async def test():
        cryptos = ["BTC", "ETH", "SOL"]
        async with PublicPriceFetcher() as fetcher:
            prices = await fetcher.fetch_all_prices(cryptos)
            for crypto, crypto_prices in prices.items():
                if crypto_prices:
                    analysis = fetcher.analyze_price_diff(crypto, crypto_prices)
                    print(f"\n{crypto} 分析:")
                    print(f"价格: {crypto_prices}")
                    print(f"差价率: {analysis.get('diff_rate', 0):.3f}%")
                    print(f"套利机会: {'是' if analysis.get('arbitrage_possible') else '否'}")

    asyncio.run(test())