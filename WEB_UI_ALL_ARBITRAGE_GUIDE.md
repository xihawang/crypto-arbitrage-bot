# 全能套利机器人 Web UI 完整使用指南

## 📋 目录
1. [功能概览](#功能概览)
2. [快速开始](#快速开始)
3. [UI 界面详解](#ui-界面详解)
4. [所有套利策略](#所有套利策略)
5. [实时数据展示](#实时数据展示)
6. [API 接口](#api-接口)
7. [故障排除](#故障排除)

---

## 🎯 功能概览

### 支持的 8 种套利策略

| 策略 | 中文名称 | 风险等级 | 收益率 | 实时监控 |
|------|--------|--------|-------|--------|
| spot_arbitrage | 现货套利 | 🟢 低 | 0.2%-2% | ✅ |
| triangle_arbitrage | 三角套利 | 🟡 中 | 0.5%-3% | ✅ |
| stablecoin_arbitrage | 稳定币套利 | 🟢 低 | 0.1%-1% | ✅ |
| dex_arbitrage | DEX 套利 | 🟡 中 | 0.5%-5% | ✅ |
| cross_chain_arbitrage | 跨链套利 | 🟡 中 | 1%-10% | ✅ |
| flash_loan_arbitrage | 闪电贷套利 | 🔴 高 | 0.3%-2% | ✅ |
| options_arbitrage | 期权套利 | 🔴 高 | 1%-50% | ✅ |
| futures_arbitrage | 期货套利 | 🟡 中 | 0.2%-5% | ✅ |

### 核心功能

- ✅ **实时价格监控** - 从 CoinGecko、币安、Coinbase、Kraken 获取多源价格
- ✅ **套利机会检测** - 自动扫描所有 8 种策略的机会
- ✅ **WebSocket 推送** - 实时推送最新数据无需手动刷新
- ✅ **策略过滤** - 按策略类型查看特定的套利机会
- ✅ **价格对比** - 展示各交易所的价格差异
- ✅ **统计分析** - 显示各策略的机会数量和风险等级
- ✅ **手动扫描** - 支持立即触发一次完整扫描

---

## 🚀 快速开始

### 方式 1: 使用启动脚本（推荐）

```bash
# 进入项目目录
cd /Users/longwang/crypto-arbitrage-bot

# 赋予执行权限
chmod +x run_all_arbitrage_ui.sh

# 启动 Web UI
./run_all_arbitrage_ui.sh
```

### 方式 2: 直接运行 Python

```bash
cd /Users/longwang/crypto-arbitrage-bot

python3 -c "
import sys
sys.path.insert(0, '.')
from web.app_all_arbitrage import main
main()
"
```

### 方式 3: 通过 Flask

```bash
cd /Users/longwang/crypto-arbitrage-bot

export FLASK_APP=web/app_all_arbitrage.py
export FLASK_ENV=production

flask run --host=0.0.0.0 --port=5000
```

### 启动后

```
🤖 启动全能 Web UI 仪表板
============================================================

📡 Web 服务启动参数:
  地址: http://localhost:5000
  调试模式: OFF
  WebSocket: 启用

========================================
💻 打开浏览器访问: http://localhost:5000
========================================
```

---

## 🎨 UI 界面详解

### 1. 顶部状态栏

```
🤖 全能套利机器人 v2.0  |  🟢 实时监控中  |  最后更新: HH:MM:SS  |  连接客户端: N
```

- **绿色指示灯** - 表示已连接到服务器
- **更新时间** - 显示最后一次数据更新的时间
- **客户端数** - 当前连接的客户端数量

### 2. 统计卡片

展示 4 个关键指标：

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ 总套利机会      │  │ 活跃策略        │  │ 监控币种        │  │ 扫描状态        │
│      12         │  │      8          │  │      25         │  │      就绪        │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 3. 策略概览（左上面板）

显示 8 个策略盒子，点击可选择查看特定策略的机会：

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 现货套利     │  │ 三角套利     │  │ 稳定币套利   │
│      2       │  │      1       │  │      3       │
└──────────────┘  └──────────────┘  └──────────────┘

[🔍 立即扫描]
```

### 4. 实时价格面板（右上）

实时显示各币种的价格差异：

```
💰 BTC
价差: 0.0578%  →  $85,782.53 (币安)
                    $85,733.00 (CoinGecko)
🔍 可套利

💰 ETH
价差: 0.0968%  →  $2,812.10 (Coinbase)
                    $2,809.38 (CoinGecko)
✅ 无机会
```

### 5. 套利机会详情面板（下方）

按策略分类显示具体的套利机会：

```
[现货套利]  [三角套利]  [稳定币套利]  [DEX套利]  ...

🎯 BTC
↑ 1.25%
💵 买入: 币安 @ $85,733.00
💰 卖出: Coinbase @ $86,799.00
⏰ 21:41:30

🎯 ETH
↑ 0.82%
💵 买入: CoinGecko @ $2,809.38
💰 卖出: Coinbase @ $2,812.10
⏰ 21:41:31
```

---

## 📊 所有套利策略详解

### 1. 现货套利 (Spot Arbitrage)

**工作原理**
在不同交易所的价格差异中获利

**示例**
```
币安 BTC: $50,000
Coinbase BTC: $50,100

买入币安: 1 BTC = $50,000
卖出 Coinbase: 1 BTC = $50,100
利润: $100 (0.2%)
```

**风险**: 🟢 低 (差价通常很小，需考虑交易费)

---

### 2. 三角套利 (Triangle Arbitrage)

**工作原理**
利用三个交易对的价格不一致

**示例**
```
路径: BTC → ETH → USDT → BTC

1. 买入: 1 BTC = 15 ETH
2. 买入: 15 ETH = 150,000 USDT
3. 买入: 150,000 USDT = 1.05 BTC

利润: 0.05 BTC
```

**风险**: 🟡 中 (需快速执行，容易错过机会)

---

### 3. 稳定币套利 (Stablecoin Arbitrage)

**工作原理**
利用稳定币 (USDT、USDC、DAI、BUSD) 的汇率差异

**示例**
```
交易所 A: 1 USDT = 1.001 USDC
交易所 B: 1 USDC = 0.999 USDT

买入: 10,000 USDT
转换: 10,010 USDC
转换回: 9,999.9 USDT

损失: -$0.1 (需更大的价差才能盈利)
```

**风险**: 🟢 低 (稳定币波动小，但差价微小)

---

### 4. DEX 套利 (Decentralized Exchange Arbitrage)

**工作原理**
在去中心化交易所间套利 (Uniswap、Curve、PancakeSwap)

**特点**
- 需考虑 Gas 费用
- 可能有滑点影响
- 无需 KYC

**风险**: 🟡 中 (Gas 费波动大)

---

### 5. 跨链套利 (Cross-Chain Arbitrage)

**工作原理**
同一资产在不同区块链的价格差异

**示例**
```
USDC 在 Ethereum: $1.001
USDC 在 Arbitrum: $0.998

买入: Arbitrum 上 USDC
跨链桥接 → Ethereum
卖出: 获利

成本: 桥接费 (通常 $1-5)
利润: 仅适合大额交易
```

**支持链**: Ethereum, Polygon, Arbitrum, Optimism

**风险**: 🟡 中 (桥接有延迟和成本)

---

### 6. 闪电贷套利 (Flash Loan Arbitrage)

**工作原理**
使用闪电贷进行无本套利 (需在同一交易内完成)

**特点**
- 无需前期资金
- 必须在同一块生成完成
- 需付出闪电贷费用 (通常 0.05%)

**风险**: 🔴 高 (需精确计算，失败则亏损费用)

---

### 7. 期权套利 (Options Arbitrage)

**工作原理**
利用期权市场的定价错误

**包括**
- **Put-Call 平价违反**: C - P ≠ S - K
- **垂直价差**: 同到期日不同行权价
- **日历价差**: 不同到期日同行权价

**示例**
```
看涨期权 (C): $2.50
看跌期权 (P): $1.00
现货价格 (S): $100
行权价 (K): $100

理论: C - P = S - K = $100
实际: $2.50 - $1.00 = $1.50 ≠ $100

如果实际 > 理论，则做空看涨+做多看跌
```

**风险**: 🔴 高 (需精通期权知识)

---

### 8. 期货套利 (Futures Arbitrage)

**工作原理**
现货与期货价格差异套利

**包括两种类型**

**类型 A: Spot-Futures**
```
现货: $50,000
3月期货: $50,500

操作:
1. 买现货: $50,000
2. 卖期货: $50,500
3. 持有至到期

利润: $500 (考虑融资成本)
```

**类型 B: 日历价差**
```
近月期货: $50,200
远月期货: $50,400

买近月，卖远月
收益差价
```

**风险**: 🟡 中 (需考虑融资成本和交割日期)

---

## 📈 实时数据展示

### 价格数据结构

```json
{
  "BTC": {
    "prices": {
      "CoinGecko": 85733.00,
      "币安": 85782.53,
      "Coinbase": 85775.99,
      "Kraken": 85987.70
    },
    "max_price": 85987.70,
    "min_price": 85733.00,
    "diff_rate": 0.0578,
    "arbitrage_possible": false,
    "timestamp": "2025-12-02T21:41:30.005090"
  }
}
```

### 机会数据结构

```json
{
  "spot_arbitrage": [
    {
      "crypto": "BTC",
      "buy_exchange": "币安",
      "buy_price": 85733.00,
      "sell_exchange": "Coinbase",
      "sell_price": 85775.99,
      "profit_rate": 0.0501,
      "timestamp": "2025-12-02T21:41:30"
    }
  ]
}
```

---

## 🔌 API 接口

### 1. 获取实时价格

```bash
GET http://localhost:5000/api/prices

响应:
{
  "prices": {...},
  "timestamp": "2025-12-02T21:41:30"
}
```

### 2. 获取所有套利机会

```bash
GET http://localhost:5000/api/opportunities

响应:
{
  "opportunities": {
    "spot_arbitrage": [...],
    "triangle_arbitrage": [...]
  },
  "status": "idle",
  "timestamp": "2025-12-02T21:41:30"
}
```

### 3. 获取特定策略的机会

```bash
GET http://localhost:5000/api/opportunities/spot_arbitrage

响应:
{
  "strategy": "spot_arbitrage",
  "opportunities": [...],
  "count": 5,
  "timestamp": "2025-12-02T21:41:30"
}
```

### 4. 获取价格历史

```bash
GET http://localhost:5000/api/price-history/BTC

响应:
{
  "crypto": "BTC",
  "history": [
    {"timestamp": "...", "price": 85733.00},
    {"timestamp": "...", "price": 85750.00}
  ],
  "count": 50
}
```

### 5. 获取统计数据

```bash
GET http://localhost:5000/api/stats

响应:
{
  "total_opportunities": 12,
  "strategies_count": 8,
  "cryptos_count": 25,
  "connected_clients": 3,
  "scan_status": "idle",
  "opportunities_by_strategy": {
    "spot_arbitrage": 5,
    "triangle_arbitrage": 2,
    ...
  }
}
```

### 6. 手动触发扫描

```bash
POST http://localhost:5000/api/manual-scan

响应:
{
  "status": "scanning",
  "message": "已启动手动扫描"
}
```

---

## 🔧 故障排除

### 问题 1: 无法连接到服务器

**错误信息**
```
Connection refused (拒绝连接)
```

**解决方案**
```bash
# 检查端口是否被占用
lsof -i :5000

# 杀死占用进程
kill -9 <PID>

# 重新启动
./run_all_arbitrage_ui.sh
```

### 问题 2: ImportError

**错误信息**
```
ImportError: cannot import name 'xxx'
```

**解决方案**
```bash
# 检查 Python 路径
cd /Users/longwang/crypto-arbitrage-bot

# 运行前需设置正确的工作目录
pwd  # 应该是 /Users/longwang/crypto-arbitrage-bot

# 重新启动
./run_all_arbitrage_ui.sh
```

### 问题 3: WebSocket 连接失败

**症状**: UI 显示"已断开连接"

**解决方案**
```bash
# 检查防火墙
# 确保 5000 端口未被防火墙阻止

# 重启浏览器并清除缓存
# Cmd + Shift + R (macOS)

# 检查服务器日志
# 查看终端输出是否有错误信息
```

### 问题 4: 数据不更新

**症状**: 价格和机会数据一直不变

**解决方案**
```bash
# 点击 "立即扫描" 按钮手动触发
# 检查后台线程是否在运行

# 从终端查看日志输出
# 应该每 30 秒看到 "价格更新完成"
# 应该每 60 秒看到 "扫描完成"
```

### 问题 5: 高 CPU 占用

**症状**: 应用运行时 CPU 占用很高

**解决方案**
```bash
# 增加扫描间隔
# 编辑 app_all_arbitrage.py
# 修改 time.sleep(30) 和 time.sleep(60) 的值

# 减少监控的币种数量
# 在 src/config.py 中修改 CRYPTOS 列表
```

---

## 💡 使用建议

### 最佳实践

1. **早期测试**
   - 从稳定币套利开始测试
   - 风险较小，数据稳定
   - 验证系统是否正常工作

2. **逐步扩展**
   - 现货套利
   - 三角套利
   - 期货套利
   - 高级策略 (闪电贷、期权)

3. **监控策略**
   - 每天查看 Web UI 仪表板
   - 关注"差价率"指标
   - 设置合适的利润阈值

4. **风险管理**
   - 始终使用小额测试
   - 不要投入全部资金
   - 监控手续费成本

### 优化建议

- **提高扫描频率**: 改为 10 秒更新一次
- **集成更多交易所**: 添加 OKX、Bybit 等
- **设置告警**: 当发现机会时自动通知
- **自动执行**: 集成 API 自动执行交易

---

## 📞 支持

如有问题，请参考：
- 📖 项目文档: `ALL_STRATEGIES_GUIDE.md`
- 📝 配置说明: `src/config.py`
- 🔧 日志文件: `logs/` 目录

---

**版本**: 2.0  
**最后更新**: 2025-12-02  
**作者**: Crypto Arbitrage Bot Team
