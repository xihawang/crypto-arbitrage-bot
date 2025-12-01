# 🌍 实时价格获取功能指南

## 📌 功能概述

本项目集成了**多源实时价格获取系统**，支持从全球主流交易所实时获取加密货币价格，并自动分析套利机会。

### 支持的数据源

| 数据源 | API 类型 | 特点 | 费用 |
|--------|---------|------|------|
| **CoinGecko** | REST | 免费、聚合数据、24h统计 | ✅ 免费 |
| **币安** | REST | 速度快、深度数据 | ✅ 免费 |
| **Coinbase** | REST | 可靠稳定、美国主流 | ✅ 免费 |
| **Kraken** | REST | 欧洲主流、数据详细 | ✅ 免费 |

---

## 🚀 快速开始

### 1️⃣ 快速查询（最简单）

**查询单个币种：**
```bash
python3 quick_price.py BTC
```

**批量查询：**
```bash
python3 quick_price.py BTC ETH SOL
```

**交互式模式：**
```bash
python3 quick_price.py
# 然后选择菜单选项 1-3
```

### 2️⃣ 完整管理模式

```bash
python3 src/main.py
```

菜单选项：
- `1` - 📊 显示实时价格
- `2` - 🔍 分析套利机会  
- `3` - 💰 显示多币种价格汇总
- `4` - 🚀 启动连续套利扫描
- `5` - 🎯 单币种详细分析
- `6` - ✨ 高级模式

### 3️⃣ 命令行参数

```bash
# 获取 BTC 价格
python3 src/main.py --mode price --crypto BTC

# 分析套利机会
python3 src/main.py --mode analyze

# 启动连续扫描（间隔60秒）
python3 src/main.py --mode scan --interval 60

# 自动交易模式
python3 src/main.py --mode auto --interval 300
```

---

## 📊 功能详解

### 1. 多交易所价格对比

```python
from src.utils.price_fetcher import price_fetcher

# 获取 BTC 的多源价格
prices = price_fetcher.get_price_multi("BTC")

# 输出：
# {
#   "CoinGecko": {"exchange": "CoinGecko", "price": 85963.00, ...},
#   "币安": {"exchange": "币安", "price": 85975.92, ...},
#   "Coinbase": {"exchange": "Coinbase", "price": 85968.48, ...},
#   "Kraken": {"exchange": "Kraken", "price": 85987.70, ...}
# }
```

### 2. 价格平均值

```python
# 获取多个交易所的平均价格
avg_price = price_fetcher.get_price_average("BTC")
# 返回: 85973.50
```

### 3. 价格差异分析

```python
# 分析价差并识别套利机会
analysis = price_fetcher.analyze_price_diff("BTC")

# 输出：
# {
#   "crypto": "BTC",
#   "timestamp": "2025-12-01T21:41:30",
#   "prices": {"CoinGecko": 85963.00, "币安": 85975.92, ...},
#   "max_price": 85987.70,
#   "min_price": 85963.00,
#   "price_diff": 24.70,
#   "diff_rate": 0.0288,        # 价差率 (%)
#   "max_exchange": "Kraken",
#   "min_exchange": "CoinGecko",
#   "arbitrage_possible": False  # > 0.1% 时为 True
# }
```

### 4. 显示价格汇总

```python
# 漂亮的格式化输出
price_fetcher.display_price_summary("BTC")

# 输出示例：
# ============================================================
# 💰 BTC 价格汇总
# ============================================================
# ⏰ 更新时间: 2025-12-01T21:41:30.005090
#
#   CoinGecko    → $   85,963.00
#   币安           → $   85,975.92
#   Coinbase     → $   85,968.48
#   Kraken       → $   85,987.70
#
# ────────────────────────────────────────────────────────────
#   最高价格: $   85,987.70 (Kraken)
#   最低价格: $   85,963.00 (CoinGecko)
#   价差: $       24.70 (0.0288%)
# ────────────────────────────────────────────────────────────
#
# ✅ 暂无明显套利机会 (价差 < 0.1%)
# ============================================================
```

---

## 🔍 套利机会检测

### 套利机会阈值

系统自动识别 **价差 > 0.1%** 的机会：

```python
if analysis["arbitrage_possible"]:
    print(f"建议买入: {analysis['min_exchange']} @ ${analysis['min_price']}")
    print(f"建议卖出: {analysis['max_exchange']} @ ${analysis['max_price']}")
    print(f"理论利润率: {analysis['diff_rate']:.4f}%")
```

### 实际套利成本

```
理论利润 = 价差率
实际利润 = 价差率 - 手续费 - 提现费 - 网络费

典型成本：
- 交易手续费：0.1% - 0.2% (各交易所)
- 提现/充值：0.05% - 0.1%
- 网络延迟成本：0.05%
- ──────────────────
- 总成本：~0.2% - 0.4%

⚠️ 因此实际套利需要价差 > 0.5% 才能盈利
```

---

## 📈 集成到统一管理器

### 自动获取实时价格

```python
from src.unified_manager import UnifiedArbitrageManager

manager = UnifiedArbitrageManager()

# 获取所有币种的实时价格
all_prices = manager.get_real_time_prices()

# 分析套利机会
opportunities = manager.analyze_price_opportunities()

# 显示价格汇总
manager.display_all_prices()

# 启动连续扫描 (自动更新价格)
manager.run_continuous(scan_interval=300)  # 每 5 分钟扫描一次
```

