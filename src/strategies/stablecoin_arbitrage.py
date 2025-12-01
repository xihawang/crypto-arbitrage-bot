"""
稳定币套利策略 (Stablecoin Arbitrage)
利用不同稳定币 (USDT, USDC, DAI, BUSD) 之间的价格差异
虽然名义上都是 $1，但常有 0.01-0.5% 的差价
"""

from src.utils.logger import logger
from src.models.trade import Session, ArbitrageOpportunity
from src.config import ARBITRAGE_THRESHOLD


class StablecoinArbitrageStrategy:
    """稳定币套利策略"""
    
    def __init__(self, exchanges):
        """
        初始化
        exchanges: {'exchange_name': exchange_connector}
        """
        self.exchanges = exchanges
        self.session = Session()
        self.stablecoins = ["USDT", "USDC", "DAI", "BUSD"]
    
    def scan_opportunities(self):
        """扫描稳定币套利机会"""
        logger.info("🔍 开始扫描稳定币套利机会...")
        opportunities = []
        
        try:
            # 获取所有稳定币在不同交易所的价格
            stablecoin_prices = self._get_stablecoin_prices()
            
            # 检查价格差异
            for stablecoin, prices in stablecoin_prices.items():
                opportunity = self._check_stablecoin_difference(stablecoin, prices)
                if opportunity:
                    opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ 扫描稳定币套利失败: {str(e)}")
            return opportunities
    
    def _get_stablecoin_prices(self):
        """获取所有稳定币在各交易所的价格"""
        prices = {}
        
        for stablecoin in self.stablecoins:
            prices[stablecoin] = {}
            
            for exchange_name, exchange in self.exchanges.items():
                try:
                    # 获取稳定币兑 USDT 的价格 (通常是接近1)
                    if stablecoin == "USDT":
                        prices[stablecoin][exchange_name] = 1.0
                    else:
                        symbol = f"{stablecoin}/USDT"
                        price = exchange.get_price(symbol)
                        if price:
                            prices[stablecoin][exchange_name] = price
                            logger.debug(f"📊 {exchange_name} {symbol}: ${price:.6f}")
                except Exception as e:
                    logger.debug(f"❌ 获取 {exchange_name} {stablecoin} 价格失败: {str(e)}")
        
        return prices
    
    def _check_stablecoin_difference(self, stablecoin, prices):
        """检查单个稳定币的价格差异"""
        try:
            if not prices or len(prices) < 2:
                return None
            
            # 过滤有效价格
            valid_prices = {ex: p for ex, p in prices.items() if p is not None and p > 0}
            
            if len(valid_prices) < 2:
                return None
            
            # 找最高和最低价格
            buy_exchange = min(valid_prices, key=valid_prices.get)
            sell_exchange = max(valid_prices, key=valid_prices.get)
            
            buy_price = valid_prices[buy_exchange]
            sell_price = valid_prices[sell_exchange]
            
            # 计算利润率 (考虑手续费 ~0.1%)
            profit_rate = ((sell_price - buy_price) / buy_price) * 100 - 0.2  # 扣除往返手续费
            
            if profit_rate > ARBITRAGE_THRESHOLD:
                logger.warning(
                    f"🚨 稳定币套利机会! {stablecoin}: "
                    f"低 {buy_exchange}(${buy_price:.6f}) → "
                    f"高 {sell_exchange}(${sell_price:.6f}) = "
                    f"{profit_rate:.2f}% 利润"
                )
                
                # 记录到数据库
                opportunity = ArbitrageOpportunity(
                    crypto=f"{stablecoin}/USDT",
                    buy_exchange=buy_exchange,
                    sell_exchange=sell_exchange,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    profit_rate=profit_rate,
                    status="pending"
                )
                self.session.add(opportunity)
                self.session.commit()
                
                return opportunity
            
            return None
            
        except Exception as e:
            logger.debug(f"❌ 检查 {stablecoin} 价格差异失败: {str(e)}")
            return None
    
    def execute_trade(self, opportunity, amount=10000):
        """
        执行稳定币套利交易
        amount: 交易金额 (USDT)
        """
        try:
            logger.info(
                f"⚡ 执行稳定币套利交易: "
                f"在 {opportunity.buy_exchange} 买入 {amount} "
                f"{opportunity.crypto} "
                f"在 {opportunity.sell_exchange} 卖出"
            )
            
            buy_exchange = self.exchanges[opportunity.buy_exchange]
            sell_exchange = self.exchanges[opportunity.sell_exchange]
            
            # 第一步: 在低价交易所买入
            buy_result = buy_exchange.buy(
                opportunity.crypto,
                amount / opportunity.buy_price,
                opportunity.buy_price * 1.0005
            )
            
            if not buy_result:
                logger.error("❌ 买入失败")
                return False
            
            logger.info(f"✅ 买入成功")
            
            # 第二步: 在高价交易所卖出
            sell_result = sell_exchange.sell(
                opportunity.crypto,
                amount / opportunity.buy_price,
                opportunity.sell_price * 0.9995
            )
            
            if not sell_result:
                logger.error("❌ 卖出失败")
                return False
            
            # 计算实际利润
            actual_profit = (amount / opportunity.buy_price) * \
                          (opportunity.sell_price - opportunity.buy_price)
            
            logger.info(f"✅ 稳定币套利交易完成! 实际利润: ${actual_profit:.2f}")
            
            opportunity.status = "executed"
            self.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 稳定币套利交易失败: {str(e)}")
            opportunity.status = "failed"
            self.session.commit()
            return False
