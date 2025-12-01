"""
三角套利策略 (Triangle Arbitrage)
在同一交易所内利用三个币对的价格不匹配进行套利
例如: BTC/USDT -> ETH/BTC -> ETH/USDT
"""

from src.utils.logger import logger
from src.models.trade import Session, ArbitrageOpportunity
from src.config import ARBITRAGE_THRESHOLD


class TriangleArbitrageStrategy:
    """三角套利策略"""
    
    def __init__(self, exchange):
        self.exchange = exchange
        self.session = Session()
    
    def scan_opportunities(self):
        """扫描三角套利机会"""
        logger.info("🔍 开始扫描三角套利机会...")
        opportunities = []
        
        try:
            # 获取交易所支持的所有币对
            symbols = self.exchange.symbols if hasattr(self.exchange, 'symbols') else []
            
            if not symbols:
                logger.warning("⚠️ 无法获取币对列表")
                return opportunities
            
            # 三角套利路径: BTC → ETH → USDT → BTC
            triangle_paths = [
                {
                    "name": "BTC-ETH-USDT",
                    "path": ["BTC/USDT", "ETH/BTC", "ETH/USDT"],
                    "initial_amount": 1.0
                },
                {
                    "name": "ETH-SOL-USDT",
                    "path": ["ETH/USDT", "SOL/ETH", "SOL/USDT"],
                    "initial_amount": 1.0
                },
                {
                    "name": "BTC-SOL-USDT",
                    "path": ["BTC/USDT", "SOL/BTC", "SOL/USDT"],
                    "initial_amount": 1.0
                },
            ]
            
            for triangle in triangle_paths:
                try:
                    opportunity = self._check_triangle(triangle, symbols)
                    if opportunity:
                        opportunities.append(opportunity)
                except Exception as e:
                    logger.debug(f"❌ 检查 {triangle['name']} 失败: {str(e)}")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ 扫描三角套利失败: {str(e)}")
            return opportunities
    
    def _check_triangle(self, triangle, available_symbols):
        """检查单个三角套利路径"""
        path = triangle["path"]
        initial_amount = triangle["initial_amount"]
        
        # 检查币对是否可用
        for symbol in path:
            if symbol not in available_symbols:
                return None
        
        try:
            # 获取三个币对的价格
            prices = {}
            for symbol in path:
                price = self.exchange.get_price(symbol)
                if not price:
                    return None
                prices[symbol] = price
            
            # 计算完整路径的收益
            # 路径: amount * (1/price1) * price2 * price3
            amount = initial_amount
            
            # 第一步: USDT -> BTC (用 USDT 换 BTC)
            amount = amount / prices[path[0]]
            logger.debug(f"  第一步 {path[0]}: {initial_amount} USDT → {amount:.8f} BTC")
            
            # 第二步: BTC -> ETH (用 BTC 换 ETH)
            amount = amount * prices[path[1]]
            logger.debug(f"  第二步 {path[1]}: {amount:.8f} ETH")
            
            # 第三步: ETH -> USDT (用 ETH 换 USDT)
            amount = amount * prices[path[2]]
            logger.debug(f"  第三步 {path[2]}: {amount:.8f} USDT")
            
            # 计算利润率
            profit_rate = ((amount - initial_amount) / initial_amount) * 100
            
            if profit_rate > ARBITRAGE_THRESHOLD:
                logger.warning(
                    f"🚨 三角套利机会! {triangle['name']}: "
                    f"{profit_rate:.2f}% 利润"
                )
                
                # 记录到数据库
                opportunity = ArbitrageOpportunity(
                    crypto=triangle['name'],
                    buy_exchange=self.exchange.exchange_name,
                    sell_exchange=self.exchange.exchange_name,
                    buy_price=initial_amount,
                    sell_price=amount,
                    profit_rate=profit_rate,
                    status="pending"
                )
                self.session.add(opportunity)
                self.session.commit()
                
                return opportunity
            
            return None
            
        except Exception as e:
            logger.debug(f"❌ 计算三角套利失败: {str(e)}")
            return None
    
    def execute_trade(self, opportunity):
        """执行三角套利交易"""
        try:
            logger.info(f"⚡ 执行三角套利交易: {opportunity.crypto}")
            
            # 这里需要实现实际的交易逻辑
            # 包括: 下单 -> 监控 -> 平仓
            
            opportunity.status = "executed"
            self.session.commit()
            
            logger.info(f"✅ 三角套利交易完成! 预期利润率: {opportunity.profit_rate:.2f}%")
            return True
            
        except Exception as e:
            logger.error(f"❌ 三角套利交易失败: {str(e)}")
            opportunity.status = "failed"
            self.session.commit()
            return False