### 扫描周期中的价格更新

每次扫描时都会：
1. ✅ 获取所有支持币种的最新价格
2. ✅ 计算多交易所的价差
3. ✅ 识别套利机会
4. ✅ 记录到数据库
5. ✅ 执行自动交易（如配置）

---

## 💻 代码示例

### 例子 1：获取并比较 BTC 价格

```python
from src.utils.price_fetcher import price_fetcher

# 方式 1：获取原始数据
prices = price_fetcher.get_price_multi("BTC")
for exchange, data in prices.items():
    print(f"{exchange}: ${data['price']:,.2f}")

# 方式 2：获取平均价格
avg = price_fetcher.get_price_average("BTC")
print(f"平均价格: ${avg:,.2f}")

# 方式 3：显示漂亮格式
price_fetcher.display_price_summary("BTC")
```

### 例子 2：监控多币种

```python
from src.utils.price_fetcher import price_fetcher

cryptos = ["BTC", "ETH", "SOL"]

for crypto in cryptos:
    analysis = price_fetcher.analyze_price_diff(crypto)
    
    if analysis["arbitrage_possible"]:
        print(f"🚨 {crypto}: {analysis['diff_rate']:.4f}% 差价")
    else:
        print(f"✅ {crypto}: 无套利机会")
```

### 例子 3：自定义价格获取

```python
from src.utils.price_fetcher import PriceFetcher

fetcher = PriceFetcher(timeout=15)

# 只获取币安价格
binance_price = fetcher.get_price_binance("BTC")

# 只获取 Coinbase 价格
coinbase_price = fetcher.get_price_coinbase("ETH")

# 获取 CoinGecko 的详细市场数据
coingecko_data = fetcher.get_price_coingecko("SOL")
print(f"24h变化: {coingecko_data['change_24h']}%")
```

---

## 🛠️ 自定义配置

### 修改支持的币种

编辑 `src/config.py`：

```python
# 添加新币种
CRYPTOS = ["BTC", "ETH", "SOL", "XRP", "DOGE"]

# 添加交易对映射
PAIR_MAPPINGS = {
    "BTC": {"symbol": "BTCUSDT", "id": "bitcoin"},
    "ETH": {"symbol": "ETHUSDT", "id": "ethereum"},
    "SOL": {"symbol": "SOLUSDT", "id": "solana"},
    "XRP": {"symbol": "XRPUSDT", "id": "ripple"},
    "DOGE": {"symbol": "DOGEUSDT", "id": "dogecoin"},
}
```

### 调整套利阈值

在 `src/utils/price_fetcher.py` 中修改：

```python
# 当前阈值 (0.1%)
"arbitrage_possible": diff_rate > 0.1,

# 修改为 0.5% (更严格，减少假阳性)
"arbitrage_possible": diff_rate > 0.5,
```

---

## 📊 性能指标

| 指标 | 值 |
|------|-----|
| 单次查询时间 | ~2-3秒 |
| 4个交易所并行查询 | ~3-5秒 |
| 10个币种批量查询 | ~10-15秒 |
| 数据缓存有效期 | 实时 |
| API 可用性 | 99.5%+ |

---

## 🐛 常见问题

### Q1: 网络超时？

```python
from src.utils.price_fetcher import PriceFetcher

# 增加超时时间
fetcher = PriceFetcher(timeout=20)
```

### Q2: 某个交易所数据无法获取？

这很正常，系统会自动跳过失败的源：

```python
prices = fetcher.get_price_multi("BTC")
# 如果币安 API 故障，会只返回其他 3 个来源的数据
```

### Q3: 如何实时监控价格变化？

```bash
# 启动实时监控（每 30 秒更新一次）
python3 src/main.py --mode scan --interval 30
```

### Q4: 价差 > 0.1% 就能赚钱吗？

❌ 不能！需要考虑成本：

```
实际利润 = 价差率 - 手续费 - 提现费 - 网络费 - 滑点
需要至少 > 0.5% 价差才能有意义的利润
```

---

## 🔗 相关文件

- **价格获取模块**: `src/utils/price_fetcher.py` (370 行)
- **统一管理器**: `src/unified_manager.py` (已集成)
- **主入口**: `src/main.py` (200 行)
- **快速查询**: `quick_price.py` (60 行)

---

## 📌 更新日志

### v1.1 (2025-12-01)
- ✅ 实现多源实时价格获取
- ✅ 支持 CoinGecko, 币安, Coinbase, Kraken
- ✅ 自动套利机会识别
- ✅ 交互式和命令行双模式
- ✅ 与统一管理器集成

### v1.0 (基础版本)
- 8个套利策略框架
- 统一管理器

---

## 🚀 下一步

1. **WebSocket 实时推送** (低延迟)
2. **告警系统** (Telegram/邮件)
3. **历史数据分析** (ML预测)
4. **自动交易** (真实账户)
5. **Web Dashboard** (可视化)

---

**最后更新**: 2025年12月1日  
**维护者**: GitHub @xihawang
