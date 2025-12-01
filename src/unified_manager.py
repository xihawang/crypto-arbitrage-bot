"""
统一的套利管理器
管理和协调所有套利策略
"""

import time
from src.utils.logger import logger
from src.config import EXCHANGES, CRYPTOS
from src.exchanges.binance import BinanceConnector
from src.exchanges.coinbase import CoinbaseConnector
from src.strategies.arbitrage import ArbitrageStrategy
from src.strategies.triangle_arbitrage import TriangleArbitrageStrategy
from src.strategies.stablecoin_arbitrage import StablecoinArbitrageStrategy
from src.strategies.dex_arbitrage import DEXArbitrageStrategy
from src.strategies.futures_arbitrage import FuturesArbitrageStrategy
from src.strategies.cross_chain_arbitrage import CrossChainArbitrageStrategy
from src.strategies.flash_loan_arbitrage import FlashLoanArbitrageStrategy
from src.strategies.options_arbitrage import OptionsArbitrageStrategy


class UnifiedArbitrageManager:
    """统一的套利管理器"""
    
    def __init__(self):
        logger.info("🚀 初始化统一套利管理器...")
        
        # 初始化交易所连接
        self.exchanges = {
            "binance": BinanceConnector(
                EXCHANGES["binance"]["api_key"],
                EXCHANGES["binance"]["api_secret"]
            ),
            "coinbase": CoinbaseConnector(
                EXCHANGES["coinbase"]["api_key"],
                EXCHANGES["coinbase"]["api_secret"]
            ),
        }
        
        # 初始化各个策略
        self.strategies = {
            "spot_arbitrage": ArbitrageStrategy(self.exchanges),
            "triangle_arbitrage": TriangleArbitrageStrategy(self.exchanges["binance"]),
            "stablecoin_arbitrage": StablecoinArbitrageStrategy(self.exchanges),
            "dex_arbitrage": DEXArbitrageStrategy(),
            "cross_chain_arbitrage": CrossChainArbitrageStrategy(),
            "flash_loan_arbitrage": FlashLoanArbitrageStrategy(),
            "options_arbitrage": OptionsArbitrageStrategy(),
        }
        
        # 期货套利需要期货交易所
        # self.strategies["futures_arbitrage"] = FuturesArbitrageStrategy(
        #     self.exchanges["binance"],
        #     futures_exchange
        # )
        
        logger.info("✅ 套利管理器初始化完成")
    
    def scan_all_opportunities(self):
        """扫描所有套利机会"""
        logger.info("\n" + "="*60)
        logger.info("🔍 开始全方位套利机会扫描")
        logger.info("="*60)
        
        all_opportunities = {
            "spot_arbitrage": [],
            "triangle_arbitrage": [],
            "stablecoin_arbitrage": [],
            "dex_arbitrage": [],
            "cross_chain_arbitrage": [],
            "flash_loan_arbitrage": [],
            "options_arbitrage": [],
        }
        
        # 1. 现货套利
        logger.info("\n1️⃣ 扫描现货套利...")
        try:
            opportunities = self.strategies["spot_arbitrage"].scan_opportunities(CRYPTOS)
            all_opportunities["spot_arbitrage"] = opportunities
            logger.info(f"✅ 发现 {len(opportunities)} 个现货套利机会")
        except Exception as e:
            logger.error(f"❌ 现货套利扫描失败: {str(e)}")
        
        # 2. 三角套利
        logger.info("\n2️⃣ 扫描三角套利...")
        try:
            opportunities = self.strategies["triangle_arbitrage"].scan_opportunities()
            all_opportunities["triangle_arbitrage"] = opportunities
            logger.info(f"✅ 发现 {len(opportunities)} 个三角套利机会")
        except Exception as e:
            logger.error(f"❌ 三角套利扫描失败: {str(e)}")
        
        # 3. 稳定币套利
        logger.info("\n3️⃣ 扫描稳定币套利...")
        try:
            opportunities = self.strategies["stablecoin_arbitrage"].scan_opportunities()
            all_opportunities["stablecoin_arbitrage"] = opportunities
            logger.info(f"✅ 发现 {len(opportunities)} 个稳定币套利机会")
        except Exception as e:
            logger.error(f"❌ 稳定币套利扫描失败: {str(e)}")
        
        # 4. DEX 套利
        logger.info("\n4️⃣ 扫描 DEX 套利...")
        try:
            opportunities = self.strategies["dex_arbitrage"].scan_opportunities()
            all_opportunities["dex_arbitrage"] = opportunities
            logger.info(f"✅ 发现 {len(opportunities)} 个 DEX 套利机会")
        except Exception as e:
            logger.error(f"❌ DEX 套利扫描失败: {str(e)}")
        
        # 5. 跨链套利
        logger.info("\n5️⃣ 扫描跨链套利...")
        try:
            opportunities = self.strategies["cross_chain_arbitrage"].scan_opportunities()
            all_opportunities["cross_chain_arbitrage"] = opportunities
            logger.info(f"✅ 发现 {len(opportunities)} 个跨链套利机会")
        except Exception as e:
            logger.error(f"❌ 跨链套利扫描失败: {str(e)}")
        
        # 6. Flash Loan 套利
        logger.info("\n6️⃣ 扫描 Flash Loan 套利...")
        try:
            opportunities = self.strategies["flash_loan_arbitrage"].scan_opportunities()
            all_opportunities["flash_loan_arbitrage"] = opportunities
            logger.info(f"✅ 发现 {len(opportunities)} 个 Flash Loan 套利机会")
        except Exception as e:
            logger.error(f"❌ Flash Loan 套利扫描失败: {str(e)}")
        
        # 7. 期权套利
        logger.info("\n7️⃣ 扫描期权套利...")
        try:
            opportunities = self.strategies["options_arbitrage"].scan_opportunities()
            all_opportunities["options_arbitrage"] = opportunities
            logger.info(f"✅ 发现 {len(opportunities)} 个期权套利机会")
        except Exception as e:
            logger.error(f"❌ 期权套利扫描失败: {str(e)}")
        
        # 统计总数
        total_opportunities = sum(len(opps) for opps in all_opportunities.values())
        logger.info("\n" + "="*60)
        logger.info(f"📊 本次扫描发现 {total_opportunities} 个套利机会")
        logger.info("="*60)
        
        return all_opportunities
    
    def display_summary(self, opportunities):
        """显示机会总结"""
        logger.info("\n" + "🎯 套利机会总结" + "\n")
        
        for strategy_name, opps in opportunities.items():
            if opps:
                logger.info(f"\n{strategy_name.upper()}: {len(opps)} 个机会")
                for i, opp in enumerate(opps, 1):
                    logger.info(
                        f"  {i}. {opp.crypto}: "
                        f"{opp.buy_exchange} → {opp.sell_exchange} = "
                        f"{opp.profit_rate:.2f}% 利润"
                    )
    
    def run_continuous(self, scan_interval=300):
        """持续运行套利扫描"""
        logger.info(f"🤖 启动连续套利扫描 (间隔: {scan_interval}秒)")
        
        iteration = 0
        try:
            while True:
                iteration += 1
                logger.info(f"\n📍 扫描周期 #{iteration}")
                logger.info("-"*60)
                
                # 扫描所有机会
                opportunities = self.scan_all_opportunities()
                
                # 显示总结
                self.display_summary(opportunities)
                
                # 可选: 执行自动交易
                # for strategy_name, opps in opportunities.items():
                #     for opp in opps:
                #         self._execute_trade(strategy_name, opp)
                
                # 等待下一次扫描
                logger.info(f"\n⏱️  等待 {scan_interval} 秒后进行下一次扫描...\n")
                time.sleep(scan_interval)
        
        except KeyboardInterrupt:
            logger.info("\n🛑 套利扫描已停止")
        except Exception as e:
            logger.error(f"❌ 发生错误: {str(e)}")
    
    def _execute_trade(self, strategy_name, opportunity):
        """执行单个套利交易"""
        try:
            logger.info(f"\n⚡ 执行 {strategy_name} 交易...")
            
            if strategy_name == "spot_arbitrage":
                self.strategies[strategy_name].execute_trade(opportunity, amount=0.01)
            elif strategy_name == "stablecoin_arbitrage":
                self.strategies[strategy_name].execute_trade(opportunity, amount=10000)
            elif strategy_name in ["dex_arbitrage", "cross_chain_arbitrage"]:
                self.strategies[strategy_name].execute_trade(opportunity, amount=1)
            
        except Exception as e:
            logger.error(f"❌ 交易执行失败: {str(e)}")


def main():
    """主程序"""
    logger.info("🚀 加密货币全方位套利机器人启动")
    logger.info("="*60)
    
    # 初始化管理器
    manager = UnifiedArbitrageManager()
    
    # 启动连续扫描
    manager.run_continuous(scan_interval=300)  # 每 5 分钟扫描一次


if __name__ == "__main__":
    main()
