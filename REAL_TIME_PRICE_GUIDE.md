# 🚀 实时价格功能集成指南

## 概述

我已经将实时价格获取功能完全集成到项目中。该功能支持从多个交易所和数据源获取加密货币实时价格，并自动检测套利机会。

---

## 📦 新增模块

### 1. **PriceFetcher** (`src/utils/price_fetcher.py`)

核心价格获取服务，支持多个交易所和数据源：

#### 支持的数据源
- 🟡 **币安 (Binance)** - 现货交易对价格
- 🔵 **Coinbase** - 美元交易对价格  
- 🟣 **Kraken** - 各币种交易对价格
- 🔴 **CoinGecko** - 实时市场数据（无需 API 密钥）

#### 主要方法

```python
from src.utils.price_fetcher import PriceFetcher

# 创建实例
fetcher = PriceFetcher()

# 1. 从单个交易所获取价格
binance_prices = fetcher.get_price_from_binance(["BTCUSDT", "ETHUSDT"])

# 2. 从 Coinbase 获取价格
coinbase_prices = fetcher.get_price_from_coinbase(["BTC-USD", "ETH-USD"])

# 3. 从 CoinGecko 获取价格
coingecko_prices = fetcher.get_price_from_coingecko(["bitcoin", "ethereum"])

# 4. 从 Kraken 获取价格
kraken_prices = fetcher.get_price_from_kraken(["XBTUSDT", "ETHUSDT"])

# 5. 多交易所价格对比
prices = fetcher.get_price_from_all_exchanges("BTC")
# 返回: {"币安": 86054.15, "Coinbase": 85988.74, "Kraken": 86025.70, ...}

# 6. 获取详细对比分析
data = fetcher.compare_prices("BTC")
# 返回包含价格、价差、套利机会等的详细数据

# 7. 打印格式化的价格报告
fetcher.print_price_report("BTC")
```

---

## 🔧 集成到策略中

### ArbitrageBot 更新

`ArbitrageBot` 类已更新以使用新的 PriceFetcher：

```python
from src.strategies.arbitrage import ArbitrageBot

bot = ArbitrageBot()

# 获取多交易所价格
prices = bot.get_prices("BTC")

# 寻找套利机会
result = bot.find_arbitrage_opportunity("BTC")
if result:
    buy_exchange, sell_exchange, min_price, max_price, profit_rate = result
    print(f"在 {buy_exchange} 买 ${min_price:.2f}")
    print(f"在 {sell_exchange} 卖 ${max_price:.2f}")
    print(f"利润率: {profit_rate:.3f}%")
```

### UnifiedArbitrageManager 更新

管理器现在包含实时价格显示功能：

```python
from src.unified_manager import UnifiedArbitrageManager

manager = UnifiedArbitrageManager()

# 显示实时价格
manager.display_real_time_prices(["BTC", "ETH", "SOL"])

# 扫描所有套利机会（包括价格信息）
manager.scan_all_opportunities()
```

---

## 💡 使用示例

### 示例 1: 获取 BTC 实时价格

```python
from src.utils.price_fetcher import PriceFetcher

fetcher = PriceFetcher()

# 获取 BTC 多交易所价格对比
btc_data = fetcher.compare_prices("BTC")

if btc_data.get("success"):
    print(f"BTC 当前价格: ${btc_data['statistics']['average']:,.2f}")
    print(f"最高: ${btc_data['statistics']['highest']:,.2f} ({btc_data['statistics']['highest_exchange']})")
    print(f"最低: ${btc_data['statistics']['lowest']:,.2f} ({btc_data['statistics']['lowest_exchange']})")
    print(f"价差: {btc_data['statistics']['difference_rate']:.3f}%")
```

### 示例 2: 自动检测套利机会

```python
from src.utils.price_fetcher import PriceFetcher

fetcher = PriceFetcher()
data = fetcher.compare_prices("ETH")

if data['arbitrage_opportunity']['detected']:
    arb = data['arbitrage_opportunity']
    print(f"🚨 发现套利机会!")
    print(f"买入: {arb['buy_exchange']}")
    print(f"卖出: {arb['sell_exchange']}")
    print(f"利润率: {arb['profit_rate']:.3f}%")
else:
    print("✅ 暂无套利机会")
```

