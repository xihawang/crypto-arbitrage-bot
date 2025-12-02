"""
当前市场价格获取器 - 基于2024年12月真实市场价格的模拟数据
"""

import asyncio
import random
import time
from datetime import datetime
from typing import Dict, List
from src.utils.logger import logger


class CurrentMarketPriceFetcher:
    """基于当前市场真实价格的获取器"""

    def __init__(self):
        # 2024年12月的最新市场价格 (更新至当前)
        self.base_prices = {
            "BTC": 102000,   # ~$102,000 (当前市场价格)
            "ETH": 3800,     # ~$3,800
            "SOL": 245,      # ~$245
            "USDT": 1.001,   # ~$1.001 (略有溢价)
            "USDC": 1.000    # ~$1.000
        }

        self.exchanges = ["binance", "coinbase", "okx", "bybit", "bitget", "kraken"]

    async def fetch_all_prices_for_crypto(self, crypto: str) -> Dict[str, float]:
        """获取指定币种在多个交易所的价格"""
        base_price = self.base_prices.get(crypto, 100)

        # 为不同交易所生成基于真实市场的价格差异
        prices = {}
        for exchange in self.exchanges:
            # 基于真实交易所的价格差异模式
            if exchange == "binance":
                # 币安通常流动性最好，价格最接近基准
                variation = random.uniform(-0.001, 0.002)
            elif exchange == "coinbase":
                # Coinbase 通常对散户有少量溢价
                variation = random.uniform(0.001, 0.004)
            elif exchange == "okx":
                # OKX 在亚洲市场活跃，可能有轻微折价
                variation = random.uniform(-0.003, 0.001)
            elif exchange == "bybit":
                # Bybit 衍生品为主，现货价格略有波动
                variation = random.uniform(-0.002, 0.003)
            elif exchange == "bitget":
                # Bitget 新兴交易所，价格波动稍大
                variation = random.uniform(-0.004, 0.004)
            elif exchange == "kraken":
                # Kraken 欧美用户多，通常价格略低
                variation = random.uniform(-0.003, 0.001)

            price = base_price * (1 + variation)

            # 特殊处理稳定币，反映真实的微小价差
            if crypto in ["USDT", "USDC"]:
                if exchange == "kraken":
                    # Kraken 稳定币通常有轻微折价
                    price = random.uniform(0.999, 1.001)
                elif exchange == "coinbase":
                    # Coinbase 稳定币通常有轻微溢价
                    price = random.uniform(1.000, 1.003)
                else:
                    # 其他交易所价格接近1:1
                    price = random.uniform(0.999, 1.002)

            prices[exchange] = round(price, 4 if crypto in ["USDT", "USDC"] else 2)

        return prices

    async def fetch_all_prices(self, cryptos: List[str]) -> Dict[str, Dict[str, float]]:
        """获取所有币种的价格"""
        logger.info(f"🔍 基于当前市场生成 {len(cryptos)} 个币种的价格...")

        all_prices = {}
        for crypto in cryptos:
            # 模拟网络延迟
            await asyncio.sleep(random.uniform(0.1, 0.3))

            prices = await self.fetch_all_prices_for_crypto(crypto)
            all_prices[crypto] = prices

            if prices:
                min_price = min(prices.values())
                max_price = max(prices.values())
                spread = ((max_price - min_price) / min_price) * 100
                logger.info(f"✅ {crypto}: ${min_price:,.2f} - ${max_price:,.2f} (价差: {spread:.3f}%)")
            else:
                logger.warning(f"❌ {crypto}: 无价格数据")

        return all_prices

    def analyze_price_diff(self, crypto: str, prices: Dict[str, float]) -> Dict:
        """分析价格差异"""
        if not prices or len(prices) < 2:
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

        # 对于稳定币，使用更低的套利阈值
        threshold = 0.05 if crypto in ["USDT", "USDC"] else 0.15
        arbitrage_possible = diff_rate >= threshold

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

    def get_all_opportunities(self, cryptos: List[str], prices: Dict[str, Dict[str, float]]) -> List[Dict]:
        """获取所有套利机会"""
        opportunities = []

        for crypto in cryptos:
            if crypto in prices and prices[crypto]:
                analysis = self.analyze_price_diff(crypto, prices[crypto])
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
current_market_price_fetcher = CurrentMarketPriceFetcher()


async def get_current_market_prices(cryptos: List[str]) -> Dict[str, Dict[str, float]]:
    """获取当前市场价格的便捷函数"""
    return await current_market_price_fetcher.fetch_all_prices(cryptos)


if __name__ == "__main__":
    # 测试代码
    async def test():
        cryptos = ["BTC", "ETH", "SOL", "USDT", "USDC"]
        prices = await current_market_price_fetcher.fetch_all_prices(cryptos)

        print("\n=== 当前市场价格分析 ===")
        for crypto, crypto_prices in prices.items():
            if crypto_prices:
                analysis = current_market_price_fetcher.analyze_price_diff(crypto, crypto_prices)
                print(f"\n{crypto}:")
                print(f"  价格区间: ${analysis.get('min_price'):,.2f} - ${analysis.get('max_price'):,.2f}")
                print(f"  价差: {analysis.get('diff_rate', 0):.3f}%")
                print(f"  套利机会: {'✅' if analysis.get('arbitrage_possible') else '❌'}")
                if analysis.get('arbitrage_possible'):
                    print(f"  建议: {analysis.get('min_exchange')} 买入 → {analysis.get('max_exchange')} 卖出")

        opportunities = current_market_price_fetcher.get_all_opportunities(cryptos, prices)
        print(f"\n🚀 发现 {len(opportunities)} 个套利机会:")
        for i, opp in enumerate(opportunities, 1):
            print(f"  {i}. {opp['crypto']}: {opp['diff_rate']:.3f}% 利润 (${opp['potential_profit']:.2f})")

    asyncio.run(test())