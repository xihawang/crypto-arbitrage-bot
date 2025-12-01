"""
加密货币套利机器人 - 主入口
支持多种运行模式：
1. 实时价格监控
2. 套利机会扫描
3. 连续自动交易
"""

import sys
import argparse
from src.utils.logger import logger
from src.utils.price_fetcher import price_fetcher
from src.config import CRYPTOS
from src.unified_manager import UnifiedArbitrageManager


def print_menu():
    """显示主菜单"""
    print(f"\n{'='*60}")
    print("🤖 加密货币套利机器人")
    print(f"{'='*60}")
    print("\n请选择运行模式:")
    print("  1. 📊 显示实时价格")
    print("  2. 🔍 分析套利机会")
    print("  3. 💰 显示多币种价格汇总")
    print("  4. 🚀 启动连续套利扫描")
    print("  5. 🎯 单币种详细分析")
    print("  6. ✨ 高级模式 (自定义)")
    print("  0. ❌ 退出")
    print(f"\n{'='*60}\n")


def show_real_time_price():
    """显示单个币种的实时价格"""
    crypto = input("请输入加密货币代码 (BTC/ETH/SOL): ").upper()
    
    if crypto not in CRYPTOS and crypto not in ["BTC", "ETH", "SOL"]:
        logger.error(f"❌ 不支持的加密货币: {crypto}")
        return
    
    logger.info(f"\n📊 获取 {crypto} 的实时价格...")
    price_fetcher.display_price_summary(crypto)


def analyze_opportunities():
    """分析套利机会"""
    manager = UnifiedArbitrageManager()
    opportunities = manager.analyze_price_opportunities()
    
    if opportunities:
        print(f"\n📋 套利机会详情:")
        print(f"\n{'币种':<6} {'差价率':<10} {'买入交易所':<12} {'买入价':<15} {'卖出交易所':<12} {'卖出价':<15}")
        print("-" * 75)
        
        for opp in opportunities:
            print(f"{opp['crypto']:<6} {opp['diff_rate']:.4f}%  {opp['buy_exchange']:<12} ${opp['buy_price']:>13,.2f} {opp['sell_exchange']:<12} ${opp['sell_price']:>13,.2f}")


def show_all_prices():
    """显示所有币种的价格"""
    manager = UnifiedArbitrageManager()
    manager.display_all_prices()


def start_continuous_scan():
    """启动连续套利扫描"""
    print("\n⚙️  配置扫描参数:")
    
    try:
        interval = input("输入扫描间隔 (秒，默认300): ").strip()
        interval = int(interval) if interval else 300
        
        if interval < 30:
            logger.warning("⚠️  扫描间隔过短，已调整为 30 秒")
            interval = 30
        
        logger.info(f"\n🚀 启动连续套利扫描 (间隔: {interval} 秒)")
        logger.info("按 Ctrl+C 停止扫描\n")
        
        manager = UnifiedArbitrageManager()
        manager.run_continuous(scan_interval=interval)
        
    except ValueError:
        logger.error("❌ 输入错误：请输入数字")
    except KeyboardInterrupt:
        logger.info("\n✅ 套利扫描已停止")


