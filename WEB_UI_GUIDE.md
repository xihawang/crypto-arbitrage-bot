# 🌐 Web UI 仪表板 - 完整使用指南

## 📍 访问地址

| 访问方式 | 地址 |
|---------|------|
| **本地访问** | http://localhost:5000 |
| **网络访问** | http://YOUR_IP:5000 |
| **API 基地址** | http://localhost:5000/api |

## 🚀 启动 Web UI

### 方式 1：使用启动脚本（推荐）
```bash
cd /Users/longwang/crypto-arbitrage-bot
chmod +x run_web_ui.sh
./run_web_ui.sh
```

### 方式 2：直接运行
```bash
cd /Users/longwang/crypto-arbitrage-bot
python3 -m web.app
```

### 方式 3：使用 Python 交互模式
```bash
cd /Users/longwang/crypto-arbitrage-bot
python3
>>> from web.app import main
>>> main()
```

## 🎨 Web UI 功能概览

### 1. 📊 实时仪表板
启动后自动打开仪表板，显示：
- ✅ 系统运行状态
- 🔄 最后更新时间
- 📈 套利机会数量
- 🪙 监控币种数量

### 2. 💰 实时价格监控
**显示内容：**
- 多个交易所的实时价格对比
- BTC、ETH、SOL 等主要币种
- 最高/最低价格标记
- 实时价差计算

**刷新方式：**
- 自动刷新：每 60 秒更新一次
- 手动刷新：点击"🔄 立即刷新"按钮

### 3. 🚨 套利机会排行
**功能：**
- 显示所有检测到的套利机会
- 按差价率排序（从高到低）
- 显示建议的买入/卖出交易所
- 实时更新机会列表

**机会指标：**
```
差价率 > 0.1% = 有套利机会
差价率 > 0.5% = 优质机会
差价率 > 1.0% = 高价值机会
```

### 4. 📊 统计数据
展示：
- 总套利机会数
- 监控币种总数
- 最大价差率
- 平均价差率

## 🔌 API 端点详解

### 获取系统状态
```bash
curl http://localhost:5000/api/status
```

**响应示例：**
```json
{
  "status": "running",
  "scan_status": "idle",
  "last_update": "2025-12-02T10:30:45.123456",
  "opportunities_count": 3,
  "cryptos_tracked": 5
}
```

### 获取实时价格
```bash
# 获取所有币种
curl http://localhost:5000/api/prices

# 获取单个币种
curl http://localhost:5000/api/prices?crypto=BTC
```

**响应示例：**
```json
{
  "prices": {
    "BTC": {
      "CoinGecko": {"price": 85733.00, ...},
      "币安": {"price": 85782.53, ...},
      "Coinbase": {"price": 85775.99, ...}
    }
  },
  "timestamp": "2025-12-02T10:30:45.123456",
  "count": 3
}
```

### 获取单币种详细分析
```bash
curl http://localhost:5000/api/price-summary/BTC
```

**响应示例：**
```json
{
  "crypto": "BTC",
  "prices": {
    "CoinGecko": 85733.00,
    "币安": 85782.53,
    "Coinbase": 85775.99
  },
  "max_price": 85782.53,
  "min_price": 85733.00,
  "price_diff": 49.53,
  "diff_rate": 0.0578,
  "max_exchange": "币安",
  "min_exchange": "CoinGecko",
  "avg_price": 85763.84,
  "arbitrage_possible": false,
  "timestamp": "2025-12-02T10:30:45.123456"
}
```

### 获取所有套利机会
```bash
curl http://localhost:5000/api/opportunities
```

**响应示例：**
```json
{
  "opportunities": [
    {
      "crypto": "ETH",
      "diff_rate": 0.1542,
      "buy_exchange": "CoinGecko",
      "buy_price": 2809.38,
      "sell_exchange": "Coinbase",
      "sell_price": 2812.71,
      "timestamp": "2025-12-02T10:30:45.123456"
    }
  ],
  "count": 1,
  "timestamp": "2025-12-02T10:30:45.123456"
}
```

### 获取图表数据
```bash
curl http://localhost:5000/api/chart-data/BTC
```