### 示例 3: 监控多个币种

```python
from src.utils.price_fetcher import PriceFetcher

fetcher = PriceFetcher()

for crypto in ["BTC", "ETH", "SOL"]:
    fetcher.print_price_report(crypto)
```

---

## 🧪 测试

运行集成测试来验证所有功能：

```bash
python3 integration_test.py
```

该测试包括：
- ✅ 从各交易所获取单个价格
- ✅ 多交易所价格对比
- ✅ 套利机会检测
- ✅ 数据格式验证

测试结果示例：
```
📊 BTC 多交易所价格对比
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
币安: $86,054.15
Coinbase: $85,988.74
Kraken: $86,025.70
CoinGecko: $85,948.00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
价差: 0.124%
🚨 套利机会: 在 CoinGecko 买入, 在币安 卖出
```

---

## 📊 返回数据格式

### compare_prices() 返回格式

```python
{
    "success": True,
    "crypto": "BTC",
    "timestamp": "2025-12-01T21:20:59.123456",
    "prices": {
        "币安": 86054.15,
        "Coinbase": 85988.74,
        "Kraken": 86025.70,
        "CoinGecko": 85948.00
    },
    "statistics": {
        "highest": 86054.15,
        "highest_exchange": "币安",
        "lowest": 85948.00,
        "lowest_exchange": "CoinGecko",
        "average": 86004.15,
        "difference": 106.15,
        "difference_rate": 0.124,
        "exchanges_count": 4
    },
    "arbitrage_opportunity": {
        "detected": True,
        "buy_exchange": "CoinGecko",
        "sell_exchange": "币安",
        "profit_rate": 0.124,
        "message": "在 CoinGecko 买入，币安 卖出可获得 0.124% 利润 (扣除手续费后)"
    }
}
```

---

## ⚙️ 配置说明

所有配置项都在 `src/config.py` 中：

```python
# 套利阈值 - 只有价差超过此值才会检测为套利机会
ARBITRAGE_THRESHOLD = 0.1  # 0.1%

# 支持的加密货币
CRYPTOS = ["BTC", "ETH", "SOL", "USDT", "USDC"]

# 价格获取超时时间
TIMEOUT = 10  # 秒
```

---

## 🔐 API 限制说明

| 数据源 | 免费限制 | 认证方式 |
|-------|--------|--------|
| **币安** | 1200 请求/分钟 | 无需认证 |
| **Coinbase** | 10 请求/秒 | 无需认证 |
| **Kraken** | 15 请求/秒 | 无需认证 |
| **CoinGecko** | 10-50 请求/分钟 | 无需认证 |

---

## 🚀 下一步建议

1. **实时监控** - 使用 `display_real_time_prices()` 定时更新价格
2. **自动交易** - 当检测到套利机会时自动执行
3. **数据持久化** - 将价格数据保存到数据库用于分析
4. **性能优化** - 使用 WebSocket 替换 REST API 获取实时推送
5. **告警系统** - 当发现套利机会时发送通知

---

## ❓ 常见问题

**Q: 为什么有时 CoinGecko 请求失败？**
A: CoinGecko 有速率限制。建议在高并发时使用缓存或增加重试延迟。

**Q: 价差 0.124% 能盈利吗？**
A: 需要考虑手续费（通常 0.1-0.2%）和提现费用。建议只在价差 > 0.3% 时交易。

**Q: 如何获取历史价格数据？**
A: 当前获取的是实时价格。历史数据可通过交易所 API 的 OHLCV 端点获取。

**Q: 支持哪些加密货币？**
A: 所有主流币种都支持。需要在交易所中存在交易对。

---

## 📝 最后

实时价格功能已完全集成到项目中，可立即使用。建议先运行 `integration_test.py` 验证环境配置，然后集成到您的交易策略中。

祝交易愉快！ 🎉
