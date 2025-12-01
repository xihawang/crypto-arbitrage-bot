# Crypto Arbitrage Bot

## 🎯 项目简介

**Crypto Arbitrage Bot** 是一个功能完整的加密货币多策略套利机器人，支持 **8 种不同的套利策略**，内置 **多源实时价格获取系统**，可自动识别套利机会并执行交易。

### ✨ 核心特性

- ✅ **8 种套利策略** - 现货、三角、稳定币、DEX、期货、跨链、闪电贷、期权
- ✅ **多源实时价格** - 币安、Coinbase、Kraken、CoinGecko 四大交易所
- ✅ **自动套利识别** - 实时分析价差并识别交易机会
- ✅ **跨交易所** - 支持现货、期货、DEX、跨链等多个市场
- ✅ **智能管理器** - 统一协调所有策略的运行和交易执行
- ✅ **详细日志** - 完整的交易记录和性能追踪
- ✅ **数据库持久化** - SQLAlchemy ORM 自动存储交易数据

## 🚀 快速开始

### 1. 最快体验 - 实时价格查询（无需 API 密钥）

```bash
# 查看 BTC、ETH 的实时价格对比
python3 quick_price.py BTC ETH

# 或交互式模式
python3 quick_price.py
```

**输出示例：**
```
💰 BTC 价格汇总
============================================================
⏰ 更新时间: 2025-12-01T21:41:30

  CoinGecko    → $   85,963.00
  币安           → $   85,975.92
  Coinbase     → $   85,968.48
  Kraken       → $   85,987.70

────────────────────────────────────────────────────────────
  最高价格: $   85,987.70 (Kraken)
  最低价格: $   85,963.00 (CoinGecko)
  价差: $       24.70 (0.0288%)
────────────────────────────────────────────────────────────
✅ 暂无明显套利机会 (价差 < 0.1%)
```

### 2. 完整功能体验

```bash
# 交互式主菜单
python3 src/main.py

# 或直接使用命令行参数
python3 src/main.py --mode price --crypto BTC
python3 src/main.py --mode analyze
python3 src/main.py --mode scan --interval 60
```

## 📚 功能详解

### 🌍 实时价格功能（已集成）

| 功能 | 文件 | 描述 |
|------|------|------|
| **多源价格** | `src/utils/price_fetcher.py` | 从 4 个交易所并行获取价格 |
| **价差分析** | `快速价格.py` | 自动计算价差率并识别套利机会 |
| **主管理器** | `src/unified_manager.py` | 集成到统一管理器，每次扫描自动更新 |
| **交互式** | `src/main.py` | 提供菜单和命令行双界面 |

👉 **详细文档**: 查看 [REAL_TIME_PRICE_GUIDE.md](./REAL_TIME_PRICE_GUIDE.md)

### 📊 8 种套利策略

| # | 策略名称 | 文件 | 风险 | 难度 | 年收益 |
|---|---------|------|------|------|--------|
| 1 | **现货套利** (Cross-Exchange) | `arbitrage.py` | 低 | ⭐ | 0.2%-2% |
| 2 | **三角套利** (Triangle) | `triangle_arbitrage.py` | 低 | ⭐ | 0.1%-1% |
| 3 | **稳定币套利** (Stablecoin) | `stablecoin_arbitrage.py` | 极低 | ⭐ | 0.05%-0.5% |
| 4 | **DEX 套利** | `dex_arbitrage.py` | 中 | ⭐⭐ | 0.5%-5% |
| 5 | **期货套利** (Futures) | `futures_arbitrage.py` | 中 | ⭐⭐ | 1%-10% |
| 6 | **跨链套利** (Cross-Chain) | `cross_chain_arbitrage.py` | 高 | ⭐⭐⭐ | 2%-20% |
| 7 | **闪电贷套利** (Flash Loan) | `flash_loan_arbitrage.py` | 中 | ⭐⭐⭐⭐ | 5%-50% |
| 8 | **期权套利** (Options) | `options_arbitrage.py` | 高 | ⭐⭐⭐⭐ | 5%-50% |

👉 **详细说明**: 查看 [ALL_STRATEGIES_GUIDE.md](./ALL_STRATEGIES_GUIDE.md)

## 📦 项目结构

