"""
期权交易所集成 - Deribit & Lyra Protocol
支持期权市场的实时价格和交易
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DeribitConnector:
    """Deribit 期权交易所连接器"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        """初始化 Deribit 连接器
        
        Args:
            api_key: API 密钥
            api_secret: API 密钥
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://www.deribit.com/api/v2"
        self.session = requests.Session()
    
    def get_available_options(self, currency: str = "BTC") -> List[Dict]:
        """获取可用的期权合约
        
        Args:
            currency: 币种 (BTC, ETH)
            
        Returns:
            期权合约列表
        """
        try:
            url = f"{self.base_url}/public/get_instruments"
            params = {
                "currency": currency,
                "kind": "option",
                "expired": False
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result"):
                logger.info(f"✅ 获取 {currency} 期权合约: {len(data['result'])} 个")
                return data["result"]
            
            return []
        
        except Exception as e:
            logger.error(f"❌ 获取期权合约失败: {str(e)}")
            return []
    
    def get_option_price(self, instrument_name: str) -> Optional[Dict]:
        """获取期权价格
        
        Args:
            instrument_name: 合约名称，如 "BTC-31DEC21-50000-C"
            
        Returns:
            价格数据
        """
        try:
            url = f"{self.base_url}/public/ticker"
            params = {"instrument_name": instrument_name}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result"):
                ticker = data["result"]
                return {
                    "instrument": instrument_name,
                    "bid": ticker.get("best_bid_price"),
                    "ask": ticker.get("best_ask_price"),
                    "last": ticker.get("last_price"),
                    "iv": ticker.get("mark_iv"),  # 隐含波动率
                    "gamma": ticker.get("gamma"),
                    "vega": ticker.get("vega"),
                    "theta": ticker.get("theta"),
                    "delta": ticker.get("delta"),
                    "timestamp": datetime.now()
                }
            
            return None
        
        except Exception as e:
            logger.error(f"❌ 获取期权价格失败: {str(e)}")
            return None
    
    def place_option_order(self, instrument_name: str, quantity: float, 
                          price: float, side: str = "buy") -> Optional[Dict]:
        """下期权订单 (需要认证)
        
        Args:
            instrument_name: 合约名称
            quantity: 数量
            price: 价格
            side: buy 或 sell
            
        Returns:
            订单响应
        """
        if not self.api_key:
            logger.error("❌ 未配置 API 密钥，无法下单")
            return None
        
        try:
            url = f"{self.base_url}/private/buy" if side == "buy" else f"{self.base_url}/private/sell"
            
            params = {
                "instrument_name": instrument_name,
                "amount": quantity,
                "price": price,
                "type": "limit"
            }
            
            logger.info(f"📊 下 {side.upper()} 单: {instrument_name} x {quantity} @ {price}")
            
            # 实际实现需要添加认证逻辑
            # response = self.session.get(url, params=params, timeout=10)
            
            return {"status": "pending", "message": "需要完整的 API 认证实现"}
        
        except Exception as e:
            logger.error(f"❌ 下单失败: {str(e)}")
            return None


class LyraConnector:
    """Lyra Protocol 连接器 (L2 期权协议)"""
    
    def __init__(self, contract_address: str = ""):
        """初始化 Lyra 连接器
        
        Args:
            contract_address: 合约地址
        """
        self.contract_address = contract_address
        self.base_url = "https://api.lyra.finance"
        self.session = requests.Session()
    
    def get_market_data(self, market: str = "BTC") -> Optional[Dict]:
        """获取市场数据
        
        Args:
            market: 市场名称
            
        Returns:
            市场数据
        """
        try:
            url = f"{self.base_url}/v1/markets/{market}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("data"):
                market_data = data["data"]
                return {
                    "market": market,
                    "spot_price": market_data.get("spot_price"),
                    "iv_rank": market_data.get("iv_rank"),
                    "24h_volume": market_data.get("volume_24h"),
                    "open_interest": market_data.get("open_interest"),
                    "timestamp": datetime.now()
                }
            
            return None
        
        except Exception as e:
            logger.error(f"❌ 获取 Lyra 市场数据失败: {str(e)}")
            return None
    
    def get_board_volatility(self, market: str = "BTC") -> Optional[float]:
        """获取波动率曲面数据
        
        Args:
            market: 市场名称
            
        Returns:
            平均隐含波动率
        """
        try:
            url = f"{self.base_url}/v1/boards/{market}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("data"):
                boards = data["data"]
                ivs = []
                
                for board in boards:
                    if "iv" in board:
                        ivs.append(board["iv"])
                
                if ivs:
                    avg_iv = sum(ivs) / len(ivs)
                    logger.info(f"📊 {market} 平均 IV: {avg_iv:.2%}")
                    return avg_iv
            
            return None
        
        except Exception as e:
            logger.error(f"❌ 获取波动率失败: {str(e)}")
            return None
    
    def get_positions(self, account: str) -> List[Dict]:
        """获取账户头寸
        
        Args:
            account: 账户地址
            
        Returns:
            头寸列表
        """
        try:
            url = f"{self.base_url}/v1/accounts/{account}/positions"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("data"):
                logger.info(f"✅ 获取账户头寸: {len(data['data'])} 个")
                return data["data"]
            
            return []
        
        except Exception as e:
            logger.error(f"❌ 获取头寸失败: {str(e)}")
            return []


class OptionsExchange:
    """期权交易所统一接口"""
    
    def __init__(self, deribit_key: str = "", deribit_secret: str = "", 
                 lyra_address: str = ""):
        """初始化期权交易所
        
        Args:
            deribit_key: Deribit API key
            deribit_secret: Deribit API secret
            lyra_address: Lyra 合约地址
        """
        self.deribit = DeribitConnector(deribit_key, deribit_secret)
        self.lyra = LyraConnector(lyra_address)
    
    def scan_put_call_parity_violations(self, currency: str = "BTC") -> List[Dict]:
        """扫描看跌看涨平价违反
        
        Args:
            currency: 币种
            
        Returns:
            价差机会列表
        """
        try:
            logger.info(f"🔍 扫描 {currency} 看跌看涨平价机会...")
            
            options = self.deribit.get_available_options(currency)
            violations = []
            
            # 按行权价分组
            by_strike = {}
            for opt in options:
                strike = opt.get("strike")
                if strike:
                    if strike not in by_strike:
                        by_strike[strike] = {"calls": [], "puts": []}
                    
                    if "C" in opt.get("instrument_name", ""):
                        by_strike[strike]["calls"].append(opt)
                    else:
                        by_strike[strike]["puts"].append(opt)
            
            # 检查平价关系
            for strike, opts in by_strike.items():
                if opts["calls"] and opts["puts"]:
                    call_opt = opts["calls"][0]
                    put_opt = opts["puts"][0]
                    
                    call_price = self.deribit.get_option_price(call_opt.get("instrument_name"))
                    put_price = self.deribit.get_option_price(put_opt.get("instrument_name"))
                    
                    if call_price and put_price:
                        call_mid = (call_price.get("bid", 0) + call_price.get("ask", 0)) / 2
                        put_mid = (put_price.get("bid", 0) + put_price.get("ask", 0)) / 2
                        
                        # 检查 C - P = S - K
                        parity_diff = call_mid - put_mid
                        
                        violations.append({
                            "strike": strike,
                            "call": call_opt.get("instrument_name"),
                            "put": put_opt.get("instrument_name"),
                            "call_price": call_mid,
                            "put_price": put_mid,
                            "parity_diff": parity_diff,
                            "timestamp": datetime.now()
                        })
            
            logger.info(f"✅ 发现 {len(violations)} 个平价机会")
            return violations
        
        except Exception as e:
            logger.error(f"❌ 扫描失败: {str(e)}")
            return []
    
    def analyze_volatility_skew(self, currency: str = "BTC") -> Optional[Dict]:
        """分析波动率斜度
        
        Args:
            currency: 币种
            
        Returns:
            波动率分析
        """
        try:
            logger.info(f"📊 分析 {currency} 波动率斜度...")
            
            # 从 Lyra 获取波动率数据
            board_iv = self.lyra.get_board_volatility(currency)
            
            if board_iv:
                return {
                    "currency": currency,
                    "board_iv": board_iv,
                    "analysis": "波动率分析完成"
                }
            
            return None
        
        except Exception as e:
            logger.error(f"❌ 分析失败: {str(e)}")
            return None


# 全局期权交易所实例
options_exchange = OptionsExchange()
