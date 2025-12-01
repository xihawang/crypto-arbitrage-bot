"""
价格获取工具 - 从多个交易所和数据源实时获取加密货币价格
支持: CoinGecko, 币安, Coinbase, Kraken 等
"""

import requests
import asyncio
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PriceFetcher:
    """多源加密货币实时价格获取器"""
    
    # API 端点配置
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    BINANCE_API = "https://api.binance.com/api/v3"
    COINBASE_API = "https://api.coinbase.com/v2"
    KRAKEN_API = "https://api.kraken.com/0/public"
    
    # 交易对映射
    PAIR_MAPPINGS = {
        "BTC": {"symbol": "BTCUSDT", "id": "bitcoin"},
        "ETH": {"symbol": "ETHUSDT", "id": "ethereum"},
        "SOL": {"symbol": "SOLUSDT", "id": "solana"},
        "USDT": {"symbol": "USDTUSDT", "id": "tether"},
        "USDC": {"symbol": "USDCUSDT", "id": "usd-coin"},
    }
    
    def __init__(self, timeout: int = 10):
        """初始化价格获取器
        
        Args:
            timeout: 请求超时时间(秒)
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "CryptoArbitrageBot/1.0"
        })
    
    # ============ CoinGecko 价格获取 ============
    
    def get_price_coingecko(self, crypto: str) -> Optional[Dict]:
        """从 CoinGecko 获取价格
        
        Args:
            crypto: 加密货币代码 (BTC, ETH, SOL等)
            
        Returns:
            包含价格和市场数据的字典
        """
        try:
            coin_id = self.PAIR_MAPPINGS.get(crypto, {}).get("id", crypto.lower())
            
            url = f"{self.COINGECKO_API}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true"
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                return {
                    "exchange": "CoinGecko",
                    "price": data[coin_id].get("usd"),
                    "market_cap": data[coin_id].get("usd_market_cap"),
                    "volume_24h": data[coin_id].get("usd_24h_vol"),
                    "change_24h": data[coin_id].get("usd_24h_change"),
                    "timestamp": datetime.now()
                }
        except Exception as e:
            logger.warning(f"❌ CoinGecko 获取 {crypto} 失败: {str(e)}")
        
        return None
    
    # ============ 币安价格获取 ============
    
    def get_price_binance(self, crypto: str) -> Optional[Dict]:
        """从币安获取价格
        
        Args:
            crypto: 加密货币代码
            
        Returns:
            包含价格的字典
        """
        try:
            symbol = self.PAIR_MAPPINGS.get(crypto, {}).get("symbol", f"{crypto}USDT")
            
            url = f"{self.BINANCE_API}/ticker/price"
            params = {"symbol": symbol}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return {
                "exchange": "币安",
                "price": float(data.get("price", 0)),
                "symbol": symbol,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.warning(f"❌ 币安获取 {crypto} 失败: {str(e)}")
        
        return None
    
    # ============ Coinbase 价格获取 ============
    
    def get_price_coinbase(self, crypto: str) -> Optional[Dict]:
        """从 Coinbase 获取价格
        
        Args:
            crypto: 加密货币代码
            
        Returns:
            包含价格的字典
        """
        try:
            pair = f"{crypto}-USD"
            
            url = f"{self.COINBASE_API}/prices/{pair}/spot"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return {
                "exchange": "Coinbase",
                "price": float(data["data"].get("amount", 0)),
                "pair": pair,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.warning(f"❌ Coinbase 获取 {crypto} 失败: {str(e)}")
        
        return None
    
    # ============ Kraken 价格获取 ============
    
    def get_price_kraken(self, crypto: str) -> Optional[Dict]:
        """从 Kraken 获取价格
        
        Args:
            crypto: 加密货币代码
            
        Returns:
            包含价格的字典
        """
        try:
            kraken_pair = f"X{crypto}USDT" if crypto in ["BTC", "ETH"] else f"{crypto}USDT"
            
            url = f"{self.KRAKEN_API}/Ticker"
            params = {"pair": kraken_pair}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result"):
                ticker = data["result"][list(data["result"].keys())[0]]
                return {
                    "exchange": "Kraken",
                    "price": float(ticker["c"][0]),  # 最后交易价
                    "pair": kraken_pair,
                    "timestamp": datetime.now()
                }
        except Exception as e:
            logger.warning(f"❌ Kraken 获取 {crypto} 失败: {str(e)}")
        
        return None
    
    # ============ 综合价格获取 ============
    
    def get_price_multi(self, crypto: str) -> Dict[str, Dict]:
        """从多个交易所获取价格
        
        Args:
            crypto: 加密货币代码
            
        Returns:
            {exchange_name: price_data} 格式的字典
        """
        prices = {}
        
        # 并行获取所有价格
        coingecko_price = self.get_price_coingecko(crypto)
        if coingecko_price:
            prices["CoinGecko"] = coingecko_price
        
        binance_price = self.get_price_binance(crypto)
        if binance_price:
            prices["币安"] = binance_price
        
        coinbase_price = self.get_price_coinbase(crypto)
        if coinbase_price:
            prices["Coinbase"] = coinbase_price
        
        kraken_price = self.get_price_kraken(crypto)
        if kraken_price:
            prices["Kraken"] = kraken_price
        
        return prices
    
    def get_price_average(self, crypto: str) -> float:
        """获取多源价格平均值
        
        Args:
            crypto: 加密货币代码
            
        Returns:
            多个交易所的平均价格
        """
        prices = self.get_price_multi(crypto)
        if not prices:
            logger.error(f"❌ 无法获取 {crypto} 的价格")
            return 0.0
        
        price_list = [p["price"] for p in prices.values() if "price" in p]
        if price_list:
            avg_price = sum(price_list) / len(price_list)
            return round(avg_price, 2)
        
        return 0.0
    
    # ============ 价格对比分析 ============
    
    def analyze_price_diff(self, crypto: str) -> Dict:
        """分析价格差异并识别套利机会
        
        Args:
            crypto: 加密货币代码
            
        Returns:
            包含价差分析的字典
        """
        prices = self.get_price_multi(crypto)
        
        if not prices or len(prices) < 2:
            return {"status": "error", "message": "数据不足"}
        
        price_values = [p["price"] for p in prices.values() if "price" in p]
        
        if not price_values:
            return {"status": "error", "message": "无价格数据"}
        
        max_price = max(price_values)
        min_price = min(price_values)
        price_diff = max_price - min_price
        diff_rate = (price_diff / min_price) * 100
        
        # 找出最高和最低交易所
        max_exchange = next(k for k, v in prices.items() if v.get("price") == max_price)
        min_exchange = next(k for k, v in prices.items() if v.get("price") == min_price)
        
        analysis = {
            "crypto": crypto,
            "timestamp": datetime.now().isoformat(),
            "prices": {exchange: price_data.get("price") for exchange, price_data in prices.items()},
            "max_price": max_price,
            "min_price": min_price,
            "price_diff": round(price_diff, 2),
            "diff_rate": round(diff_rate, 4),
            "max_exchange": max_exchange,
            "min_exchange": min_exchange,
            "arbitrage_possible": diff_rate > 0.1,  # > 0.1% 考虑有套利机会
        }
        
        return analysis
    
    # ============ 批量获取 ============
    
    def get_all_prices(self, cryptos: List[str]) -> Dict[str, Dict]:
        """获取多个加密货币的价格
        
        Args:
            cryptos: 加密货币代码列表
            
        Returns:
            {crypto: multi_price_data} 格式的字典
        """
        all_prices = {}
        for crypto in cryptos:
            all_prices[crypto] = self.get_price_multi(crypto)
        return all_prices
    
    def display_price_summary(self, crypto: str) -> None:
        """显示价格汇总
        
        Args:
            crypto: 加密货币代码
        """
        analysis = self.analyze_price_diff(crypto)
        
        if analysis.get("status") == "error":
            logger.error(f"❌ {analysis.get('message')}")
            return
        
        print(f"\n{'='*60}")
        print(f"💰 {crypto} 价格汇总")
        print(f"{'='*60}")
        print(f"⏰ 更新时间: {analysis['timestamp']}\n")
        
        # 显示各交易所价格
        for exchange, price in analysis["prices"].items():
            print(f"  {exchange:12} → ${price:>12,.2f}")
        
        # 显示统计信息
        print(f"\n{'-'*60}")
        print(f"  最高价格: ${analysis['max_price']:>12,.2f} ({analysis['max_exchange']})")
        print(f"  最低价格: ${analysis['min_price']:>12,.2f} ({analysis['min_exchange']})")
        print(f"  价差: ${analysis['price_diff']:>12,.2f} ({analysis['diff_rate']:.4f}%)")
        print(f"{'-'*60}")
        
        # 套利提示
        if analysis["arbitrage_possible"]:
            print(f"\n🚨 发现套利机会!")
            print(f"   买入: {analysis['min_exchange']} @ ${analysis['min_price']:,.2f}")
            print(f"   卖出: {analysis['max_exchange']} @ ${analysis['max_price']:,.2f}")
            print(f"   理论利润率: {analysis['diff_rate']:.4f}%")
        else:
            print(f"\n✅ 暂无明显套利机会 (价差 < 0.1%)")
        
        print(f"\n{'='*60}\n")


# 全局实例
price_fetcher = PriceFetcher()
