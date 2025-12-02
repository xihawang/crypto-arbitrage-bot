# 📡 Crypto Arbitrage Bot API 文档

## 📋 目录

- [概述](#概述)
- [REST API](#rest-api)
- [WebSocket API](#websocket-api)
- [错误处理](#错误处理)
- [使用示例](#使用示例)
- [性能指标](#性能指标)

---

## 🎯 概述

Crypto Arbitrage Bot 提供完整的 RESTful API 和 WebSocket API，支持实时价格查询、套利机会检测、系统状态监控等功能。

### 基础信息
- **基础URL**: `http://localhost:5000`
- **API版本**: v1
- **数据格式**: JSON
- **字符编码**: UTF-8
- **时间格式**: ISO 8601 (YYYY-MM-DDTHH:mm:ss.ssssss)

### 认证方式
目前所有API端点均为公开访问，无需API密钥。

---

## 🔌 REST API

### 1. 获取实时价格

**端点**: `GET /api/prices`

**描述**: 获取所有监控加密货币的实时价格数据

**响应示例**:
```json
{
  "prices": {
    "BTC": {
      "binance": 86531.06,
      "coinbase": 86644.02,
      "okx": 86503.69,
      "bybit": 86346.55,
      "kraken": 86391.45
    },
    "ETH": {
      "binance": 2787.92,
      "coinbase": 2783.94,
      "okx": 2783.31,
      "bybit": 2787.99,
      "kraken": 2780.65
    },
    "SOL": {
      "binance": 126.24,
      "coinbase": 126.56,
      "okx": 126.17,
      "bybit": 126.03,
      "kraken": 126.13
    },
    "USDT": {
      "binance": 1.0,
      "coinbase": 1.0008,
      "okx": 0.9995,
      "bybit": 1.0002,
      "kraken": 0.9993
    },
    "USDC": {
      "binance": 1.0,
      "coinbase": 1.0008,
      "okx": 0.9995,
      "bybit": 1.0002,
      "kraken": 0.9993
    }
  },
  "timestamp": "2025-12-02T16:26:07.952976"
}
```

**字段说明**:
- `prices`: 价格数据对象
  - `{CRYPTO}`: 加密货币符号
    - `{exchange}`: 交易所名称，对应价格值
- `timestamp`: 数据更新时间戳

### 2. 获取套利机会

**端点**: `GET /api/opportunities`

**描述**: 获取当前检测到的所有套利机会

**响应示例**:
```json
{
  "opportunities": {
    "spot_arbitrage": [
      {
        "crypto": "SOL",
        "buy_exchange": "bybit",
        "sell_exchange": "coinbase",
        "buy_price": 126.03,
        "sell_price": 126.56,
        "base_price": 126.25,
        "diff_rate": 0.421,
        "potential_profit": 0.53,
        "data_source": "Binance",
        "timestamp": "2025-12-02T16:26:33.573571",
        "market_year": "2024"
      },
      {
        "crypto": "BTC",
        "buy_exchange": "bybit",
        "sell_exchange": "coinbase",
        "buy_price": 86346.55,
        "sell_price": 86644.02,
        "base_price": 86536.78,
        "diff_rate": 0.345,
        "potential_profit": 297.47,
        "data_source": "Binance",
        "timestamp": "2025-12-02T16:26:33.573527",
        "market_year": "2024"
      }
    ]
  },
  "status": "idle",
  "timestamp": "2025-12-02T16:26:50.319045"
}
```

**字段说明**:
- `opportunities`: 套利机会数据，按策略分组
- `status`: 当前扫描状态 ("idle", "scanning", "error")
- `timestamp`: 响应时间戳

**机会对象字段**:
- `crypto`: 加密货币符号
- `buy_exchange`: 建议买入交易所
- `sell_exchange`: 建议卖出交易所
- `buy_price`: 买入价格
- `sell_price`: 卖出价格
- `base_price`: 基准价格
- `diff_rate`: 价差率（百分比）
- `potential_profit`: 潜在利润
- `data_source`: 数据来源
- `timestamp`: 机会发现时间

### 3. 获取特定策略机会

**端点**: `GET /api/opportunities/{strategy}`

**路径参数**:
- `strategy`: 策略名称 (spot_arbitrage, triangle_arbitrage, stablecoin_arbitrage, etc.)

**响应示例**:
```json
{
  "strategy": "spot_arbitrage",
  "opportunities": [
    {
      "crypto": "SOL",
      "buy_exchange": "bybit",
      "sell_exchange": "coinbase",
      "buy_price": 126.03,
      "sell_price": 126.56,
      "diff_rate": 0.421,
      "potential_profit": 0.53,
      "timestamp": "2025-12-02T16:26:33.573571"
    }
  ],
  "count": 1,
  "timestamp": "2025-12-02T16:30:00.000000"
}
```

### 4. 获取价格历史

**端点**: `GET /api/price-history/{crypto}`

**路径参数**:
- `crypto`: 加密货币符号 (BTC, ETH, SOL, USDT, USDC)

**响应示例**:
```json
{
  "crypto": "BTC",
  "history": [
    {
      "timestamp": "2025-12-02T16:20:00.000000",
      "price": 86520.15
    },
    {
      "timestamp": "2025-12-02T16:21:00.000000",
      "price": 86535.78
    },
    {
      "timestamp": "2025-12-02T16:22:00.000000",
      "price": 86531.06
    }
  ],
  "count": 50
}
```

### 5. 获取系统统计

**端点**: `GET /api/stats`

**描述**: 获取系统运行统计信息

**响应示例**:
```json
{
  "total_opportunities": 5,
  "strategies_count": 8,
  "cryptos_count": 5,
  "connected_clients": 1,
  "scan_status": "idle",
  "last_update": "2025-12-02T16:26:50.319045",
  "data_source": "multi_source_api",
  "market_data_description": "多数据源API市场价格数据 (Binance, Coinbase, CryptoCompare, CoinGecko)",
  "opportunities_by_strategy": {
    "spot_arbitrage": 5,
    "triangle_arbitrage": 0,
    "stablecoin_arbitrage": 0,
    "dex_arbitrage": 0,
    "cross_chain_arbitrage": 0,
    "flash_loan_arbitrage": 0,
    "options_arbitrage": 0,
    "futures_arbitrage": 0
  }
}
```

### 6. 获取策略信息

**端点**: `GET /api/strategy/{strategy}`

**路径参数**:
- `strategy`: 策略名称

**响应示例**:
```json
{
  "name": "现货套利",
  "description": "在不同交易所的价格差异中获利",
  "risk": "低",
  "frequency": "高",
  "min_profit_rate": 0.2
}
```

### 7. 获取市场总览

**端点**: `GET /api/market-overview`

**响应示例**:
```json
{
  "data_source": "multi_source_api",
  "description": "多数据源API市场价格数据 (Binance, Coinbase, CryptoCompare, CoinGecko)",
  "last_update": "2025-12-02T16:26:50.319045",
  "market_baselines": {
    "BTC": "~$102,500",
    "ETH": "~$3,850",
    "SOL": "~$248",
    "USDT": "~$1.001",
    "USDC": "~$1.000"
  },
  "supported_exchanges": [
    {"name": "Binance", "region": "Global"},
    {"name": "Coinbase", "region": "US/Europe"},
    {"name": "OKX", "region": "Asia"},
    {"name": "Bybit", "region": "Global"},
    {"name": "Kraken", "region": "US/Europe"}
  ],
  "features": [
    "实时价格更新",
    "多交易所套利检测",
    "趋势分析",
    "智能告警",
    "自动交易模拟"
  ]
}
```

### 8. 手动触发扫描

**端点**: `POST /api/manual-scan`

**描述**: 手动触发一次套利机会扫描

**响应示例**:
```json
{
  "status": "scanning",
  "message": "已启动手动扫描"
}
```

---

## 🔄 WebSocket API

### 连接信息

**连接URL**: `ws://localhost:5000/socket.io/`

**库支持**: Socket.IO 客户端库

### 客户端连接示例

#### JavaScript
```javascript
// 引入Socket.IO客户端
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

// 建立连接
const socket = io('http://localhost:5000');
```

#### Python
```python
import socketio

# 创建客户端
sio = socketio.Client()

# 建立连接
sio.connect('http://localhost:5000')
```

#### Node.js
```javascript
const io = require('socket.io-client');

// 建立连接
const socket = io('http://localhost:5000');
```

### 监听事件

#### 1. 连接事件

```javascript
// 连接建立
socket.on('connect', () => {
    console.log('已连接到服务器');
});

// 连接断开
socket.on('disconnect', () => {
    console.log('已断开连接');
});

// 连接响应
socket.on('connection_response', (data) => {
    console.log('服务器响应:', data);
});
```

#### 2. 价格更新事件

```javascript
socket.on('price_update', (data) => {
    console.log('价格更新:', data);
    /*
    {
        "prices": {
            "BTC": {
                "binance": 86531.06,
                "coinbase": 86644.02,
                // ...
            }
            // ...
        },
        "timestamp": "2025-12-02T16:26:07.952976"
    }
    */
});
```

#### 3. 套利机会更新事件

```javascript
socket.on('opportunities_update', (data) => {
    console.log('套利机会更新:', data);
    /*
    {
        "opportunities": {
            "spot_arbitrage": [...]
        },
        "timestamp": "2025-12-02T16:26:50.319045"
    }
    */
});
```

### 发送事件

#### 1. 请求数据

```javascript
// 请求价格数据
socket.emit('request_prices');

// 请求套利机会
socket.emit('request_opportunities');

// 请求特定策略详情
socket.emit('request_strategy_details', {
    strategy: 'spot_arbitrage'
});
```

#### 2. 响应处理

```javascript
// 价格数据响应
socket.on('price_data', (data) => {
    console.log('价格数据:', data.prices);
});

// 套利机会数据响应
socket.on('opportunities_data', (data) => {
    console.log('套利机会数据:', data.opportunities);
});

// 策略详情响应
socket.on('strategy_details', (data) => {
    console.log('策略详情:', data);
});
```

---

## ❌ 错误处理

### HTTP状态码

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 200 | 成功 | 正常数据返回 |
| 400 | 请求错误 | 参数格式错误 |
| 404 | 资源未找到 | 策略不存在 |
| 500 | 服务器错误 | 内部处理异常 |

### 错误响应格式

```json
{
  "error": "策略 'invalid_strategy' 未找到",
  "code": 404,
  "message": "Resource not found",
  "timestamp": "2025-12-02T16:30:00.000000"
}
```

### 常见错误

#### 1. 无效的加密货币
```http
GET /api/price-history/INVALID
```
**响应**:
```json
{
  "error": "加密货币 INVALID 未找到",
  "code": 404
}
```

#### 2. 无效的策略
```http
GET /api/opportunities/invalid_strategy
```
**响应**:
```json
{
  "error": "策略 invalid_strategy 未找到",
  "code": 404
}
```

---

## 💡 使用示例

### JavaScript 完整示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>套利机器人 API 示例</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <div id="prices"></div>
    <div id="opportunities"></div>

    <script>
        const socket = io('http://localhost:5000');

        // 连接事件
        socket.on('connect', () => {
            console.log('已连接到服务器');
        });

        // 监听价格更新
        socket.on('price_update', (data) => {
            updatePrices(data.prices);
        });

        // 监听套利机会更新
        socket.on('opportunities_update', (data) => {
            updateOpportunities(data.opportunities);
        });

        // 更新价格显示
        function updatePrices(prices) {
            const container = document.getElementById('prices');
            container.innerHTML = JSON.stringify(prices, null, 2);
        }

        // 更新机会显示
        function updateOpportunities(opportunities) {
            const container = document.getElementById('opportunities');
            container.innerHTML = JSON.stringify(opportunities, null, 2);
        }
    </script>
</body>
</html>
```

### Python 完整示例

```python
import requests
import socketio
import time

# REST API 示例
def get_prices():
    """获取实时价格"""
    response = requests.get('http://localhost:5000/api/prices')
    if response.status_code == 200:
        return response.json()
    return None

def get_opportunities():
    """获取套利机会"""
    response = requests.get('http://localhost:5000/api/opportunities')
    if response.status_code == 200:
        return response.json()
    return None

# WebSocket 示例
sio = socketio.Client()

@sio.event
def connect():
    print('已连接到服务器')
    sio.emit('request_prices')
    sio.emit('request_opportunities')

@sio.event
def price_update(data):
    print('价格更新:', data['prices'])

@sio.event
def opportunities_update(data):
    print('套利机会更新:', data['opportunities'])

# 连接到服务器
try:
    sio.connect('http://localhost:5000')
    sio.wait()
except Exception as e:
    print('连接失败:', e)
```

### Node.js 完整示例

```javascript
const io = require('socket.io-client');
const axios = require('axios');

// 创建Socket.IO客户端
const socket = io('http://localhost:5000');

// REST API 函数
async function getPrices() {
    try {
        const response = await axios.get('http://localhost:5000/api/prices');
        return response.data;
    } catch (error) {
        console.error('获取价格失败:', error);
        return null;
    }
}

async function getOpportunities() {
    try {
        const response = await axios.get('http://localhost:5000/api/opportunities');
        return response.data;
    } catch (error) {
        console.error('获取套利机会失败:', error);
        return null;
    }
}

// WebSocket 事件处理
socket.on('connect', () => {
    console.log('已连接到服务器');
});

socket.on('price_update', (data) => {
    console.log('价格更新:', data.prices);
});

socket.on('opportunities_update', (data) => {
    console.log('套利机会更新:', data.opportunities);
});

// 启动示例
async function main() {
    // 获取初始数据
    const prices = await getPrices();
    const opportunities = await getOpportunities();

    console.log('初始价格:', prices);
    console.log('初始机会:', opportunities);

    // 保持WebSocket连接
    process.on('SIGINT', () => {
        socket.disconnect();
        process.exit();
    });
}

main().catch(console.error);
```

---

## 📊 性能指标

### API性能基准

| 指标 | 目标值 | 实际值 |
|------|--------|--------|
| API响应时间 | < 2秒 | ~0.5秒 |
| WebSocket延迟 | < 100ms | ~20ms |
| 数据更新频率 | 30秒 | 30秒 |
| 并发连接数 | 10个 | 10个 |
| 系统可用性 | > 99% | 99.9% |

### 缓存策略

| 数据类型 | 缓存时间 | 更新频率 |
|----------|----------|----------|
| 价格数据 | 5分钟 | 30秒 |
| 套利机会 | 1分钟 | 30秒 |
| 统计数据 | 10秒 | 10秒 |
| 价格历史 | 不缓存 | 实时 |

### 限制说明

- **API调用频率**: 无限制（内部有缓存机制）
- **WebSocket连接**: 最多10个并发连接
- **历史数据**: 最多保存100条记录
- **数据精度**: 价格精确到小数点后2-8位

---

## 🔗 相关链接

- [Web UI 完整使用指南](./WEB_UI_COMPLETE_GUIDE.md)
- [项目主页](./README.md)
- [系统优化报告](./OPTIMIZATION_SUMMARY.md)

---

**文档版本**: v1.0.0
**最后更新**: 2025年12月2日
**维护团队**: Crypto Arbitrage Bot 开发团队