"""
扩展的价格获取器 - 支持6个主流交易所
新增: OKX, Bybit, Bitget
"""

import requests
import asyncio
import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Optional
from src.utils.logger import logger
from src.config import EXCHANGES


class ExtendedPriceFetcher:
    """扩展价格获取器 - 支持多交易所实时价格"""

    def __init__(self):
        self.session = None
        self.last_prices = {}
        self.price_cache = {}
        self.cache_ttl = 5  # 缓存5秒
        self.last_fetch_time = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _get_symbol_pair(self, crypto: str, exchange: str) -> str:
        """获取交易所对应的交易对"""
        symbol_map = {
            "binance": {
                "BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT",
                "USDT": "USDTUSD", "USDC": "USDCUSDT"
            },
            "coinbase": {
                "BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD",
                "USDT": "USDT-USD", "USDC": "USDC-USD"
            },
            "kraken": {
                "BTC": "XBTUSD", "ETH": "ETHUSD", "SOL": "SOLUSD",
                "USDT": "USDTZ", "USDC": "USDCZ"
            },
            "okx": {
                "BTC": "BTC-USDT", "ETH": "ETH-USDT", "SOL": "SOL-USDT",
                "USDT": "USDT-USDT", "USDC": "USDC-USDT"
            },
            "bybit": {
                "BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT",
                "USDT": "USDTUSDT", "USDC": "USDCUSDT"
            },
            "bitget": {
                "BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT",
                "USDT": "USDTUSDT", "USDC": "USDCUSDT"
            }
        }
        return symbol_map.get(exchange, {}).get(crypto, "")

    async def fetch_binance_price(self, crypto: str) -> Optional[float]:
        """获取币安价格"""
        try:
            symbol = self._get_symbol_pair(crypto, "binance")
            if not symbol:
                return None

            async with self.session.get(
                f"https://api.binance.com/api/v3/ticker/price",
                params={"symbol": symbol},
                timeout=5
            ) as response:
                data = await response.json()
                return float(data["price"])
        except Exception as e:
            logger.debug(f"币安 {crypto} 价格获取失败: {e}")
            return None

    async def fetch_coinbase_price(self, crypto: str) -> Optional[float]:
        """获取Coinbase价格"""
        try:
            symbol = self._get_symbol_pair(crypto, "coinbase")
            if not symbol:
                return None

            async with self.session.get(
                f"https://api.coinbase.com/v2/exchange-rates",
                params={"currency": crypto},
                timeout=5
            ) as response:
                data = await response.json()
                return float(data["data"]["rates"]["USD"])
        except Exception as e:
            logger.debug(f"Coinbase {crypto} 价格获取失败: {e}")
            return None

    async def fetch_okx_price(self, crypto: str) -> Optional[float]:
        """获取OKX价格"""
        try:
            symbol = self._get_symbol_pair(crypto, "okx")
            if not symbol:
                return None

            async with self.session.get(
                f"https://www.okx.com/api/v5/market/ticker",
                params={"instId": symbol},
                timeout=5
            ) as response:
                data = await response.json()
                if data.get("code") == "0" and data.get("data"):
                    return float(data["data"][0]["last"])
        except Exception as e:
            logger.debug(f"OKX {crypto} 价格获取失败: {e}")
            return None

    async def fetch_bybit_price(self, crypto: str) -> Optional[float]:
        """获取Bybit价格"""
        try:
            symbol = self._get_symbol_pair(crypto, "bybit")
            if not symbol:
                return None

            async with self.session.get(
                f"https://api.bybit.com/v5/market/tickers",
                params={"category": "spot", "symbol": symbol},
                timeout=5
            ) as response:
                data = await response.json()
                if data.get("retCode") == 0 and data.get("result", {}).get("list"):
                    return float(data["result"]["list"][0]["lastPrice"])
        except Exception as e:
            logger.debug(f"Bybit {crypto} 价格获取失败: {e}")
            return None

    async def fetch_bitget_price(self, crypto: str) -> Optional[float]:
        """获取Bitget价格"""
        try:
            symbol = self._get_symbol_pair(crypto, "bitget")
            if not symbol:
                return None

            async with self.session.get(
                f"https://api.bitget.com/api/v2/spot/market/tickers",
                params={"symbol": symbol},
                timeout=5
            ) as response:
                data = await response.json()
                if data.get("code") == "00000" and data.get("data"):
                    return float(data["data"][0]["lastPr"])
        except Exception as e:
            logger.debug(f"Bitget {crypto} 价格获取失败: {e}")
            return None

    async def fetch_kraken_price(self, crypto: str) -> Optional[float]:
        """获取Kraken价格"""
        try:
            symbol = self._get_symbol_pair(crypto, "kraken")
            if not symbol:
                return None

            async with self.session.get(
                f"https://api.kraken.com/0/public/Ticker",
                params={"pair": symbol},
                timeout=5
            ) as response:
                data = await response.json()
                if data.get("error") == [] and data.get("result"):
                    result_key = list(data["result"].keys())[0]
                    return float(data["result"][result_key]["c"][0])
        except Exception as e:
            logger.debug(f"Kraken {crypto} 价格获取失败: {e}")
            return None

    async def fetch_all_prices_for_crypto(self, crypto: str) -> Dict[str, float]:
        """获取指定币种在所有交易所的价格"""
        exchanges = ["binance", "coinbase", "okx", "bybit", "bitget"]

        fetchers = {
            "binance": self.fetch_binance_price,
            "coinbase": self.fetch_coinbase_price,
            "okx": self.fetch_okx_price,
            "bybit": self.fetch_bybit_price,
            "bitget": self.fetch_bitget_price,
            "kraken": self.fetch_kraken_price
        }

        tasks = []
        for exchange in exchanges:
            if EXCHANGES.get(exchange, {}).get("enabled", False):
                task = asyncio.create_task(fetchers[exchange](crypto))
                tasks.append((exchange, task))

        results = {}
        for exchange, task in tasks:
            try:
                price = await task
                if price and price > 0:
                    results[exchange] = price
                    logger.debug(f"✅ {exchange}: {crypto} = ${price:,.2f}")
                else:
                    logger.debug(f"❌ {exchange}: {crypto} 获取失败")
            except Exception as e:
                logger.debug(f"❌ {exchange}: {crypto} 错误 - {e}")

        return results

    async def fetch_all_prices(self, cryptos: List[str]) -> Dict[str, Dict[str, float]]:
        """获取所有币种在所有交易所的价格"""
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
                logger.info(f"✅ {crypto}: {len(prices)} 个交易所价格")
            except Exception as e:
                logger.error(f"❌ {crypto} 价格获取失败: {e}")
                all_prices[crypto] = {}

        self.last_prices = all_prices
        return all_prices

    def analyze_price_diff(self, crypto: str) -> Dict:
        """分析指定币种的价格差异"""
        if crypto not in self.last_prices:
            return {
                "status": "error",
                "message": f"没有找到 {crypto} 的价格数据"
            }

        prices = self.last_prices[crypto]
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

        arbitrage_possible = diff_rate >= 2.0  # 2%以上才套利

        return {
            "status": "success",
            "crypto": crypto,
            "prices": prices,
            "max_price": max_price,
            "min_price": min_price,
            "max_exchange": max_exchange,
            "min_exchange": min_exchange,
            "price_diff": price_diff,
            "diff_rate": round(diff_rate, 2),
            "arbitrage_possible": arbitrage_possible,
            "timestamp": datetime.now().isoformat()
        }

    def get_all_opportunities(self, cryptos: List[str]) -> List[Dict]:
        """获取所有套利机会"""
        opportunities = []

        for crypto in cryptos:
            analysis = self.analyze_price_diff(crypto)
            if analysis.get("status") == "success" and analysis.get("arbitrage_possible"):
                opportunities.append({
                    "crypto": crypto,
                    "buy_exchange": analysis.get("min_exchange"),
                    "sell_exchange": analysis.get("max_exchange"),
                    "buy_price": analysis.get("min_price"),
                    "sell_price": analysis.get("max_price"),
                    "diff_rate": analysis.get("diff_rate"),
                    "potential_profit": analysis.get("price_diff"),
                    "timestamp": analysis.get("timestamp")
                })

        # 按差价率排序
        opportunities.sort(key=lambda x: x["diff_rate"], reverse=True)
        return opportunities


# 全局实例
extended_price_fetcher = ExtendedPriceFetcher()


async def get_real_time_prices(cryptos: List[str]) -> Dict[str, Dict[str, float]]:
    """获取实时价格的便捷函数"""
    async with extended_price_fetcher as fetcher:
        return await fetcher.fetch_all_prices(cryptos)


async def monitor_opportunities(cryptos: List[str]) -> List[Dict]:
    """监控套利机会的便捷函数"""
    async with extended_price_fetcher as fetcher:
        prices = await fetcher.fetch_all_prices(cryptos)
        return fetcher.get_all_opportunities(cryptos)


if __name__ == "__main__":
    # 测试代码
    async def test():
        cryptos = ["BTC", "ETH", "SOL"]
        async with ExtendedPriceFetcher() as fetcher:
            prices = await fetcher.fetch_all_prices(cryptos)
            for crypto, crypto_prices in prices.items():
                analysis = fetcher.analyze_price_diff(crypto)
                print(f"\n{crypto} 分析:")
                print(f"价格: {crypto_prices}")
                print(f"差价率: {analysis.get('diff_rate', 0):.2f}%")
                print(f"套利机会: {'是' if analysis.get('arbitrage_possible') else '否'}")

    asyncio.run(test())