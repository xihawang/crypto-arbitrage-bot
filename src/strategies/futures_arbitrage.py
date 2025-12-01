"""
期货套利策略 (Futures Arbitrage)
包括:
1. 现货期货套利: 买现货 + 卖空期货合约
2. 期现套利: 买期货 + 卖空现货
3. 跨期套利: 不同到期日期货之间的差价
"""

from src.utils.logger import logger
from src.models.trade import Session, ArbitrageOpportunity
from src.config import ARBITRAGE_THRESHOLD
from datetime import datetime, timedelta


class FuturesArbitrageStrategy:
    """期货套利策略"""
    
    def __init__(self, spot_exchange, futures_exchange):
        """
        初始化
        spot_exchange: 现货交易所
        futures_exchange: 期货交易所
        """
        self.spot_exchange = spot_exchange
        self.futures_exchange = futures_exchange
        self.session = Session()
    
    def scan_opportunities(self):
        """扫描期货套利机会"""
        logger.info("🔍 开始扫描期货套利机会...")
        opportunities = []
        
        try:
            # 1. 扫描现货期货套利机会
            spot_futures_opps = self._scan_spot_futures_arbitrage()
            opportunities.extend(spot_futures_opps)
            
            # 2. 扫描跨期套利机会
            calendar_opps = self._scan_calendar_spread()
            opportunities.extend(calendar_opps)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ 扫描期货套利失败: {str(e)}")
            return opportunities
    
    def _scan_spot_futures_arbitrage(self):
        """扫描现货期货套利机会"""
        logger.info("📊 扫描现货期货套利...")
        opportunities = []
        
        try:
            symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
            
            for symbol in symbols:
                # 获取现货价格
                spot_price = self.spot_exchange.get_price(symbol)
                if not spot_price:
                    continue
                
                # 获取期货价格 (最近合约)
                futures_symbol = symbol.replace("USDT", "USDT_PERP")
                futures_price = self._get_futures_price(futures_symbol)
                if not futures_price:
                    continue
                
                # 计算基差 (Basis)
                basis = futures_price - spot_price
                basis_rate = (basis / spot_price) * 100
                
                logger.info(
                    f"💱 {symbol}: 现货=${spot_price:.2f}, "
                    f"期货=${futures_price:.2f}, "
                    f"基差={basis_rate:.3f}%"
                )
                
                # 检查套利机会
                # 如果期货溢价 > 0.5% (需要考虑融资成本和手续费)
                if basis_rate > 0.5:
                    logger.warning(
                        f"🚨 期货溢价套利机会! {symbol}: "
                        f"基差 {basis_rate:.3f}%"
                    )
                    
                    opportunity = ArbitrageOpportunity(
                        crypto=f"{symbol}_PERP",
                        buy_exchange="现货",
                        sell_exchange="期货",
                        buy_price=spot_price,
                        sell_price=futures_price,
                        profit_rate=basis_rate,
                        status="pending"
                    )
                    self.session.add(opportunity)
                    opportunities.append(opportunity)
                
                # 如果期货贴水 < -0.5% (需要考虑融资成本和手续费)
                elif basis_rate < -0.5:
                    logger.warning(
                        f"🚨 期货贴水套利机会! {symbol}: "
                        f"基差 {basis_rate:.3f}%"
                    )
                    
                    opportunity = ArbitrageOpportunity(
                        crypto=f"{symbol}_PERP",
                        buy_exchange="期货",
                        sell_exchange="现货",
                        buy_price=futures_price,
                        sell_price=spot_price,
                        profit_rate=-basis_rate,
                        status="pending"
                    )
                    self.session.add(opportunity)
                    opportunities.append(opportunity)
            
            self.session.commit()
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ 扫描现货期货套利失败: {str(e)}")
            return opportunities
    
    def _scan_calendar_spread(self):
        """扫描跨期套利机会"""
        logger.info("📊 扫描跨期套利...")
        opportunities = []
        
        try:
            # 获取不同到期日的期货合约价格
            symbols = ["BTC/USDT", "ETH/USDT"]
            
            for symbol in symbols:
                try:
                    # 获取近月、次月、季月合约价格
                    nearby = self._get_futures_price(f"{symbol}_0101")  # 近月
                    deferred = self._get_futures_price(f"{symbol}_0102")  # 次月
                    seasonal = self._get_futures_price(f"{symbol}_0103")  # 季月
                    
                    if nearby and deferred:
                        # 计算价差
                        spread = deferred - nearby
                        spread_rate = (spread / nearby) * 100
                        
                        logger.info(
                            f"📈 {symbol} 近月-次月: ${nearby:.2f} - ${deferred:.2f} = "
                            f"${spread:.2f} ({spread_rate:.3f}%)"
                        )
                        
                        # 如果价差异常，可能存在套利机会
                        if abs(spread_rate) > 0.5:
                            logger.warning(
                                f"🚨 跨期套利机会! {symbol}: "
                                f"价差 {spread_rate:.3f}%"
                            )
                            
                            if spread > 0:
                                # 卖近月，买次月
                                opportunity = ArbitrageOpportunity(
                                    crypto=f"{symbol}_CALENDAR",
                                    buy_exchange="次月",
                                    sell_exchange="近月",
                                    buy_price=deferred,
                                    sell_price=nearby,
                                    profit_rate=spread_rate,
                                    status="pending"
                                )
                            else:
                                # 买近月，卖次月
                                opportunity = ArbitrageOpportunity(
                                    crypto=f"{symbol}_CALENDAR",
                                    buy_exchange="近月",
                                    sell_exchange="次月",
                                    buy_price=nearby,
                                    sell_price=deferred,
                                    profit_rate=-spread_rate,
                                    status="pending"
                                )
                            
                            self.session.add(opportunity)
                            opportunities.append(opportunity)
                
                except Exception as e:
                    logger.debug(f"❌ 获取 {symbol} 跨期价格失败: {str(e)}")
            
            self.session.commit()
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ 扫描跨期套利失败: {str(e)}")
            return opportunities
    
    def _get_futures_price(self, symbol):
        """获取期货价格"""
        try:
            if hasattr(self.futures_exchange, 'get_price'):
                return self.futures_exchange.get_price(symbol)
            return None
        except Exception as e:
            logger.debug(f"❌ 获取期货价格失败: {str(e)}")
            return None
    
    def execute_spot_futures_trade(self, opportunity, amount=1):
        """
        执行现货期货套利
        strategy: "long" (现货溢价) 或 "short" (期货溢价)
        """
        try:
            logger.info(
                f"⚡ 执行现货期货套利: "
                f"在{opportunity.buy_exchange}买入, "
                f"在{opportunity.sell_exchange}卖出"
            )
            
            # 检查融资成本
            financing_cost = self._estimate_financing_cost(opportunity)
            actual_profit = opportunity.profit_rate - financing_cost
            
            logger.info(f"📊 融资成本: {financing_cost:.3f}%, 实际利润: {actual_profit:.3f}%")
            
            if actual_profit < ARBITRAGE_THRESHOLD:
                logger.warning("⚠️ 考虑融资成本后，利润不足")
                return False
            
            # 第一步: 在现货市场建立头寸
            if opportunity.buy_exchange == "现货":
                # 买现货
                spot_result = self.spot_exchange.buy(
                    opportunity.crypto.replace("_PERP", ""),
                    amount,
                    opportunity.buy_price * 1.001
                )
                if not spot_result:
                    logger.error("❌ 买现货失败")
                    return False
                
                logger.info("✅ 买现货成功")
            
            # 第二步: 在期货市场建立反向头寸
            # 卖空期货
            futures_result = self.futures_exchange.sell(
                opportunity.crypto,
                amount,
                opportunity.sell_price * 0.999
            )
            if not futures_result:
                logger.error("❌ 卖期货失败")
                return False
            
            logger.info("✅ 卖期货成功")
            
            # 记录交易
            opportunity.status = "executed"
            self.session.commit()
            
            logger.info(
                f"✅ 现货期货套利交易完成! "
                f"预期利润: {actual_profit:.3f}%"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 现货期货套利交易失败: {str(e)}")
            opportunity.status = "failed"
            self.session.commit()
            return False
    
    def _estimate_financing_cost(self, opportunity):
        """估计融资成本"""
        # 日融资成本: 约 0.01% - 0.05% (每日)
        # 假设持有 7 天
        daily_financing_rate = 0.03  # 0.03% 每日
        holding_days = 7
        
        total_cost = daily_financing_rate * holding_days
        return total_cost
    
    def execute_calendar_spread(self, opportunity, amount=1):
        """执行跨期套利"""
        try:
            logger.info(
                f"⚡ 执行跨期套利: "
                f"卖{opportunity.sell_exchange}, 买{opportunity.buy_exchange}"
            )
            
            # 第一步: 卖近月合约
            sell_result = self.futures_exchange.sell(
                f"{opportunity.crypto.replace('_CALENDAR', '')}_NEARBY",
                amount,
                opportunity.sell_price * 0.999
            )
            if not sell_result:
                logger.error("❌ 卖近月失败")
                return False
            
            logger.info("✅ 卖近月成功")
            
            # 第二步: 买次月合约
            buy_result = self.futures_exchange.buy(
                f"{opportunity.crypto.replace('_CALENDAR', '')}_DEFERRED",
                amount,
                opportunity.buy_price * 1.001
            )
            if not buy_result:
                logger.error("❌ 买次月失败")
                return False
            
            logger.info("✅ 买次月成功")
            
            opportunity.status = "executed"
            self.session.commit()
            
            logger.info(
                f"✅ 跨期套利交易完成! "
                f"预期利润: {opportunity.profit_rate:.3f}%"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 跨期套利交易失败: {str(e)}")
            opportunity.status = "failed"
            self.session.commit()
            return False