def single_coin_analysis():
    """单币种详细分析"""
    crypto = input("请输入加密货币代码 (BTC/ETH/SOL): ").upper()
    
    if crypto not in CRYPTOS and crypto not in ["BTC", "ETH", "SOL"]:
        logger.error(f"❌ 不支持的加密货币: {crypto}")
        return
    
    logger.info(f"\n📈 {crypto} 详细分析")
    logger.info(f"{'='*60}\n")
    
    # 获取多源价格
    prices = price_fetcher.get_price_multi(crypto)
    
    print(f"💰 多源价格数据:")
    print(f"{'交易所':<15} {'价格':<20} {'时间':<20}")
    print("-" * 55)
    
    for exchange, data in prices.items():
        timestamp = data.get("timestamp", "").strftime("%H:%M:%S") if hasattr(data.get("timestamp"), "strftime") else str(data.get("timestamp"))
        print(f"{exchange:<15} ${data.get('price'):>18,.2f} {timestamp:<20}")
    
    # 价格分析
    analysis = price_fetcher.analyze_price_diff(crypto)
    
    print(f"\n📊 价格分析:")
    print(f"  平均价格: ${price_fetcher.get_price_average(crypto):,.2f}")
    print(f"  最高价格: ${analysis['max_price']:,.2f} ({analysis['max_exchange']})")
    print(f"  最低价格: ${analysis['min_price']:,.2f} ({analysis['min_exchange']})")
    print(f"  价差: ${analysis['price_diff']:,.2f}")
    print(f"  价差率: {analysis['diff_rate']:.4f}%")
    
    if analysis["arbitrage_possible"]:
        print(f"\n🚨 套利机会检测:")
        print(f"  建议买入: {analysis['min_exchange']} @ ${analysis['min_price']:,.2f}")
        print(f"  建议卖出: {analysis['max_exchange']} @ ${analysis['max_price']:,.2f}")
        print(f"  理论利润率: {analysis['diff_rate']:.4f}%")
    else:
        print(f"\n✅ 暂无明显套利机会 (价差 < 0.1%)")
    
    print(f"\n{'='*60}\n")


def advanced_mode():
    """高级模式 - 自定义选项"""
    print("\n⚙️  高级模式")
    print(f"{'='*60}")
    
    print("\n1. 批量获取多币种价格")
    print("2. 导出价格数据到 CSV")
    print("3. 配置告警阈值")
    print("4. 返回主菜单")
    
    choice = input("\n选择: ").strip()
    
    if choice == "1":
        # 批量获取
        manager = UnifiedArbitrageManager()
        all_prices = manager.get_real_time_prices()
        
        logger.info(f"\n✅ 已获取 {len(all_prices)} 种加密货币的价格数据")
        
        # 统计
        for crypto, exchanges_data in all_prices.items():
            if exchanges_data:
                prices = [p.get("price") for p in exchanges_data.values() if "price" in p]
                if prices:
                    avg = sum(prices) / len(prices)
                    logger.info(f"  {crypto}: ${avg:,.2f} (来源: {len(prices)} 个交易所)")
    
    elif choice == "2":
        logger.info("📁 CSV 导出功能将在下个版本实现")
    
    elif choice == "3":
        logger.info("🔔 告警阈值配置功能将在下个版本实现")


def main():
    """主程序入口"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + "加密货币多策略套利机器人 v1.0".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    # 命令行参数支持
    parser = argparse.ArgumentParser(description="加密货币套利机器人")
    parser.add_argument("--mode", choices=["price", "analyze", "scan", "auto"], help="运行模式")
    parser.add_argument("--crypto", help="指定加密货币")
    parser.add_argument("--interval", type=int, default=300, help="扫描间隔(秒)")
    
    args = parser.parse_args()
    
    # 命令行模式
    if args.mode:
        if args.mode == "price":
            if args.crypto:
                prices = price_fetcher.get_price_multi(args.crypto)
                logger.info(f"✅ {args.crypto} 价格: {prices}")
            else:
                show_real_time_price()
        elif args.mode == "analyze":
            analyze_opportunities()
        elif args.mode == "scan":
            manager = UnifiedArbitrageManager()
            manager.run_continuous(scan_interval=args.interval)
        elif args.mode == "auto":
            logger.info("🚀 启动完整自动交易模式 (需要配置 API 密钥)")
            manager = UnifiedArbitrageManager()
            manager.run_continuous(scan_interval=args.interval)
    else:
        # 交互式模式
        while True:
            print_menu()
            choice = input("请选择 (0-6): ").strip()
            
            if choice == "0":
                logger.info("👋 感谢使用，再见!")
                sys.exit(0)
            elif choice == "1":
                show_real_time_price()
            elif choice == "2":
                analyze_opportunities()
            elif choice == "3":
                show_all_prices()
            elif choice == "4":
                start_continuous_scan()
            elif choice == "5":
                single_coin_analysis()
            elif choice == "6":
                advanced_mode()
            else:
                logger.error("❌ 无效选择，请重试")
            
            input("\n按 Enter 继续...")


if __name__ == "__main__":
    main()