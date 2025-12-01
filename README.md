# Crypto Arbitrage Bot

## 项目简介
Crypto Arbitrage Bot 是一个用于在不同加密货币交易所之间进行套利的自动化交易机器人。该项目支持 BTC、ETH、SOL 及其他山寨币的套利功能，旨在帮助用户利用市场价格差异实现盈利。

## 功能
- 与多个交易所（如 Binance、Coinbase、Kraken）进行交互
- 实时获取市场数据
- 实现套利策略，自动执行交易
- 投资组合管理，跟踪资产和收益
- 日志记录功能，记录交易和系统事件

## 项目结构
```
crypto-arbitrage-bot
├── src
│   ├── main.py               # 应用程序入口点
│   ├── config.py             # 项目配置文件
│   ├── exchanges              # 交易所模块
│   ├── blockchain             # 区块链模块
│   ├── strategies             # 策略模块
│   ├── utils                  # 工具模块
│   └── models                 # 数据模型
├── tests                      # 测试模块
├── requirements.txt           # 依赖包列表
├── .env.example               # 环境变量示例配置
└── README.md                  # 项目文档
```

## 安装
1. 克隆该项目到本地：
   ```
   git clone https://github.com/yourusername/crypto-arbitrage-bot.git
   ```
2. 进入项目目录：
   ```
   cd crypto-arbitrage-bot
   ```
3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用

### 1. 创建虚拟环境
```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件，添加你的交易所 API 密钥
nano .env  # 或用 vim、VS Code 等编辑器打开
```

在 `.env` 中填入以下内容：

```env
# ========== Binance API ==========
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# ========== Coinbase API ==========
COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_API_SECRET=your_coinbase_api_secret_here

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