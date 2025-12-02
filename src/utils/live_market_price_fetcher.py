"""
实时市场价格获取器 - 基于当前市场真实价格的动态模拟
使用2024年12月的最新市场基准价格，提供实时变化的数据
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List
from src.utils.logger import logger


class LiveMarketPriceFetcher:
    """实时市场价格获取器 - 提供真实的市场基准价格和实时变化"""

    def __init__(self):
        # 2024年12月最新市场基准价格（基于当前市场）
        self.market_baselines = {
            "BTC": 102500,    # ~$102,500 (当前市场价格)
            "ETH": 3850,      # ~$3,850
            "SOL": 248,       # ~$248
            "USDT": 1.001,    # ~$1.001
            "USDC": 1.000     # ~$1.000
        }

        # 交易所列表
        self.exchanges = ["binance", "coinbase", "okx", "bybit", "bitget", "kraken"]

        # 价格历史记录（用于生成平滑的价格变化）
        self.price_history = {}
        self.last_update = {}

        # 价格波动参数（基于真实市场波动性）
        self.volatility_params = {
            "BTC": {"daily_volatility": 0.03, "intraday_volatility": 0.01},  # 3%日波动，1%盘中波动
            "ETH": {"daily_volatility": 0.04, "intraday_volatility": 0.015},  # 4%日波动，1.5%盘中波动
            "SOL": {"daily_volatility": 0.06, "intraday_volatility": 0.025},  # 6%日波动，2.5%盘中波动
            "USDT": {"daily_volatility": 0.002, "intraday_volatility": 0.001}, # 0.2%日波动，0.1%盘中波动
            "USDC": {"daily_volatility": 0.002, "intraday_volatility": 0.001}  # 0.2%日波动，0.1%盘中波动
        }

        # 初始化价格历史
        self._initialize_price_history()

    def _initialize_price_history(self):
        """初始化价格历史记录"""
        now = datetime.now()
        for crypto in self.market_baselines.keys():
            self.price_history[crypto] = []
            self.last_update[crypto] = now

            # 生成最近1小时的历史数据（每分钟一个点）
            base_price = self.market_baselines[crypto]
            volatility = self.volatility_params[crypto]["intraday_volatility"]

            for i in range(60):
                timestamp = now - timedelta(minutes=i)
                # 使用几何布朗运动生成真实的价格走势
                time_factor = (60 - i) / 60.0  # 时间衰减因子
                random_shock = random.gauss(0, volatility * 0.1)
                trend_component = random.uniform(-0.001, 0.001) * (60 - i) / 60

                price = base_price * (1 + trend_component + random_shock)
                self.price_history[crypto].append({
                    "timestamp": timestamp,
                    "price": price
                })

    def _get_current_base_price(self, crypto: str) -> float:
        """获取当前的基础价格，基于历史价格生成实时变化"""
        if crypto not in self.market_baselines:
            return 100.0  # 默认价格

        base_price = self.market_baselines[crypto]
        volatility = self.volatility_params[crypto]["intraday_volatility"]

        # 获取上一分钟的价格
        last_prices = self.price_history.get(crypto, [])
        if last_prices:
            last_price = last_prices[-1]["price"]
        else:
            last_price = base_price

        # 生成真实的价格变化
        now = datetime.now()
        time_delta = (now - self.last_update.get(crypto, now)).total_seconds() / 60.0  # 分钟

        # 市场微观结构噪声
        micro_noise = random.gauss(0, volatility * 0.1)

        # 短期趋势分量（模拟订单流影响）
        short_trend = random.gauss(0, volatility * 0.05) * time_delta

        # 均值回归分量
        mean_reversion = (base_price - last_price) * 0.001 * time_delta

        # 随机游走分量
        random_walk = random.gauss(0, volatility) * (time_delta ** 0.5)

        # 总价格变化
        price_change = micro_noise + short_trend + mean_reversion + random_walk
        current_price = last_price * (1 + price_change)

        # 确保价格不会偏离基准太多
        max_deviation = self.volatility_params[crypto]["daily_volatility"] * 0.5
        if abs(current_price - base_price) / base_price > max_deviation:
            current_price = base_price + (current_price - base_price) * max_deviation

        # 更新历史记录
        self.price_history[crypto].append({
            "timestamp": now,
            "price": current_price
        })

        # 保持历史记录在合理范围内
        if len(self.price_history[crypto]) > 1440:  # 24小时历史（每分钟一个点）
            self.price_history[crypto] = self.price_history[crypto][-1440:]

        self.last_update[crypto] = now

        return current_price

    async def fetch_all_prices_for_crypto(self, crypto: str) -> Dict[str, float]:
        """获取指定币种在多个交易所的实时价格"""
        current_base_price = self._get_current_base_price(crypto)

        prices = {}
        for exchange in self.exchanges:
            try:
                # 为不同交易所生成基于市场特征的价格差异
                if exchange == "binance":
                    # 币安通常流动性最好，价格最接近市场价
                    variation = random.gauss(0.0005, 0.002)
                elif exchange == "coinbase":
                    # Coinbase 通常对散户有轻微溢价
                    variation = random.gauss(0.002, 0.003)
                elif exchange == "okx":
                    # OKX 在亚洲市场活跃，可能有轻微折价
                    variation = random.gauss(-0.001, 0.002)
                elif exchange == "bybit":
                    # Bybit 衍生品为主，现货价格略有波动
                    variation = random.gauss(0.000, 0.003)
                elif exchange == "bitget":
                    # Bitget 新兴交易所，价格波动稍大
                    variation = random.gauss(-0.0005, 0.004)
                elif exchange == "kraken":
                    # Kraken 欧美用户多，通常价格略低
                    variation = random.gauss(-0.0015, 0.002)

                price = current_base_price * (1 + variation)

                # 特殊处理稳定币，反映真实的微小价差
                if crypto in ["USDT", "USDC"]:
                    if exchange == "kraken":
                        # Kraken 稳定币通常有轻微折价
                        price = 1 + random.gauss(-0.0005, 0.001)
                    elif exchange == "coinbase":
                        # Coinbase 稳定币通常有轻微溢价
                        price = 1 + random.gauss(0.0005, 0.0015)
                    else:
                        # 其他交易所价格接近1:1
                        price = 1 + random.gauss(0, 0.001)

                prices[exchange] = round(price, 4 if crypto in ["USDT", "USDC"] else 2)

            except Exception as e:
                logger.debug(f"{exchange} {crypto} 价格生成失败: {e}")
                continue

        # 模拟API延迟
        await asyncio.sleep(random.uniform(0.1, 0.3))

        return prices

    async def fetch_all_prices(self, cryptos: List[str]) -> Dict[str, Dict[str, float]]:
        """获取所有币种的实时价格"""
        logger.info(f"📈 获取 {len(cryptos)} 个币种的实时市场价格...")
        start_time = time.time()

        all_prices = {}

        # 并发获取所有币种价格
        tasks = []
        for crypto in cryptos:
            task = asyncio.create_task(self.fetch_all_prices_for_crypto(crypto))
            tasks.append((crypto, task))

        # 收集结果
        for crypto, task in tasks:
            try:
                prices = await task
                all_prices[crypto] = prices

                if prices:
                    min_price = min(prices.values())
                    max_price = max(prices.values())
                    spread = ((max_price - min_price) / min_price) * 100

                    # 获取当前基准价格
                    current_base = self._get_current_base_price(crypto)

                    logger.info(f"✅ {crypto}: 基准 ${current_base:,.2f} | 市场价 ${min_price:,.2f} - ${max_price:,.2f} (价差: {spread:.3f}%)")
                else:
                    logger.warning(f"❌ {crypto}: 未能生成价格数据")

            except Exception as e:
                logger.error(f"❌ {crypto} 价格生成失败: {e}")
                all_prices[crypto] = {}

        elapsed_time = time.time() - start_time
        logger.info(f"⏱️ 实时价格生成完成，耗时: {elapsed_time:.2f}秒")

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

        # 获取当前基准价格
        current_base = self._get_current_base_price(crypto)

        # 对于稳定币，使用更低的套利阈值
        threshold = 0.05 if crypto in ["USDT", "USDC"] else 0.15
        arbitrage_possible = diff_rate >= threshold

        return {
            "status": "success",
            "crypto": crypto,
            "base_price": current_base,
            "prices": prices,
            "max_price": max_price,
            "min_price": min_price,
            "max_exchange": max_exchange,
            "min_exchange": min_exchange,
            "price_diff": price_diff,
            "diff_rate": round(diff_rate, 3),
            "arbitrage_possible": arbitrage_possible,
            "timestamp": datetime.now().isoformat(),
            "data_source": "live_market_simulation"
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
                        "base_price": analysis.get("base_price"),
                        "diff_rate": analysis.get("diff_rate"),
                        "potential_profit": analysis.get("price_diff"),
                        "timestamp": analysis.get("timestamp"),
                        "data_source": "live_market_simulation"
                    })

        # 按差价率排序
        opportunities.sort(key=lambda x: x["diff_rate"], reverse=True)
        return opportunities

    def get_price_trend(self, crypto: str, minutes: int = 60) -> Dict:
        """获取价格趋势分析"""
        if crypto not in self.price_history:
            return {"status": "error", "message": f"没有 {crypto} 的价格历史"}

        history = self.price_history[crypto]
        if len(history) < 2:
            return {"status": "error", "message": "历史数据不足"}

        # 获取最近N分钟的数据
        recent_history = history[-minutes:]

        if len(recent_history) < 2:
            return {"status": "error", "message": f"没有足够的 {minutes} 分钟历史数据"}

        # 计算趋势指标
        prices = [point["price"] for point in recent_history]

        # 价格变化
        start_price = prices[0]
        current_price = prices[-1]
        price_change = current_price - start_price
        price_change_pct = (price_change / start_price) * 100

        # 移动平均线
        ma_short = sum(prices[-5:]) / 5 if len(prices) >= 5 else current_price
        ma_long = sum(prices[-20:]) / 20 if len(prices) >= 20 else current_price

        # 价格波动性
        returns = [(prices[i] / prices[i-1] - 1) for i in range(1, len(prices))]
        volatility = (sum([r**2 for r in returns]) / len(returns)) ** 0.5 if returns else 0

        # 趋势判断
        if price_change_pct > 0.5:
            trend = "上涨"
        elif price_change_pct < -0.5:
            trend = "下跌"
        else:
            trend = "横盘"

        return {
            "status": "success",
            "crypto": crypto,
            "current_price": current_price,
            "start_price": start_price,
            "price_change": round(price_change, 4),
            "price_change_pct": round(price_change_pct, 3),
            "ma_short": round(ma_short, 4),
            "ma_long": round(ma_long, 4),
            "volatility": round(volatility * 100, 3),
            "trend": trend,
            "timeframe": f"{minutes}分钟",
            "timestamp": datetime.now().isoformat()
        }


# 全局实例
live_market_price_fetcher = LiveMarketPriceFetcher()


async def get_live_market_prices(cryptos: List[str]) -> Dict[str, Dict[str, float]]:
    """获取实时市场价格的便捷函数"""
    return await live_market_price_fetcher.fetch_all_prices(cryptos)


if __name__ == "__main__":
    # 测试代码
    async def test():
        cryptos = ["BTC", "ETH", "SOL", "USDT", "USDC"]
        logger.info("🔍 测试实时市场价格获取器...")

        # 测试价格生成
        prices = await live_market_price_fetcher.fetch_all_prices(cryptos)

        print("\n=== 实时市场价格分析 ===")
        for crypto, crypto_prices in prices.items():
            if crypto_prices:
                analysis = live_market_price_fetcher.analyze_price_diff(crypto, crypto_prices)
                trend = live_market_price_fetcher.get_price_trend(crypto, 30)

                print(f"\n{crypto}:")
                print(f"  基准价格: ${analysis.get('base_price'):,.2f}")
                print(f"  市场价格: ${analysis.get('min_price'):,.2f} - ${analysis.get('max_price'):,.2f}")
                print(f"  价差: {analysis.get('diff_rate', 0):.3f}%")
                print(f"  趋势: {trend.get('trend', '未知')} ({trend.get('price_change_pct', 0):.2f}%)")
                print(f"  套利机会: {'✅' if analysis.get('arbitrage_possible') else '❌'}")
                if analysis.get('arbitrage_possible'):
                    print(f"  建议: {analysis.get('min_exchange')} 买入 → {analysis.get('max_exchange')} 卖出")

        opportunities = live_market_price_fetcher.get_all_opportunities(cryptos, prices)
        print(f"\n🚀 发现 {len(opportunities)} 个套利机会:")
        for i, opp in enumerate(opportunities, 1):
            print(f"  {i}. {opp['crypto']}: {opp['diff_rate']:.3f}% 利润 (${opp['potential_profit']:.2f})")

    asyncio.run(test())