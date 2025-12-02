"""
演示价格获取器 - 生成模拟价格数据
用于演示套利系统功能
"""

import asyncio
import random
import time
from datetime import datetime
from typing import Dict, List
from src.utils.logger import logger


class DemoPriceFetcher:
    """演示价格获取器 - 生成模拟价格数据"""

    def __init__(self):
        # 基准价格
        self.base_prices = {
            "BTC": 95000,
            "ETH": 3500,
            "SOL": 180,
            "USDT": 1.0,
            "USDC": 1.0
        }

        # 交易所列表
        self.exchanges = ["binance", "coinbase", "okx", "bybit", "bitget", "kraken"]

    async def fetch_all_prices_for_crypto(self, crypto: str) -> Dict[str, float]:
        """生成指定币种在多个交易所的模拟价格"""
        base_price = self.base_prices.get(crypto, 100)

        # 为每个交易所生成略微不同的价格
        prices = {}
        for exchange in self.exchanges:
            # 添加随机价格差异 ±0.5%
            variation = random.uniform(-0.005, 0.005)
            price = base_price * (1 + variation)

            # 特殊处理稳定币
            if crypto in ["USDT", "USDC"]:
                price = random.uniform(0.998, 1.002)

            prices[exchange] = round(price, 2 if crypto != "USDT" and crypto != "USDC" else 4)

        return prices

    async def fetch_all_prices(self, cryptos: List[str]) -> Dict[str, Dict[str, float]]:
        """生成所有币种的模拟价格"""
        logger.info(f"🔍 生成 {len(cryptos)} 个币种的模拟价格...")

        all_prices = {}
        for crypto in cryptos:
            # 模拟网络延迟
            await asyncio.sleep(random.uniform(0.1, 0.3))

            prices = await self.fetch_all_prices_for_crypto(crypto)
            all_prices[crypto] = prices

            count = len(prices)
            logger.info(f"✅ {crypto}: {count} 个交易所价格")

        return all_prices

    def analyze_price_diff(self, crypto: str, prices: Dict[str, float] = None) -> Dict:
        """分析价格差异"""
        if prices is None:
            return {"status": "error", "message": f"没有找到 {crypto} 的价格数据"}

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

        # 对于稳定币，降低套利阈值
        threshold = 0.1 if crypto in ["USDT", "USDC"] else 0.5
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

    def get_all_opportunities(self, cryptos: List[str], prices: Dict[str, Dict[str, float]] = None) -> List[Dict]:
        """获取所有套利机会"""
        if prices is None:
            return []

        opportunities = []

        for crypto in cryptos:
            if crypto in prices:
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
demo_price_fetcher = DemoPriceFetcher()


async def get_demo_prices(cryptos: List[str]) -> Dict[str, Dict[str, float]]:
    """获取演示价格的便捷函数"""
    return await demo_price_fetcher.fetch_all_prices(cryptos)


async def get_demo_opportunities(cryptos: List[str]) -> List[Dict]:
    """获取演示套利机会的便捷函数"""
    prices = await demo_price_fetcher.fetch_all_prices(cryptos)
    return demo_price_fetcher.get_all_opportunities(cryptos, prices)


if __name__ == "__main__":
    # 测试代码
    async def test():
        cryptos = ["BTC", "ETH", "SOL"]
        prices = await demo_price_fetcher.fetch_all_prices(cryptos)

        for crypto, crypto_prices in prices.items():
            analysis = demo_price_fetcher.analyze_price_diff(crypto, crypto_prices)
            print(f"\n{crypto} 分析:")
            print(f"价格: {crypto_prices}")
            print(f"差价率: {analysis.get('diff_rate', 0):.3f}%")
            print(f"套利机会: {'是' if analysis.get('arbitrage_possible') else '否'}")
            if analysis.get('arbitrage_possible'):
                print(f"建议: {analysis.get('min_exchange')} 买入, {analysis.get('max_exchange')} 卖出")

        opportunities = demo_price_fetcher.get_all_opportunities(cryptos, prices)
        print(f"\n🚀 发现 {len(opportunities)} 个套利机会:")
        for opp in opportunities:
            print(f"  {opp['crypto']}: {opp['diff_rate']:.3f}% 利润")

    asyncio.run(test())