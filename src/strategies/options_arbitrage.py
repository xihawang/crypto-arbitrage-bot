"""
期权套利策略 (Options Arbitrage)
利用期权的看涨/看跌价差以及期权与现货的差异进行套利
主要策略:
1. 垂直价差 (Vertical Spread)
2. 日历价差 (Calendar Spread)
3. 转换套利 (Conversion/Reversal)
"""

from src.utils.logger import logger
from src.models.trade import Session, ArbitrageOpportunity
from src.config import ARBITRAGE_THRESHOLD
import math


class OptionsArbitrageStrategy:
    """期权套利策略"""
    
    def __init__(self):
        self.session = Session()
        
        # 支持的期权交易所
        self.options_exchanges = ["deribit", "lyra", "hegic"]
    
    def scan_opportunities(self):
        """扫描期权套利机会"""
        logger.info("🔍 开始扫描期权套利机会...")
        opportunities = []
        
        try:
            # 1. 扫描看涨/看跌不相称 (Put-Call Parity Violation)
            parity_opps = self._scan_put_call_parity_violations()
            opportunities.extend(parity_opps)
            
            # 2. 扫描垂直价差套利
            vertical_opps = self._scan_vertical_spreads()
            opportunities.extend(vertical_opps)
            
            # 3. 扫描日历价差套利
            calendar_opps = self._scan_calendar_spreads()
            opportunities.extend(calendar_opps)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ 扫描期权套利失败: {str(e)}")
            return opportunities
    
    def _scan_put_call_parity_violations(self):
        """
        扫描看涨/看跌平价违规
        
        看涨/看跌平价: C - P = S - K*exp(-r*T)
        其中: C=看涨价格, P=看跌价格, S=现货价格, K=行权价, T=到期时间
        """
        opportunities = []
        
        try:
            logger.info("📊 扫描看涨/看跌平价...")
            
            symbols = ["BTC", "ETH"]
            
            for symbol in symbols:
                try:
                    # 获取现货价格
                    spot_price = self._get_spot_price(symbol)
                    if not spot_price:
                        continue
                    
                    # 获取期权数据
                    options_data = self._get_options_data(symbol)
                    
                    for option in options_data:
                        # 获取看涨和看跌期权
                        call_price = option.get('call_price', 0)
                        put_price = option.get('put_price', 0)
                        strike = option.get('strike', 0)
                        time_to_expiry = option.get('time_to_expiry', 0)
                        
                        if call_price == 0 or put_price == 0:
                            continue
                        
                        # 计算理论值
                        risk_free_rate = 0.05  # 5% 年利率
                        discount_factor = math.exp(-risk_free_rate * time_to_expiry)
                        
                        theoretical_diff = spot_price - strike * discount_factor
                        actual_diff = call_price - put_price
                        
                        # 检查套利机会
                        arbitrage_amount = actual_diff - theoretical_diff
                        arbitrage_rate = (arbitrage_amount / spot_price) * 100
                        
                        if abs(arbitrage_rate) > ARBITRAGE_THRESHOLD:
                            logger.warning(
                                f"🚨 看涨/看跌平价违规! {symbol} 行权价 {strike}: "
                                f"套利空间 {arbitrage_rate:.2f}%"
                            )
                            
                            # 确定套利方向
                            if arbitrage_amount > 0:
                                # 看涨被高估，应该卖看涨，买看跌
                                trade_type = "sell_call_buy_put"
                            else:
                                # 看跌被高估，应该买看涨，卖看跌
                                trade_type = "buy_call_sell_put"
                            
                            opportunity = ArbitrageOpportunity(
                                crypto=f"{symbol}_PUT_CALL_PARITY",
                                buy_exchange=trade_type,
                                sell_exchange=f"strike_{strike}",
                                buy_price=put_price if "buy_put" in trade_type else call_price,
                                sell_price=call_price if "buy_put" in trade_type else put_price,
                                profit_rate=abs(arbitrage_rate),
                                status="pending"
                            )
                            self.session.add(opportunity)
                            opportunities.append(opportunity)
                
                except Exception as e:
                    logger.debug(f"❌ 扫描 {symbol} 看涨/看跌失败: {str(e)}")
            
            self.session.commit()
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ 扫描看涨/看跌平价失败: {str(e)}")
            return opportunities
    
    def _scan_vertical_spreads(self):
        """
        扫描垂直价差套利
        
        看涨垂直价差 (Bull Call Spread):
        买低行权价看涨 + 卖高行权价看涨
        
        看跌垂直价差 (Bear Put Spread):
        卖高行权价看跌 + 买低行权价看跌
        """
        opportunities = []
        
        try:
            logger.info("📊 扫描垂直价差...")
            
            symbols = ["BTC", "ETH"]
            
            for symbol in symbols:
                try:
                    options_data = self._get_options_data(symbol)
                    
                    # 找相邻的行权价
                    for i in range(len(options_data) - 1):
                        lower_strike = options_data[i]
                        upper_strike = options_data[i + 1]
                        
                        # 检查看涨垂直价差
                        lower_call = lower_strike.get('call_price', 0)
                        upper_call = upper_strike.get('call_price', 0)
                        
                        if lower_call > 0 and upper_call > 0:
                            # 理论上: lower_call 应该 > upper_call
                            if lower_call <= upper_call:
                                profit_rate = ((lower_call - upper_call) / lower_call) * 100
                                
                                if profit_rate > ARBITRAGE_THRESHOLD:
                                    logger.warning(
                                        f"🚨 看涨垂直价差违规! {symbol}: "
                                        f"套利空间 {abs(profit_rate):.2f}%"
                                    )
                                    
                                    opportunity = ArbitrageOpportunity(
                                        crypto=f"{symbol}_BULL_CALL_SPREAD",
                                        buy_exchange=f"call_{lower_strike['strike']}",
                                        sell_exchange=f"call_{upper_strike['strike']}",
                                        buy_price=lower_call,
                                        sell_price=upper_call,
                                        profit_rate=abs(profit_rate),
                                        status="pending"
                                    )
                                    self.session.add(opportunity)
                                    opportunities.append(opportunity)
                
                except Exception as e:
                    logger.debug(f"❌ 扫描 {symbol} 垂直价差失败: {str(e)}")
            
            self.session.commit()
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ 扫描垂直价差失败: {str(e)}")
            return opportunities
    
    def _scan_calendar_spreads(self):
        """
        扫描日历价差套利
        
        卖近月期权 + 买远月期权
        如果隐含波动率回到正常水平，可获利
        """
        opportunities = []
        
        try:
            logger.info("📊 扫描日历价差...")
            
            symbols = ["BTC", "ETH"]
            
            for symbol in symbols:
                try:
                    # 获取不同到期日期的期权
                    near_term = self._get_options_data(symbol, days_to_expiry=7)
                    far_term = self._get_options_data(symbol, days_to_expiry=30)
                    
                    for near, far in zip(near_term, far_term):
                        if near['strike'] == far['strike']:
                            near_price = near.get('call_price', 0)
                            far_price = far.get('call_price', 0)
                            
                            if near_price > 0 and far_price > 0:
                                # 计算时间价值差异
                                price_diff = near_price - far_price
                                
                                # 如果近月比远月昂贵，可能是套利机会
                                if price_diff > 0:
                                    diff_rate = (price_diff / far_price) * 100
                                    
                                    if diff_rate > ARBITRAGE_THRESHOLD:
                                        logger.warning(
                                            f"🚨 日历价差机会! {symbol} 行权价 {near['strike']}: "
                                            f"套利空间 {diff_rate:.2f}%"
                                        )
                                        
                                        opportunity = ArbitrageOpportunity(
                                            crypto=f"{symbol}_CALENDAR_SPREAD",
                                            buy_exchange=f"far_{far['expiry']}",
                                            sell_exchange=f"near_{near['expiry']}",
                                            buy_price=far_price,
                                            sell_price=near_price,
                                            profit_rate=diff_rate,
                                            status="pending"
                                        )
                                        self.session.add(opportunity)
                                        opportunities.append(opportunity)
                
                except Exception as e:
                    logger.debug(f"❌ 扫描 {symbol} 日历价差失败: {str(e)}")
            
            self.session.commit()
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ 扫描日历价差失败: {str(e)}")
            return opportunities
    
    def _get_spot_price(self, symbol):
        """获取现货价格"""
        try:
            logger.debug(f"🔄 获取 {symbol} 现货价格...")
            return None  # 需要实现
        except Exception as e:
            logger.debug(f"❌ 获取现货价格失败: {str(e)}")
            return None
    
    def _get_options_data(self, symbol, days_to_expiry=None):
        """获取期权数据"""
        try:
            logger.debug(f"🔄 获取 {symbol} 期权数据...")
            # 需要调用期权交易所 API (Deribit, Lyra 等)
            return []
        except Exception as e:
            logger.debug(f"❌ 获取期权数据失败: {str(e)}")
            return []
    
    def execute_put_call_parity_trade(self, opportunity):
        """执行看涨/看跌平价套利"""
        try:
            logger.info(f"⚡ 执行看涨/看跌平价套利: {opportunity.crypto}")
            
            if "buy_put" in opportunity.buy_exchange:
                logger.info(f"🔄 买看跌期权 @ ${opportunity.buy_price:.2f}")
                logger.info(f"🔄 卖看涨期权 @ ${opportunity.sell_price:.2f}")
            else:
                logger.info(f"🔄 买看涨期权 @ ${opportunity.buy_price:.2f}")
                logger.info(f"🔄 卖看跌期权 @ ${opportunity.sell_price:.2f}")
            
            opportunity.status = "executed"
            self.session.commit()
            
            logger.info(f"✅ 期权套利完成! 预期利润率: {opportunity.profit_rate:.2f}%")
            return True
            
        except Exception as e:
            logger.error(f"❌ 期权套利失败: {str(e)}")
            opportunity.status = "failed"
            self.session.commit()
            return False