```
crypto-arbitrage-bot/
├── src/
│   ├── config.py                      # ⚙️ 配置管理
│   ├── main.py                        # 🚀 主入口 (交互式界面)
│   ├── unified_manager.py             # 🎛️ 统一管理器 (协调所有策略)
│   │
│   ├── utils/
│   │   ├── price_fetcher.py          # 💰 多源实时价格获取
│   │   ├── logger.py                 # 📝 日志系统
│   │   └── helpers.py                # 🛠️ 辅助函数
│   │
│   ├── exchanges/
│   │   ├── binance.py                # 🔗 币安连接器
│   │   ├── coinbase.py               # 🔗 Coinbase 连接器
│   │   └── kraken.py                 # 🔗 Kraken 连接器 (基础)
│   │
│   ├── blockchain/
│   │   ├── btc.py                    # ⛓️ BTC 区块链
│   │   ├── eth.py                    # ⛓️ Ethereum 区块链
│   │   └── sol.py                    # ⛓️ Solana 区块链
│   │
│   ├── strategies/
│   │   ├── arbitrage.py              # 现货套利
│   │   ├── triangle_arbitrage.py     # 三角套利
│   │   ├── stablecoin_arbitrage.py   # 稳定币套利
│   │   ├── dex_arbitrage.py          # DEX 套利
│   │   ├── futures_arbitrage.py      # 期货套利
│   │   ├── cross_chain_arbitrage.py  # 跨链套利
│   │   ├── flash_loan_arbitrage.py   # 闪电贷套利
│   │   ├── options_arbitrage.py      # 期权套利
│   │   └── portfolio.py              # 投资组合管理
│   │
│   └── models/
│       └── trade.py                  # 💾 数据库模型
│
├── tests/
│   ├── test_exchanges.py             # 交易所测试
│   ├── test_strategies.py            # 策略测试
│   └── performance_test.py           # 性能测试
│
├── 📄 quick_price.py                 # ⚡ 快速价格查询脚本
├── 📄 test_real_time_price.py        # 价格获取测试
├── 📄 requirements.txt                # 依赖包
├── 📄 .gitignore                     # Git 忽略规则
├── 📄 README.md                      # 本文件
├── 📄 REAL_TIME_PRICE_GUIDE.md       # 🌍 实时价格使用指南
├── 📄 ALL_STRATEGIES_GUIDE.md        # 📊 所有策略详解
└── 📄 COMPLETION_SUMMARY.md          # ✅ 项目完成总结
```

## ⚙️ 安装步骤

### 第 1 步：克隆项目

```bash
git clone https://github.com/xihawang/crypto-arbitrage-bot.git
cd crypto-arbitrage-bot
```

### 第 2 步：创建虚拟环境

```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 第 3 步：安装依赖

```bash
pip install -r requirements.txt
```

### 第 4 步：配置 API 密钥（可选）

只有在需要**执行实际交易**时才需要。查看实时价格**无需 API 密钥**。

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，添加你的 API 密钥
nano .env
```

在 `.env` 中填入以下内容：

```env
# ========== Binance API ==========
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# ========== Coinbase API ==========
COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_API_SECRET=your_coinbase_api_secret_here
```

## 🎮 使用方式

### 🔥 方式 1：快速查询（最推荐新手）

```bash
# 查询 BTC 价格
python3 quick_price.py BTC

# 查询多个币种
python3 quick_price.py BTC ETH SOL

# 交互式菜单
python3 quick_price.py
```

### 🎛️ 方式 2：完整功能菜单

```bash
python3 src/main.py
```

菜单选项：
```
1. 📊 显示实时价格
2. 🔍 分析套利机会
3. 💰 显示多币种价格汇总
4. 🚀 启动连续套利扫描
5. 🎯 单币种详细分析
6. ✨ 高级模式 (自定义)
```

### ⌨️ 方式 3：命令行参数

```bash
# 获取 BTC 实时价格
python3 src/main.py --mode price --crypto BTC

# 分析所有币种的套利机会
python3 src/main.py --mode analyze

# 启动连续扫描 (间隔 60 秒)
python3 src/main.py --mode scan --interval 60

# 自动交易模式
python3 src/main.py --mode auto --interval 300
```

## 💡 代码示例

### 例子 1：获取实时价格

```python
from src.utils.price_fetcher import price_fetcher

# 获取 BTC 的多源价格
prices = price_fetcher.get_price_multi("BTC")

# 显示漂亮格式
price_fetcher.display_price_summary("BTC")

# 获取平均价格
avg_price = price_fetcher.get_price_average("BTC")
print(f"BTC 平均价格: ${avg_price:,.2f}")
```

### 例子 2：分析套利机会

```python
from src.unified_manager import UnifiedArbitrageManager

manager = UnifiedArbitrageManager()

# 分析所有币种的套利机会
opportunities = manager.analyze_price_opportunities()

for opp in opportunities:
    print(f"{opp['crypto']}: 在 {opp['buy_exchange']} 买入，")
    print(f"        在 {opp['sell_exchange']} 卖出，利润 {opp['diff_rate']:.2f}%")
```

### 例子 3：启动套利扫描

```python
from src.unified_manager import UnifiedArbitrageManager

manager = UnifiedArbitrageManager()

# 每 5 分钟扫描一次所有策略
manager.run_continuous(scan_interval=300)
```

## 📊 最近更新

