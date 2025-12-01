"""
快速价格查询脚本 - 直接获取实时 BTC/ETH/SOL 价格
使用方式:
  python3 quick_price.py                    # 交互式模式
  python3 quick_price.py BTC                # 快速查询 BTC
  python3 quick_price.py BTC ETH SOL        # 批量查询
"""

import sys
from src.utils.price_fetcher import price_fetcher
from src.utils.logger import logger


def main():
    """主程序"""
    
    if len(sys.argv) > 1:
        # 命令行模式：直接传入币种
        cryptos = [arg.upper() for arg in sys.argv[1:]]
        
        for crypto in cryptos:
            print(f"\n{'='*60}")
            price_fetcher.display_price_summary(crypto)
    else:
        # 交互式模式
        print("\n" + "="*60)
        print("💰 快速价格查询工具")
        print("="*60)
        
        while True:
            print("\n选项:")
            print("  1. 查询单币种价格")
            print("  2. 批量查询 (BTC, ETH, SOL)")
            print("  3. 分析套利机会")
            print("  0. 退出")
            
            choice = input("\n请选择 (0-3): ").strip()
            
            if choice == "0":
                print("\n👋 再见!\n")
                break
            
            elif choice == "1":
                crypto = input("输入币种代码 (BTC/ETH/SOL): ").upper()
                price_fetcher.display_price_summary(crypto)
            
            elif choice == "2":
                print("\n获取 BTC, ETH, SOL 的价格...")
                for crypto in ["BTC", "ETH", "SOL"]:
                    price_fetcher.display_price_summary(crypto)
            
            elif choice == "3":
                print("\n分析套利机会...")
                
                for crypto in ["BTC", "ETH", "SOL"]:
                    analysis = price_fetcher.analyze_price_diff(crypto)
                    
                    if analysis.get("arbitrage_possible"):
                        print(f"\n🚨 {crypto} 发现套利机会!")
                        print(f"   差价率: {analysis['diff_rate']:.4f}%")
                        print(f"   买入: {analysis['min_exchange']} @ ${analysis['min_price']:,.2f}")
                        print(f"   卖出: {analysis['max_exchange']} @ ${analysis['max_price']:,.2f}")
            
            else:
                logger.error("❌ 无效选择")


if __name__ == "__main__":
    main()
