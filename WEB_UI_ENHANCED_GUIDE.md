# 🎯 增强版 Web UI 使用指南 (v2.0)

## 📋 目录

- [快速开始](#快速开始)
- [功能介绍](#功能介绍)
- [访问方式](#访问方式)
- [API 文档](#api-文档)
- [WebSocket 事件](#websocket-事件)
- [常见问题](#常见问题)
- [进阶配置](#进阶配置)

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
pip install flask flask-socketio flask-cors python-socketio python-engineio
```

### 2️⃣ 启动 Web 服务

**使用原始版本 (基础功能):**
```bash
python3 web/app.py
```

**使用增强版本 (推荐 - WebSocket 实时推送):**
```bash
python3 web/app_enhanced.py
```

### 3️⃣ 访问仪表板

在浏览器中打开:
```
http://localhost:5000
```

### 4️⃣ 查看日志输出

```
🚀 启动增强版 Web UI 仪表板 (v2.0)
============================================================

📍 访问地址: http://localhost:5000
📊 API 文档: http://localhost:5000/api/v2

✨ 新增功能:
  ⚡ WebSocket 实时推送 (30秒更新)
  📈 历史数据追踪
  💾 数据库存储
  📊 统计分析
  🔔 实时通知
  📱 移动端适配

按 Ctrl+C 停止服务器
```

---

## 🎯 功能介绍

### 📊 实时仪表板

**快速指标卡:**
- 🎯 **套利机会** - 发现的套利机会总数
- 📊 **监控币种** - 正在追踪的加密货币数
- 📈 **最大差价率** - 当前最高套利机会
- ⏱️ **最后更新** - 最近一次扫描时间

### 🚨 套利机会表

显示所有发现的套利机会，包括:
- 币种代码 (BTC, ETH, SOL等)
- 买入交易所和价格
- 卖出交易所和价格
- 差价率 (%)
- 快速执行按钮

**颜色编码:**
- 🔴 红色 (> 0.3%) - 高利润机会
- 🟠 橙色 (0.2-0.3%) - 中等利润
- 🟢 绿色 (< 0.2%) - 低利润

### 📈 价格数据标签页

- 多交易所价格对比柱状图
- 实时价格数据表格
- 支持单币种详细查看

### 📊 数据分析标签页

- 平均差价率、最小差价率统计
- 套利机会趋势线图
- 扫描状态实时显示

### ⚙️ 设置

- 启用/禁用自动刷新
- 启用/禁用通知
- 导出数据
- 清空缓存

---

## 💻 访问方式

### 🖥️ 桌面浏览器

| 浏览器 | 支持 | 备注 |
|--------|------|------|
| Chrome | ✅ | 推荐，最佳性能 |
| Firefox | ✅ | 完全支持 |
| Safari | ✅ | 完全支持 |
| Edge | ✅ | 完全支持 |

### 📱 移动设备

- 完全响应式设计
- 支持手机和平板
- 触摸优化操作
- PWA 支持 (离线访问)

### 🔗 访问链接

```
主仪表板:     http://localhost:5000
API 文档:    http://localhost:5000/api/v2
WebSocket:   ws://localhost:5000/socket.io/?transport=websocket
```

---

## 📡 API 文档

### REST API 端点

#### 获取系统状态
```bash
GET /api/v2/status

响应:
{
  "status": "running",
  "scan_status": "idle",
  "last_update": "2025-12-02T10:30:45.123456",
  "opportunities_count": 5,
  "cryptos_tracked": 3,
  "connected_clients": 2
}
```

#### 获取所有价格
```bash
GET /api/v2/prices

响应:
{
  "prices": {
    "BTC": {
      "币安": {"price": 45000.50, "timestamp": "..."},
      "Coinbase": {"price": 45010.25, "timestamp": "..."}
    },
    "ETH": {...}
  },
  "timestamp": "2025-12-02T10:30:45.123456",
  "count": 3
}
```

#### 获取单币种价格
```bash
GET /api/v2/prices?crypto=BTC

响应:
{
  "crypto": "BTC",
  "prices": {
    "币安": {"price": 45000.50},
    "Coinbase": {"price": 45010.25}
  }
}
```

#### 获取价格历史
```bash
GET /api/v2/price-history/<crypto>?limit=50

响应:
{
  "crypto": "BTC",
  "history": [
    {
      "exchange": "币安",
      "price": 45000.50,
      "timestamp": "2025-12-02T10:30:45"
    },
    ...
  ],
  "count": 50
}
```

#### 获取套利机会
```bash
GET /api/v2/opportunities

响应:
{
  "opportunities": [
    {
      "crypto": "BTC",
      "diff_rate": 0.1542,
      "buy_exchange": "币安",
      "buy_price": 45000.00,
      "sell_exchange": "Coinbase",
      "sell_price": 45069.50,
      "timestamp": "2025-12-02T10:30:45"
    }
  ],
  "count": 5
}
```

#### 获取统计数据
```bash
GET /api/v2/statistics

响应:
{
  "total_opportunities": 5,
  "total_cryptos": 3,
  "avg_diff_rate": 0.1250,
  "max_diff_rate": 0.2500,
  "min_diff_rate": 0.0100,
  "last_scan": "2025-12-02T10:30:45",
  "scan_status": "idle"
}
```

#### 获取 Top N 套利机会
```bash
GET /api/v2/analytics/top-opportunities?n=5

响应:
{
  "top_opportunities": [...],
  "count": 5
}
```

#### 获取价格范围
```bash
GET /api/v2/analytics/price-range/<crypto>

响应:
{
  "crypto": "BTC",
  "max": 45500.00,
  "min": 44500.00,
  "avg": 45000.25,
  "latest": 45050.00,
  "data_points": 100
}
```

#### 手动刷新数据
```bash
POST /api/v2/refresh

响应:
{
  "status": "success",
  "message": "✅ 刷新完成，发现 5 个套利机会",
  "timestamp": "2025-12-02T10:30:45"
}
```

---

## 🔄 WebSocket 事件

### 客户端事件

#### 连接成功
```javascript
socket.on('connected', function(data) {
  console.log('已连接，客户端数:', data.clients);
});
```

#### 价格更新
```javascript
socket.on('price_update', function(data) {
  console.log('价格更新:', data);
  // data.prices - 所有价格
  // data.opportunities - 套利机会
  // data.timestamp - 时间戳
});
```

#### 订阅价格
```javascript
socket.emit('subscribe_prices');
```

#### 请求价格历史
```javascript
socket.emit('request_price_history', {
  crypto: 'BTC'
});

socket.on('price_history', function(data) {
  console.log('价格历史:', data.history);
});
```

### 实时推送频率

- **价格更新**: 每 30 秒
- **机会检测**: 每 30 秒
- **数据库存储**: 每次更新
- **UI 刷新**: 实时 (WebSocket)

---

## ❓ 常见问题

### Q1: 页面加载缓慢？

**A:** 可能原因和解决方案:

1. **交易所 API 响应慢**
   - 检查网络连接
   - 尝试禁用某个交易所
   - 增加超时时间

2. **浏览器缓存**
   ```bash
   按 Ctrl+Shift+Delete 清空缓存
   或 Ctrl+Shift+R 强制刷新
   ```

3. **数据库过大**
   ```bash
   # 清空数据库
   rm arbitrage_bot.db
   ```

### Q2: WebSocket 连接失败？

**A:** 检查以下几点:

1. **服务器是否运行**
   ```bash
   curl http://localhost:5000
   ```

2. **防火墙设置**
   - 允许 5000 端口

3. **重启服务器**
   ```bash
   Ctrl+C 停止
   python3 web/app_enhanced.py 重启
   ```

### Q3: 套利机会不出现？

**A:** 可能原因:

1. **价差太小** - 当前市场波动小
2. **API 密钥失效** - 检查配置
3. **网络连接** - 确保能连接交易所

### Q4: 如何导出数据？

**A:** 目前支持两种方式:

1. **通过 Web UI**
   - 点击 ⚙️ 设置 > 导出数据

2. **直接查询数据库**
   ```bash
   sqlite3 arbitrage_bot.db
   .headers on
   .mode column
   SELECT * FROM opportunities;
   ```

### Q5: 能在移动设备上使用吗？

**A:** 完全支持！

1. 在移动浏览器输入 `http://your-pc-ip:5000`
   (找到你电脑的 IP 地址)

2. 或使用内网穿透工具 (ngrok, frp等)

---

## ⚙️ 进阶配置

### 修改扫描频率

编辑 `web/app_enhanced.py`:

```python
# 第 100 行左右
time.sleep(30)  # 改为你想要的秒数
```

### 修改数据保留期限

编辑 `web/app_enhanced.py`:

```python
# 第 30 行左右
price_history[crypto] = deque(maxlen=100)  # 改为你想要的记录数
```

### 启用 HTTPS

```python
# 在 main() 函数中修改
socketio.run(app, 
    host='0.0.0.0', 
    port=443,
    certfile='cert.pem',
    keyfile='key.pem'
)
```

### 启用用户认证

```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == 'admin' and password == 'your_password'

@app.route('/api/v2/status')
@auth.login_required
def get_status():
    ...
```

### 连接外部数据库

```python
# 改为 PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/arbitrage_db"

from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
```

---

## 📞 获取帮助

### 调试模式

```bash
# 启用详细日志
export DEBUG=1
python3 web/app_enhanced.py
```

### 查看日志

```bash
# 实时查看日志
tail -f arbitrage_bot.log

# 查看特定错误
grep "ERROR" arbitrage_bot.log
```

### 性能监控

```bash
# 监控进程资源占用
watch -n 1 'ps aux | grep app_enhanced'

# 监控数据库大小
ls -lh arbitrage_bot.db
```

---

## 🚀 下一步

### 短期优化 (1-2周)

- [ ] 添加 Telegram 通知
- [ ] 实现交易执行面板
- [ ] 优化 UI/UX

### 中期功能 (3-6周)

- [ ] 集成机器学习预测
- [ ] 添加回测引擎
- [ ] 实现风险管理

### 长期计划 (2-3个月)

- [ ] 多账户管理
- [ ] 云端部署
- [ ] 移动 APP

---

## 📚 参考文档

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Flask-SocketIO 文档](https://flask-socketio.readthedocs.io/)
- [Socket.IO 客户端文档](https://socket.io/docs/v4/client-api/)
- [Chart.js 文档](https://www.chartjs.org/docs/latest/)

---

## 💬 反馈与建议

发现 Bug 或有改进建议？

- 在 GitHub 上提交 Issue
- 发送邮件到 support@example.com
- 加入我们的 Telegram 群组

---

**祝您使用愉快！🎉**

