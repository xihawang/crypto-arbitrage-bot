"""
实时价格测试脚本
测试获取 BTC 当前价格的各种方法
"""

import requests
import json
from datetime import datetime


def get_price_from_coingecko():
    """从 CoinGecko 获取 BTC 价格 (免费 API)"""
    try:
        print("\n1️⃣ 从 CoinGecko 获取价格...")
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,solana",
            "vs_currencies": "usd",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("✅ CoinGecko 数据获取成功:\n")
        print(f"  💰 BTC 价格: ${data['bitcoin']['usd']:,.2f}")
        print(f"     24h 涨幅: {data['bitcoin'].get('usd_24h_change', 'N/A'):.2f}%")
        print(f"     市值: ${data['bitcoin'].get('usd_market_cap', 'N/A'):,.0f}")
        
        print(f"\n  💰 ETH 价格: ${data['ethereum']['usd']:,.2f}")
        print(f"     24h 涨幅: {data['ethereum'].get('usd_24h_change', 'N/A'):.2f}%")
        
        print(f"\n  💰 SOL 价格: ${data['solana']['usd']:,.2f}")
        print(f"     24h 涨幅: {data['solana'].get('usd_24h_change', 'N/A'):.2f}%")
        
        return data['bitcoin']['usd']
        
    except Exception as e:
        print(f"❌ CoinGecko 获取失败: {str(e)}")
        return None


def get_price_from_binance():
    """从币安公开 API 获取 BTC 价格"""
    try:
        print("\n2️⃣ 从币安公开 API 获取价格...")
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": "BTCUSDT"}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        btc_price = float(data['price'])
        print(f"✅ 币安数据获取成功:\n")
        print(f"  💰 BTC/USDT: ${btc_price:,.2f}")
        
        return btc_price
        
    except Exception as e:
        print(f"❌ 币安 API 获取失败: {str(e)}")
        return None


def get_price_from_coinbase():
    """从 Coinbase 公开 API 获取 BTC 价格"""
    try:
        print("\n3️⃣ 从 Coinbase 公开 API 获取价格...")
        url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        btc_price = float(data['data']['amount'])
        print(f"✅ Coinbase 数据获取成功:\n")
        print(f"  💰 BTC/USD: ${btc_price:,.2f}")
        
        return btc_price
        
    except Exception as e:
        print(f"❌ Coinbase API 获取失败: {str(e)}")
        return None


def get_price_from_kraken():
    """从 Kraken 公开 API 获取 BTC 价格"""
    try:
        print("\n4️⃣ 从 Kraken 公开 API 获取价格...")
        url = "https://api.kraken.com/0/public/Ticker"
        params = {"pair": "XBTUSDT"}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data['result']:
            ticker_data = data['result'][list(data['result'].keys())[0]]
            btc_price = float(ticker_data['c'][0])  # 最后交易价格
            print(f"✅ Kraken 数据获取成功:\n")
            print(f"  💰 XBT/USDT: ${btc_price:,.2f}")
            
            return btc_price
        
    except Exception as e:
        print(f"❌ Kraken API 获取失败: {str(e)}")
        return None


def compare_prices():
    """对比多个交易所的 BTC 价格"""
    print("\n" + "="*60)
    print("🔍 BTC 实时价格对比")
    print("="*60)
    print(f"⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    prices = {}
    
    # 获取所有价格
    coingecko_price = get_price_from_coingecko()
    if coingecko_price:
        prices['CoinGecko'] = coingecko_price
    
    binance_price = get_price_from_binance()
    if binance_price:
        prices['币安'] = binance_price
    
    coinbase_price = get_price_from_coinbase()
    if coinbase_price:
        prices['Coinbase'] = coinbase_price
    
    kraken_price = get_price_from_kraken()
    if kraken_price:
        prices['Kraken'] = kraken_price
    
    # 显示对比结果
    if prices:
        print("\n" + "="*60)
        print("📊 价格对比汇总")
        print("="*60 + "\n")
        
        for exchange, price in prices.items():
            print(f"  {exchange:12} → ${price:>12,.2f}")
        
        # 计算价差
        max_price = max(prices.values())
        min_price = min(prices.values())
        price_diff = max_price - min_price
        diff_rate = (price_diff / min_price) * 100
        
        print("\n" + "-"*60)
        print(f"  最高价格: ${max_price:,.2f}")
        print(f"  最低价格: ${min_price:,.2f}")
        print(f"  价差: ${price_diff:,.2f} ({diff_rate:.3f}%)")
        print("-"*60)
        
        # 套利机会分析
        if diff_rate > 0.1:
            print(f"\n🚨 发现套利机会!")
            print(f"   在 {[k for k, v in prices.items() if v == min_price][0]} 买入")
            print(f"   在 {[k for k, v in prices.items() if v == max_price][0]} 卖出")
            print(f"   理论利润: {diff_rate:.3f}% (扣除手续费后可能无利)")
        else:
            print(f"\n✅ 暂无明显套利机会 (价差 < 0.1%)")
    else:
        print("\n❌ 无法获取价格数据")
    
    print("\n" + "="*60 + "\n")


def get_btc_24h_stats():
    """获取 BTC 24小时统计数据"""
    try:
        print("\n📈 BTC 24小时统计数据")
        print("-"*60)
        
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        params = {
            "localization": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()['market_data']
        
        print(f"\n  当前价格: ${data['current_price']['usd']:,.2f}")
        print(f"  24h 最高: ${data['high_24h']['usd']:,.2f}")
        print(f"  24h 最低: ${data['low_24h']['usd']:,.2f}")
        print(f"  24h 涨幅: {data['price_change_percentage_24h']:.2f}%")
        print(f"  7日涨幅: {data['price_change_percentage_7d']:.2f}%")
        print(f"  30日涨幅: {data['price_change_percentage_30d']:.2f}%")
        print(f"  1年涨幅: {data['price_change_percentage_1y']:.2f}%")
        print(f"\n  市值: ${data['market_cap']['usd']:,.0f}")
        print(f"  24h 交易量: ${data['total_volume']['usd']:,.0f}")
        print(f"  市值占比: {data['market_cap_percentage']:.2f}%")
        
    except Exception as e:
        print(f"❌ 获取统计数据失败: {str(e)}")


if __name__ == "__main__":
    print("\n" + "🤖 " + "="*56)
    print("     加密货币实时价格测试工具")
    print("=" * 60 + "\n")
    
    # 获取多交易所价格对比
    compare_prices()
    
    # 获取 24 小时统计
    get_btc_24h_stats()
    
    print("\n✅ 测试完成!\n")