### 手动刷新数据
```bash
curl -X POST http://localhost:5000/api/refresh
```

## 📱 Web UI 界面说明

### 顶部信息区
| 指标 | 说明 |
|-----|-----|
| 系统状态 | 🟢 运行中/🔵 待机/🔴 错误 |
| 最后更新 | 最后一次数据刷新的时间 |
| 套利机会 | 当前检测到的套利机会数量 |
| 监控币种 | 正在监控的加密货币总数 |

### 中部控制区
- **🔄 立即刷新**：强制立即刷新所有数据
- **⏸️ 自动刷新**：切换自动刷新状态（每 60 秒）

### 统计数据区
展示实时的套利机会统计信息

### 套利机会排行表
优先级排序：
1. 差价率最高的机会
2. 显示建议的交易路径
3. 风险评估

### 实时价格对比表
显示各交易所的最新价格

## 🎯 使用场景

### 场景 1：快速价格查询
1. 打开 http://localhost:5000
2. 查看"实时价格对比"表
3. 找到目标币种的价格
4. 点击"🔄 立即刷新"获取最新数据

### 场景 2：发现套利机会
1. 打开仪表板
2. 查看"🚨 套利机会排行"
3. 按差价率找到最佳机会
4. 记录买入/卖出交易所和价格

### 场景 3：持续监控
1. 启动 Web UI
2. 保持浏览器打开
3. 自动每 60 秒更新一次
4. 有新机会时会显示在列表中

### 场景 4：API 集成
如果想在其他应用中使用数据：
```python
import requests

# 获取套利机会
response = requests.get('http://localhost:5000/api/opportunities')
opportunities = response.json()

# 处理数据
for opp in opportunities['opportunities']:
    print(f"{opp['crypto']}: {opp['diff_rate']:.4f}%")
```

## 🔧 配置和定制

### 修改刷新间隔
编辑 `/Users/longwang/crypto-arbitrage-bot/web/app.py`：

```python
time.sleep(60)  # 改为需要的秒数
```

### 修改监控币种
编辑 `/Users/longwang/crypto-arbitrage-bot/src/config.py`：

```python
CRYPTOS = ["BTC", "ETH", "SOL", "ADA"]  # 添加更多币种
```

### 修改套利阈值
编辑 `price_fetcher.py` 中的：

```python
"arbitrage_possible": diff_rate > 0.1,  # 改为需要的阈值
```

## 🚨 常见问题

### Q: Web UI 无法连接？
**A:** 
1. 确认 Flask 已安装：`pip install flask flask-cors`
2. 检查 5000 端口是否被占用：`lsof -i :5000`
3. 尝试换一个端口，修改 `app.run(port=8000)`

### Q: 数据不更新？
**A:** 
1. 点击"🔄 立即刷新"手动刷新
2. 检查网络连接
3. 检查日志文件查看错误信息

### Q: 如何在远程访问？
**A:** 
1. 修改 `app.run(host='0.0.0.0', port=5000)`
2. 使用 `http://YOUR_SERVER_IP:5000` 访问
3. 确保防火墙允许 5000 端口

### Q: 如何后台运行？
**A:** 
```bash
nohup python3 -m web.app > web.log 2>&1 &
```

## 📊 性能优化建议

- 🔸 自动刷新间隔最小建议 30 秒
- 🔸 同时监控币种不超过 20 个
- 🔸 使用 CDN 加速前端资源
- 🔸 考虑使用 Nginx 反向代理

## 🔒 安全建议

1. **生产环境配置：**
   ```bash
   # 不要使用 debug=True
   # 使用 HTTPS
   # 添加身份验证
   ```

2. **部署到云服务器：**
   ```bash
   # 使用 Gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 web.app:app
   ```

3. **Docker 部署：**
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   EXPOSE 5000
   CMD ["python3", "-m", "web.app"]
   ```

## 📞 支持和反馈

有问题或建议？
- 📧 Email: support@example.com
- 🐛 Bug Report: 提交 Issue
- 💡 Feature Request: 讨论区

---

**版本：** 1.0  
**更新时间：** 2025-12-02  
**维护者：** 加密套利机器人团队