### v1.1 - 实时价格功能 (2025-12-01)
- ✅ 实现多源实时价格获取系统
- ✅ 支持 4 个主流交易所 (币安、Coinbase、Kraken、CoinGecko)
- ✅ 自动套利机会识别和分析
- ✅ 交互式菜单和命令行双界面
- ✅ 集成到统一管理器
- ✅ 完整的使用文档

### v1.0 - 初始版本
- 8 种完整的套利策略框架
- 统一管理器系统
- SQLAlchemy 数据库
- 结构化日志系统

## 📚 文档指南

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| [README.md](./README.md) | 项目概述和快速开始 | 👤 所有人 |
| [REAL_TIME_PRICE_GUIDE.md](./REAL_TIME_PRICE_GUIDE.md) | 🌍 实时价格功能详解 | 👤 想获取实时价格的 |
| [ALL_STRATEGIES_GUIDE.md](./ALL_STRATEGIES_GUIDE.md) | 📊 8 种策略深入解析 | 👤 想了解各种策略的 |
| [COMPLETION_SUMMARY.md](./COMPLETION_SUMMARY.md) | ✅ 项目完成总结 | 👤 项目贡献者 |

## ⚠️ 免责声明

- 🚨 本项目仅用于**教育和研究**目的
- 🚨 请勿用于**实际生产环境**，不对任何交易损失负责
- 🚨 使用本项目前，请充分了解加密货币交易风险
- 🚨 所有交易策略均无法保证盈利

## 🤝 贡献

欢迎提交 Issue 或 Pull Request！

## 📝 许可证

MIT License - 详见 [LICENSE](./LICENSE)

---

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

**最后更新**: 2025年12月1日

# ========== Kraken API ==========
KRAKEN_API_KEY=your_kraken_api_key_here
KRAKEN_API_SECRET=your_kraken_api_secret_here

# ========== 数据库配置 ==========
DB_URL=sqlite:///crypto_arbitrage.db

# ========== 日志配置 ==========
LOG_LEVEL=INFO

# ========== 套利配置 ==========
# 套利利润阈值（百分比，默认 2.0）
ARBITRAGE_THRESHOLD=2.0

# 扫描间隔（秒，默认 300 = 5分钟）
SCAN_INTERVAL=300

# 每次交易的数量（例如 0.01 BTC）
TRADE_AMOUNT=0.01

# 启用自动交易（false = 仅检测，true = 自动执行）
AUTO_TRADE_ENABLED=false
```

#### API 密钥获取说明

**Binance:**
1. 访问 https://www.binance.com/en/account/api-management
2. 点击 "Create API" 
3. 选择 "System generated"
4. 设置 API 限制：勾选 "Spot Trading" 和 "Margin Trading"
5. 设置 IP 白名单（推荐填写你的 IP 地址）
6. 复制 API Key 和 Secret

**Coinbase:**
1. 访问 https://coinbase.com/settings/api
2. 点击 "New API Key"
3. 选择权限：勾选 "wallet:accounts:read" 和 "wallet:transactions:create"
4. 设置通行短语
5. 复制 API Key 和 Secret

**Kraken:**
1. 访问 https://www.kraken.com/settings/api
2. 点击 "Generate New Key"
3. 选择权限：勾选 "Query Funds", "Query Open Orders", "Create & Modify Orders"
4. 复制 API Key 和 Private Key

### 4. 启动套利机器人

#### 模式一：仅监控（推荐先用这个测试）
```bash
python src/main.py
```

输出示例：
```
🚀 加密货币套利机器人启动
============================================================

📍 扫描周期 #1
------------------------------------------------------------
📊 币安 BTC/USDT: $42,500.00
📊 Coinbase BTC/USDT: $42,650.00
💰 BTC/USDT: 低 币安($42,500.00) → 高 Coinbase($42,650.00) = 0.35%

📊 币安 ETH/USDT: $2,350.00
📊 Coinbase ETH/USDT: $2,400.00
🚨 发现套利机会! ETH/USDT: 2.13% 利润

🎯 发现 1 个套利机会:
  - ETH/USDT: 2.13% (币安 → Coinbase)

⏱️  等待 300 秒后进行下一次扫描...
```

#### 模式二：启用自动交易（谨慎使用！）
1. 在 `.env` 中设置：`AUTO_TRADE_ENABLED=true`
2. 确保账户有足够余额
3. 运行：`python src/main.py`

### 5. 查看日志
```bash
# 查看实时日志
tail -f logs/$(date +%Y%m%d).log

# 查看历史日志
cat logs/20251201.log | grep "发现套利机会"

# 统计套利机会数量
grep "发现套利机会" logs/*.log | wc -l
```

### 6. 停止机器人
```bash
# 按 Ctrl+C 停止运行
^C

# 或在后台运行时
killall python
```

## 贡献
欢迎任何形式的贡献！请提交问题或拉取请求。

## 许可证
该项目采用 MIT 许可证，详细信息请参见 LICENSE 文件。