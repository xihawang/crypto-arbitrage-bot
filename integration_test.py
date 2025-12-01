"""
集成测试脚本 - 展示实时价格功能的集成
测试实时价格获取和套利机会检测
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.price_fetcher import PriceFetcher
from src.utils.logger import setup_logger

logger = setup_logger("integration_test")


def test_price_fetcher():
    """测试价格获取器功能"""
    
    print("\n" + "="*70)
    print("🧪 价格获取器集成测试")
    print("="*70 + "\n")
    
    fetcher = PriceFetcher()
    
    # 测试 1: 获取单个交易所的价格
    print("✅ 测试 1: 从币安获取价格")
    print("-"*70)
    binance_prices = fetcher.get_price_from_binance(["BTCUSDT", "ETHUSDT"])
    for symbol, price in binance_prices.items():
        print(f"   {symbol}: ${price:,.2f}")
    
    # 测试 2: 从 Coinbase 获取价格
    print("\n✅ 测试 2: 从 Coinbase 获取价格")
    print("-"*70)
    coinbase_prices = fetcher.get_price_from_coinbase(["BTC-USD", "ETH-USD"])
    for symbol, price in coinbase_prices.items():
        print(f"   {symbol}: ${price:,.2f}")
    
    # 测试 3: 从 CoinGecko 获取价格
    print("\n✅ 测试 3: 从 CoinGecko 获取价格")
    print("-"*70)
    coingecko_prices = fetcher.get_price_from_coingecko(["bitcoin", "ethereum"])
    for symbol, price in coingecko_prices.items():
        print(f"   {symbol}: ${price:,.2f}")
    
    # 测试 4: 多交易所价格对比
    print("\n✅ 测试 4: BTC 多交易所价格对比")
    print("-"*70)
    fetcher.print_price_report("BTC")
    
    # 测试 5: ETH 多交易所价格对比
    print("\n✅ 测试 5: ETH 多交易所价格对比")
    print("-"*70)
    fetcher.print_price_report("ETH")
    
    # 测试 6: SOL 多交易所价格对比
    print("\n✅ 测试 6: SOL 多交易所价格对比")
    print("-"*70)
    fetcher.print_price_report("SOL")
    
    # 测试 7: 获取原始数据进行分析
    print("\n✅ 测试 7: 原始数据分析")
    print("-"*70)
    btc_data = fetcher.compare_prices("BTC")
    
    if btc_data.get("success"):
        print(f"\n📊 BTC 数据汇总:")
        print(f"   交易所数量: {btc_data['statistics']['exchanges_count']}")
        print(f"   价格范围: ${btc_data['statistics']['lowest']:,.2f} - ${btc_data['statistics']['highest']:,.2f}")
        print(f"   价差率: {btc_data['statistics']['difference_rate']:.3f}%")
        
        if btc_data['arbitrage_opportunity']['detected']:
            print(f"\n🚨 套利机会详情:")
            print(f"   {btc_data['arbitrage_opportunity']['message']}")
        else:
            print(f"\n✅ 暂无套利机会")
    
    print("\n" + "="*70)
    print("✅ 集成测试完成!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        test_price_fetcher()
    except Exception as e:
        logger.error(f"❌ 测试失败: {str(e)}", exc_info=True)
        print(f"\n❌ 测试失败: {str(e)}")
