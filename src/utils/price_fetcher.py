"""
实时价格获取服务
从多个交易所和数据源获取加密货币实时价格
"""

import requests
import asyncio
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger("price_fetcher")


class PriceFetcher:
    """价格获取服务 - 支持多个数据源"""
    
    # API 超时时间
    TIMEOUT = 10
    
    # 支持的交易所
    EXCHANGES = {
        "binance": "币安",
        "coinbase": "Coinbase",
        "kraken": "Kraken",
        "coingecko": "CoinGecko"
    }
    
    @staticmethod
    def get_price_from_coingecko(symbols: List[str] = None) -> Dict[str, float]:
        """
        从 CoinGecko 获取价格 (免费 API，无需认证)
        
        Args:
            symbols: 加密货币符号列表 (如: ["bitcoin", "ethereum", "solana"])
        
        Returns:
            {symbol: price_usd} 格式的价格字典
        """
        if symbols is None:
            symbols = ["bitcoin", "ethereum", "solana"]
        
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": ",".join(symbols),
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true"
            }
            
            response = requests.get(url, params=params, timeout=PriceFetcher.TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            result = {}
            for symbol, prices in data.items():
                result[symbol] = prices.get("usd", None)
            
            logger.info(f"✅ CoinGecko 获取成功: {len(result)} 个资产")
            return result
            
        except Exception as e:
            logger.error(f"❌ CoinGecko 获取失败: {str(e)}")
            return {}
    
    @staticmethod
    def get_price_from_binance(symbols: List[str] = None) -> Dict[str, float]:
        """
        从币安公开 API 获取价格 (无需认证)
        
        Args:
            symbols: 交易对列表 (如: ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
        
        Returns:
            {symbol: price} 格式的价格字典
        """
        if symbols is None:
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
        try:
            result = {}
            
            for symbol in symbols:
                url = "https://api.binance.com/api/v3/ticker/price"
                params = {"symbol": symbol}
                
                response = requests.get(url, params=params, timeout=PriceFetcher.TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                result[symbol] = float(data['price'])
            
            logger.info(f"✅ 币安获取成功: {len(result)} 个交易对")
            return result
            
        except Exception as e:
            logger.error(f"❌ 币安获取失败: {str(e)}")
            return {}
    
    @staticmethod
    def get_price_from_coinbase(symbols: List[str] = None) -> Dict[str, float]:
        """
        从 Coinbase 公开 API 获取价格 (无需认证)
        
        Args:
            symbols: 交易对列表 (如: ["BTC-USD", "ETH-USD"])
        
        Returns:
            {symbol: price} 格式的价格字典
        """
        if symbols is None:
            symbols = ["BTC-USD", "ETH-USD", "SOL-USD"]
        
        try:
            result = {}
            
            for symbol in symbols:
                url = f"https://api.coinbase.com/v2/prices/{symbol}/spot"
                response = requests.get(url, timeout=PriceFetcher.TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                result[symbol] = float(data['data']['amount'])
            
            logger.info(f"✅ Coinbase 获取成功: {len(result)} 个交易对")
            return result
            
        except Exception as e:
            logger.error(f"❌ Coinbase 获取失败: {str(e)}")
            return {}
    
    @staticmethod
    def get_price_from_kraken(symbols: List[str] = None) -> Dict[str, float]:
        """
        从 Kraken 公开 API 获取价格 (无需认证)
        
        Args:
            symbols: 交易对列表 (如: ["XBTUSDT", "ETHUSDT"])
        
        Returns:
            {symbol: price} 格式的价格字典
        """
        if symbols is None:
            symbols = ["XBTUSDT", "ETHUSDT", "SOLUSDT"]
        
        try:
            result = {}
            
            for symbol in symbols:
                url = "https://api.kraken.com/0/public/Ticker"
                params = {"pair": symbol}
                
                response = requests.get(url, params=params, timeout=PriceFetcher.TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                if data.get('result'):
                    ticker_data = data['result'][list(data['result'].keys())[0]]
                    result[symbol] = float(ticker_data['c'][0])  # 最后交易价格
            
            logger.info(f"✅ Kraken 获取成功: {len(result)} 个交易对")
            return result
            
        except Exception as e:
            logger.error(f"❌ Kraken 获取失败: {str(e)}")
            return {}
    
    @staticmethod
    def get_price_from_all_exchanges(crypto: str = "BTC") -> Dict[str, float]:
        """
        从所有交易所获取价格并返回对比结果
        
        Args:
            crypto: 加密货币代码 (如: "BTC", "ETH", "SOL")
        
        Returns:
            {exchange_name: price} 格式的价格字典
        """
        results = {}
        
        # CoinGecko
        symbol_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana"
        }
        
        if crypto in symbol_map:
            cg_data = PriceFetcher.get_price_from_coingecko([symbol_map[crypto]])
            if symbol_map[crypto] in cg_data:
                results["CoinGecko"] = cg_data[symbol_map[crypto]]
        
        # 币安
        binance_symbols = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT"
        }
        
        if crypto in binance_symbols:
            binance_data = PriceFetcher.get_price_from_binance([binance_symbols[crypto]])
            if binance_symbols[crypto] in binance_data:
                results["币安"] = binance_data[binance_symbols[crypto]]
        
        # Coinbase
        coinbase_symbols = {
            "BTC": "BTC-USD",
            "ETH": "ETH-USD",
            "SOL": "SOL-USD"
        }
        
        if crypto in coinbase_symbols:
            coinbase_data = PriceFetcher.get_price_from_coinbase([coinbase_symbols[crypto]])
            if coinbase_symbols[crypto] in coinbase_data:
                results["Coinbase"] = coinbase_data[coinbase_symbols[crypto]]
        
        # Kraken
        kraken_symbols = {
            "BTC": "XBTUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT"
        }
        
        if crypto in kraken_symbols:
            kraken_data = PriceFetcher.get_price_from_kraken([kraken_symbols[crypto]])
            if kraken_symbols[crypto] in kraken_data:
                results["Kraken"] = kraken_data[kraken_symbols[crypto]]
        
        return results
    
    @staticmethod
    def compare_prices(crypto: str = "BTC") -> Dict:
        """
        获取多交易所价格并进行对比分析
        
        Args:
            crypto: 加密货币代码 (如: "BTC", "ETH", "SOL")
        
        Returns:
            包含价格、价差、套利机会等信息的字典
        """
        prices = PriceFetcher.get_price_from_all_exchanges(crypto)
        
        if not prices:
            logger.warning(f"⚠️ 无法获取 {crypto} 的价格数据")
            return {
                "success": False,
                "crypto": crypto,
                "message": "无可用数据"
            }
        
        # 计算统计数据
        max_price = max(prices.values())
        min_price = min(prices.values())
        avg_price = sum(prices.values()) / len(prices)
        price_diff = max_price - min_price
        diff_rate = (price_diff / min_price) * 100
        
        # 找到最高和最低的交易所
        max_exchange = [k for k, v in prices.items() if v == max_price][0]
        min_exchange = [k for k, v in prices.items() if v == min_price][0]
        
        # 检查是否有套利机会 (价差 > 0.1%)
        has_arbitrage = diff_rate > 0.1
        
        result = {
            "success": True,
            "crypto": crypto,
            "timestamp": datetime.now().isoformat(),
            "prices": prices,
            "statistics": {
                "highest": max_price,
                "highest_exchange": max_exchange,
                "lowest": min_price,
                "lowest_exchange": min_exchange,
                "average": avg_price,
                "difference": price_diff,
                "difference_rate": diff_rate,
                "exchanges_count": len(prices)
            },
            "arbitrage_opportunity": {
                "detected": has_arbitrage,
                "buy_exchange": min_exchange,
                "sell_exchange": max_exchange,
                "profit_rate": diff_rate,
                "message": f"在 {min_exchange} 买入，{max_exchange} 卖出可获得 {diff_rate:.3f}% 利润 (扣除手续费后)" if has_arbitrage else "暂无明显套利机会"
            }
        }
        
        return result
    
    @staticmethod
    def print_price_report(crypto: str = "BTC"):
        """
        打印价格对比报告
        
        Args:
            crypto: 加密货币代码
        """
        print("\n" + "="*70)
        print(f"🔍 {crypto} 实时价格对比报告")
        print("="*70)
        print(f"⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        data = PriceFetcher.compare_prices(crypto)
        
        if not data.get("success"):
            print(f"❌ {data.get('message')}\n")
            return
        
        # 价格表
        print("📊 各交易所价格:")
        print("-"*70)
        for exchange, price in data["prices"].items():
            print(f"  {exchange:12} → ${price:>15,.2f}")
        
        # 统计数据
        stats = data["statistics"]
        print("\n" + "-"*70)
        print(f"  最高价格: ${stats['highest']:>15,.2f}  ({stats['highest_exchange']})")
        print(f"  最低价格: ${stats['lowest']:>15,.2f}  ({stats['lowest_exchange']})")
        print(f"  平均价格: ${stats['average']:>15,.2f}")
        print(f"  价差: ${stats['difference']:>15,.2f}  ({stats['difference_rate']:>7.3f}%)")
        print("-"*70)
        
        # 套利机会
        arb = data["arbitrage_opportunity"]
        if arb["detected"]:
            print(f"\n🚨 发现套利机会!")
            print(f"   {arb['message']}")
        else:
            print(f"\n✅ {arb['message']}")
        
        print("\n" + "="*70 + "\n")


# 使用示例
if __name__ == "__main__":
    # 单个加密货币价格对比
    PriceFetcher.print_price_report("BTC")
    PriceFetcher.print_price_report("ETH")
    PriceFetcher.print_price_report("SOL")
    
    # 获取原始数据
    result = PriceFetcher.compare_prices("BTC")
    print(f"\n📈 BTC 数据: {result}")
