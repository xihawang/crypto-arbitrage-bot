"""
高级功能使用指南
介绍 WebSocket、机器学习、期权、风险管理等高级功能
"""

# # 🚀 高级功能使用指南

## 目录
1. [WebSocket 实时价格流](#websocket-实时价格流)
2. [机器学习套利预测](#机器学习套利预测)
3. [期权交易所集成](#期权交易所集成)
4. [风险管理系统](#风险管理系统)
5. [Telegram 实时通知](#telegram-实时通知)
6. [Web UI 仪表板](#web-ui-仪表板)
7. [多链部署](#多链部署)

---

## WebSocket 实时价格流

### 简介
WebSocket 提供比 REST API 更低的延迟和更高的实时性，适合频繁交易的场景。

### 功能特性
- ✅ 支持币安和 Coinbase 的 WebSocket
- ✅ 实时价格推送（毫秒级延迟）
- ✅ 自动重连机制
- ✅ 多币种并行监听

### 使用方法

```python
from src.integrations.websocket_price_stream import price_stream_manager

# 启动价格流
async def main():
    await price_stream_manager.start_all_streams()

# 或者只启动币安
async def binance_only():
    await price_stream_manager.start_binance_stream(
        symbols=["btcusdt", "ethusdt", "solusdt"]
    )

# 添加自定义价格处理回调
async def on_price_update(symbol, price, timestamp):
    print(f"[{timestamp}] {symbol.upper()}: ${price:,.2f}")

price_stream_manager.add_price_callback(on_price_update)
```

### 与其他功能集成

```python
# 与套利检测集成
async def detect_arbitrage():
    # 获取最新价格
    prices = price_stream_manager.get_all_latest_prices()
    
    # 进行套利分析
    for crypto in ["btcusdt", "ethusdt"]:
        price = prices.get(crypto)
        if price:
            # 进行套利计算
            pass

# 启动监听
asyncio.run(price_stream_manager.start_all_streams())
```

---

## 机器学习套利预测

### 简介
使用历史价格数据训练机器学习模型，预测未来的套利机会。

### 支持的模型
- 随机森林 (Random Forest)
- 梯度提升 (Gradient Boosting)

### 使用方法

```python
from src.ml.price_predictor import arbitrage_predictor

# 添加价格数据
arbitrage_predictor.add_price_data(
    crypto="BTC",
    timestamp=datetime.now(),
    prices={
        "binance": 85900,
        "coinbase": 85850,
        "kraken": 85950
    }
)

# 训练模型
arbitrage_predictor.train_model("BTC", model_type="rf")

# 预测套利机会
prediction = arbitrage_predictor.predict_arbitrage_opportunity(
    crypto="BTC",
    current_prices={
        "binance": 85900,
        "coinbase": 85850,
        "kraken": 85950
    }
)

print(f"当前差价率: {prediction['current_diff_rate']:.4f}%")
print(f"预测差价率: {prediction['predicted_diff_rate']:.4f}%")
print(f"趋势: {prediction['trend']}")
```

### 批量预测

```python
# 批量预测多个币种
predictions = arbitrage_predictor.predict_batch(
    cryptos=["BTC", "ETH", "SOL"],
    current_prices_dict={
        "BTC": {"binance": 85900, "coinbase": 85850},
        "ETH": {"binance": 2810, "coinbase": 2808},
        "SOL": {"binance": 127.5, "coinbase": 127.3}
    }
)

for pred in predictions:
    if pred['trend'] == 'up':
        print(f"🚀 {pred['crypto']}: 差价率上升趋势")
```

### 模型评估

```python
# 获取模型性能
performance = arbitrage_predictor.get_model_performance("BTC")

print(f"R² 分数: {performance['r2_score']:.4f}")
print(f"MSE: {performance['mse']:.6f}")
print(f"MAE: {performance['mae']:.6f}")
```

---

## 期权交易所集成

### 简介
集成 Deribit 和 Lyra Protocol 的期权交易功能。

### Deribit 集成

```python
from src.exchanges.options_exchange import DeribitConnector

# 初始化连接
deribit = DeribitConnector(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# 获取可用期权
options = deribit.get_available_options(currency="BTC")

for opt in options[:5]:
    print(f"合约: {opt['instrument_name']}")
    print(f"行权价: {opt['strike']}")

# 获取期权价格
price_data = deribit.get_option_price("BTC-31DEC21-50000-C")

print(f"买价: {price_data['bid']}")
print(f"卖价: {price_data['ask']}")
print(f"隐含波动率: {price_data['iv']:.2%}")
print(f"Greeks - Delta: {price_data['delta']:.4f}")
print(f"Greeks - Vega: {price_data['vega']:.4f}")
```

### Lyra Protocol 集成

```python
from src.exchanges.options_exchange import LyraConnector

# 初始化 Lyra
lyra = LyraConnector(contract_address="0x...")

# 获取市场数据
market_data = lyra.get_market_data(market="BTC")

print(f"现货价格: ${market_data['spot_price']:,.2f}")
print(f"IV 排名: {market_data['iv_rank']:.2%}")

# 获取波动率曲面
board_iv = lyra.get_board_volatility("BTC")
print(f"平均 IV: {board_iv:.2%}")
```

### 看跌看涨平价检测

```python
from src.exchanges.options_exchange import OptionsExchange

options_exchange = OptionsExchange(
    deribit_key="key",
    deribit_secret="secret"
)

# 扫描平价违反
violations = options_exchange.scan_put_call_parity_violations("BTC")

for viol in violations:
    if abs(viol['parity_diff']) > 100:
        print(f"🚨 行权价 {viol['strike']}: 平价差异 ${viol['parity_diff']:,.2f}")
```

---

## 风险管理系统

### 简介
完整的头寸管理、止损/止盈、风险评分系统。

### 开启头寸

```python
from src.risk.risk_manager import risk_manager

# 设置账户余额
risk_manager.account_balance = 50000

# 开启 LONG 头寸
position = risk_manager.open_position(
    crypto="BTC",
    exchange="binance",
    side="long",
    quantity=0.5,
    entry_price=85000,
    stop_loss=82000,  # 亏损 3000 USD
    take_profit=90000  # 盈利 2500 USD
)

if position:
    print(f"✅ 开仓成功")
    print(f"风险敞口: ${position.risk_exposure:,.2f}")
```

### 价格更新和自动止损

```python
# 更新价格并检查止损/止盈
closed = risk_manager.update_position_price(
    crypto="BTC",
    exchange="binance",
    current_price=87500
)

if closed:
    for closure in closed:
        print(f"⏸️ {closure['reason']}: ${closure['pnl']:,.2f} ({closure['pnl_rate']:.2f}%)")
```

### 风险评估

```python
# 计算投资组合风险
risk_analysis = risk_manager.calculate_portfolio_risk()

print(f"总敞口: ${risk_analysis['total_exposure']:,.2f}")
print(f"敞口比例: {risk_analysis['exposure_rate']:.2%}")
print(f"风险评分: {risk_analysis['risk_score']:.1f}/100")
print(f"风险等级: {risk_analysis['risk_level']}")

# 获取交易性能
perf = risk_manager.get_position_performance()

print(f"胜率: {perf['win_rate']:.2f}%")
print(f"总收益: ${perf['total_pnl']:,.2f}")
```

### 显示信息

```python
# 显示所有活跃头寸
risk_manager.display_positions()

# 显示风险分析
risk_manager.display_risk_analysis()
```

---

## Telegram 实时通知

### 配置

首先，从 Telegram 获取凭证：
1. 与 @BotFather 聊天创建机器人，获得 Bot Token
2. 与 @userinfobot 聊天获得你的 Chat ID

### 使用方法

```python
from src.notifications.telegram_bot import notification_manager

# 配置 Telegram
notification_manager.telegram.bot_token = "YOUR_BOT_TOKEN"
notification_manager.telegram.chat_id = "YOUR_CHAT_ID"

# 发送套利通知
notification_manager.notify_arbitrage_opportunity({
    "crypto": "BTC",
    "diff_rate": 0.25,
    "buy_exchange": "币安",
    "buy_price": 85850,
    "sell_exchange": "Coinbase",
    "sell_price": 86065
})

# 发送开仓通知
notification_manager.notify_trade_opened({
    "crypto": "ETH",
    "side": "LONG",
    "quantity": 2,
    "price": 2810
})

# 发送平仓通知
notification_manager.notify_trade_closed({
    "crypto": "ETH",
    "quantity": 2,
    "price": 2825,
    "pnl": 30,
    "pnl_rate": 0.53
})

# 发送错误警告
notification_manager.notify_error("币安 API 连接失败")

# 发送日报
notification_manager.send_daily_report({
    "cryptos_scanned": 50,
    "opportunities": 12,
    "trades": 5,
    "total_pnl": 245.67,
    "best_trade": "BTC +$125.45"
})
```

---

## Web UI 仪表板

### 启动仪表板

```bash
# 安装 Streamlit
pip install streamlit plotly

# 启动仪表板
streamlit run web/dashboard.py
```

### 功能

1. **📊 实时价格** - 多交易所价格对比和 24h 走势图
2. **💡 套利机会** - 实时套利机会扫描和分布分析
3. **📈 交易历史** - 交易记录、收益分析、累计收益走势
4. **⚠️ 风险管理** - 风险指标、头寸监控、风险分布
5. **📱 通知设置** - Telegram 配置和通知类型设置
6. **⚙️ 系统设置** - 交易所 API 配置、风险参数、扫描配置

### 访问地址

```
http://localhost:8501
```

---

## 多链部署

### 简介
支持在 Ethereum、Polygon、Arbitrum、Optimism、Base 等多条链上部署合约。

### 支持的链

```python
from src.blockchain.multi_chain_deploy import multi_chain_deployer

# 列出支持的链
multi_chain_deployer.list_supported_chains()

# 输出:
# 🌐 支持的区块链
# • Ethereum (ID: 1)
# • Polygon (ID: 137)
# • Arbitrum One (ID: 42161)
# • Optimism (ID: 10)
# • Base (ID: 8453)
```

### 检查网络状态

```python
# 检查单个网络
status = multi_chain_deployer.check_network_status("ethereum")

print(f"链: {status['chain']}")
print(f"已连接: {status['connected']}")
print(f"最新区块: {status['latest_block']}")
print(f"Gas 价格: {status['gas_price_gwei']:.2f} Gwei")

# 检查所有网络
statuses = multi_chain_deployer.get_all_networks_status()
```

### 部署合约

```python
# 初始化部署器（需要私钥）
deployer = MultiChainDeployer(private_key="0x...")

# 准备合约代码
contract_abi = [...]  # 从编译器获取
contract_bytecode = "0x..."  # 从编译器获取

# 部署到 Polygon
deployment = deployer.deploy_contract(
    chain_name="polygon",
    contract_abi=contract_abi,
    contract_bytecode=contract_bytecode,
    constructor_args=[]
)

if deployment:
    print(f"✅ 部署成功")
    print(f"合约地址: {deployment['contract_address']}")
    print(f"交易 Hash: {deployment['transaction_hash']}")
    print(f"查看: {deployment['explorer_url']}")

# 验证合约
verified = deployer.verify_deployment("polygon", deployment['contract_address'])
```

### 批量部署

```python
# 在多条链上部署同一合约
chains = ["ethereum", "polygon", "arbitrum", "optimism"]

for chain in chains:
    deployment = deployer.deploy_contract(
        chain_name=chain,
        contract_abi=contract_abi,
        contract_bytecode=contract_bytecode
    )
    
    if deployment:
        print(f"✅ {chain.upper()}: {deployment['contract_address']}")

# 显示部署总结
deployer.display_deployment_summary()
```

---

## 集成所有功能的完整示例

```python
import asyncio
from src.integrations.websocket_price_stream import price_stream_manager
from src.ml.price_predictor import arbitrage_predictor
from src.exchanges.options_exchange import options_exchange
from src.risk.risk_manager import risk_manager
from src.notifications.telegram_bot import notification_manager

async def complete_example():
    # 1. 启动 WebSocket 实时价格流
    await price_stream_manager.start_all_streams()
    
    # 2. 获取最新价格
    latest_prices = price_stream_manager.get_all_latest_prices()
    
    # 3. 使用 ML 预测套利机会
    predictions = arbitrage_predictor.predict_batch(
        cryptos=["BTC", "ETH"],
        current_prices_dict=latest_prices
    )
    
    # 4. 扫描期权机会
    violations = options_exchange.scan_put_call_parity_violations()
    
    # 5. 检查风险
    risk_analysis = risk_manager.calculate_portfolio_risk()
    
    # 6. 发送通知
    if predictions and risk_analysis['risk_level'] == "✅ 极低":
        notification_manager.notify_arbitrage_opportunity(predictions[0])

# 运行
asyncio.run(complete_example())
```

---

## 性能优化提示

### 1. WebSocket 优化
- 使用批量订阅减少连接数
- 实现本地缓存减少网络请求
- 定期重连以保持连接稳定

### 2. ML 模型优化
- 定期重训练模型以适应市场变化
- 使用交叉验证防止过拟合
- 监控模型性能指标

### 3. 风险管理优化
- 根据市场波动调整头寸大小
- 使用动态止损而不是固定止损
- 定期审查和调整风险参数

### 4. 通知优化
- 设置通知频率限制避免消息轰炸
- 对通知进行分类和优先级排序
- 定期检查 Telegram 配置是否有效

---

## 故障排除

### WebSocket 连接失败
```python
# 检查网络连接
import asyncio
from src.integrations.websocket_price_stream import BinanceWebSocket

ws = BinanceWebSocket()
try:
    asyncio.run(ws.connect())
except Exception as e:
    print(f"错误: {e}")
    # 检查 RPC 端点和防火墙设置
```

### 机器学习模型错误
```python
# 检查数据质量
predictor = arbitrage_predictor
result = predictor._extract_features("BTC")

if result is None:
    print("❌ 数据不足")
else:
    X, y = result
    print(f"样本数: {len(X)}")
    print(f"特征数: {X.shape[1]}")
```

### Telegram 消息未发送
```python
# 测试连接
bot = notification_manager.telegram
success = bot.send_message("测试消息")

if not success:
    print("❌ Token 或 Chat ID 配置错误")
```

---

## 更新日志

### v1.1 (当前版本)
- ✅ WebSocket 实时价格流
- ✅ 机器学习套利预测
- ✅ 期权交易所集成
- ✅ 完整风险管理系统
- ✅ Telegram 实时通知
- ✅ Web UI 仪表板
- ✅ 多链部署工具

---

## 许可证

MIT License - 详见 LICENSE 文件

---

## 支持

如有问题或建议，请提交 GitHub Issue。

**感谢您使用加密货币套利机器人！** 🚀
