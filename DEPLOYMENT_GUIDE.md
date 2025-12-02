# 🚀 Crypto Arbitrage Bot 部署和配置指南

## 📋 目录

- [部署环境要求](#部署环境要求)
- [快速部署](#快速部署)
- [生产环境部署](#生产环境部署)
- [Docker部署](#docker部署)
- [配置详解](#配置详解)
- [环境变量](#环境变量)
- [监控和维护](#监控和维护)
- [故障排除](#故障排除)

---

## 🖥️ 部署环境要求

### 最低要求
- **操作系统**: Linux (Ubuntu 18.04+), macOS 10.14+, Windows 10+
- **Python**: 3.7+
- **内存**: 2GB RAM
- **存储**: 10GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **操作系统**: Ubuntu 20.04 LTS
- **Python**: 3.9+
- **内存**: 4GB RAM
- **存储**: 20GB SSD
- **CPU**: 2核心以上
- **网络**: 带宽 10Mbps+

### 依赖软件
```bash
# 基础依赖
python3
pip3
git

# 可选依赖（生产环境）
nginx
supervisor
docker
docker-compose
```

---

## ⚡ 快速部署

### 1. 克隆项目
```bash
git clone https://github.com/your-username/crypto-arbitrage-bot.git
cd crypto-arbitrage-bot
```

### 2. 创建虚拟环境
```bash
# Python 3
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境
```bash
# 复制配置文件
cp .env.example .env

# 编辑配置（可选）
nano .env
```

### 5. 启动服务
```bash
# 启动Web界面
python web/app_all_arbitrage.py
```

### 6. 访问应用
- **本地**: http://localhost:5000
- **网络**: http://YOUR_IP:5000

---

## 🏭 生产环境部署

### 1. 系统准备

#### Ubuntu/Debian
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和相关工具
sudo apt install python3 python3-pip python3-venv git nginx supervisor -y

# 安装Node.js（可选，用于前端构建）
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install nodejs -y
```

#### CentOS/RHEL
```bash
# 安装EPEL
sudo yum install epel-release -y

# 安装Python和工具
sudo yum install python3 python3-pip git nginx supervisor -y
```

### 2. 用户和服务配置

#### 创建专用用户
```bash
# 创建系统用户
sudo useradd -r -s /bin/false cryptobot

# 创建应用目录
sudo mkdir -p /opt/crypto-arbitrage-bot
sudo chown cryptobot:cryptobot /opt/crypto-arbitrage-bot
```

#### 部署应用代码
```bash
# 切换到应用目录
cd /opt/crypto-arbitrage-bot

# 克隆代码
sudo -u cryptobot git clone https://github.com/your-username/crypto-arbitrage-bot.git .

# 设置权限
sudo chown -R cryptobot:cryptobot /opt/crypto-arbitrage-bot
sudo chmod +x /opt/crypto-arbitrage-bot/*.py
```

### 3. 环境配置

#### 创建生产环境配置
```bash
sudo nano /opt/crypto-arbitrage-bot/.env
```

**生产环境配置示例**:
```bash
# Flask配置
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-very-secure-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///data/crypto_arbitrage.db

# API配置
API_TIMEOUT=15
CACHE_DURATION=300

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/crypto-arbitrage-bot/app.log

# 安全配置
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SOCKET_CORS_ALLOWED_ORIGINS=https://yourdomain.com

# 性能配置
MAX_CONNECTIONS=20
SCAN_INTERVAL=30
```

#### 创建日志目录
```bash
sudo mkdir -p /var/log/crypto-arbitrage-bot
sudo chown cryptobot:cryptobot /var/log/crypto-arbitrage-bot
```

### 4. Supervisor 配置

#### 创建Supervisor配置文件
```bash
sudo nano /etc/supervisor/conf.d/crypto-arbitrage-bot.conf
```

**配置内容**:
```ini
[program:crypto-arbitrage-bot]
command=/opt/crypto-arbitrage-bot/venv/bin/python /opt/crypto-arbitrage-bot/web/app_all_arbitrage.py
directory=/opt/crypto-arbitrage-bot
user=cryptobot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/crypto-arbitrage-bot/supervisor.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
environment=PATH="/opt/crypto-arbitrage-bot/venv/bin"
```

#### 启动服务
```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start crypto-arbitrage-bot

# 检查状态
sudo supervisorctl status crypto-arbitrage-bot
```

### 5. Nginx 反向代理

#### 创建Nginx配置
```bash
sudo nano /etc/nginx/sites-available/crypto-arbitrage-bot
```

**配置内容**:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL证书配置
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # 日志
    access_log /var/log/nginx/crypto-arbitrage-bot.access.log;
    error_log /var/log/nginx/crypto-arbitrage-bot.error.log;

    # 反向代理
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # WebSocket支持
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 启用站点
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/crypto-arbitrage-bot /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

---

## 🐳 Docker部署

### 1. 创建Dockerfile

```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "web/app_all_arbitrage.py"]
```

### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  crypto-arbitrage-bot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
      - CACHE_DURATION=300
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/stats"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - crypto-arbitrage-bot
    restart: unless-stopped
```

### 3. 构建和运行

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f crypto-arbitrage-bot

# 停止服务
docker-compose down
```

---

## ⚙️ 配置详解

### 1. Flask应用配置

#### config.py 主要参数
```python
class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///crypto_arbitrage.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API配置
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 10))
    CACHE_DURATION = int(os.environ.get('CACHE_DURATION', 300))

    # WebSocket配置
    SOCKET_CORS_ALLOWED_ORIGINS = os.environ.get('SOCKET_CORS_ALLOWED_ORIGINS', '*')

    # 性能配置
    MAX_CONNECTIONS = int(os.environ.get('MAX_CONNECTIONS', 10))
    SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL', 30))
```

### 2. 数据源配置

#### 多数据源优先级
```python
# src/utils/multi_source_price_fetcher.py
API_PRIORITY = [
    ("Binance", fetch_binance_price),      # 最高优先级
    ("Coinbase", fetch_coinbase_price),    # 高优先级
    ("CryptoCompare", fetch_crypto_compare_price),  # 中优先级
    ("CoinGecko", fetch_coingecko_price)   # 最低优先级
]

# 缓存配置
CACHE_DURATION = 300  # 5分钟

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒
```

### 3. 套利策略配置

#### 策略参数
```python
# src/config.py
ARBITRAGE_CONFIG = {
    "spot_arbitrage": {
        "enabled": True,
        "min_profit_rate": 0.15,  # 0.15%
        "max_position_size": 10000,  # $10,000
        "risk_level": "low"
    },
    "triangle_arbitrage": {
        "enabled": True,
        "min_profit_rate": 0.5,   # 0.5%
        "max_position_size": 5000,   # $5,000
        "risk_level": "medium"
    },
    "stablecoin_arbitrage": {
        "enabled": True,
        "min_profit_rate": 0.05,  # 0.05%
        "max_position_size": 50000,  # $50,000
        "risk_level": "low"
    }
}
```

### 4. 监控配置

#### 日志配置
```python
# src/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    # 创建logger
    logger = logging.getLogger('crypto_arbitrage_bot')
    logger.setLevel(logging.INFO)

    # 文件处理器
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

---

## 🌍 环境变量

### 必需变量

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `SECRET_KEY` | Flask密钥 | `dev-secret-key` | `your-secure-key` |
| `FLASK_ENV` | 运行环境 | `development` | `production` |
| `FLASK_DEBUG` | 调试模式 | `True` | `False` |

### 可选变量

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `DATABASE_URL` | 数据库URL | `sqlite:///crypto_arbitrage.db` | `postgresql://user:pass@host/db` |
| `API_TIMEOUT` | API超时时间(秒) | `10` | `15` |
| `CACHE_DURATION` | 缓存时间(秒) | `300` | `600` |
| `MAX_CONNECTIONS` | 最大连接数 | `10` | `20` |
| `SCAN_INTERVAL` | 扫描间隔(秒) | `30` | `60` |
| `LOG_LEVEL` | 日志级别 | `INFO` | `DEBUG` |
| `LOG_FILE` | 日志文件路径 | `logs/app.log` | `/var/log/app.log` |

### 交易所API变量（可选）

```bash
# Binance
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_secret

# Coinbase
COINBASE_API_KEY=your_coinbase_key
COINBASE_API_SECRET=your_coinbase_secret
COINBASE_PASSPHRASE=your_coinbase_passphrase

# 其他交易所...
```

---

## 📊 监控和维护

### 1. 健康检查

#### API健康检查端点
```bash
# 检查系统状态
curl http://localhost:5000/api/stats

# 检查价格数据
curl http://localhost:5000/api/prices

# 检查套利机会
curl http://localhost:5000/api/opportunities
```

#### 系统监控脚本
```bash
#!/bin/bash
# health_check.sh

API_URL="http://localhost:5000/api/stats"
LOG_FILE="/var/log/crypto-arbitrage-bot/health_check.log"

response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $response -eq 200 ]; then
    echo "$(date): API健康检查通过" >> $LOG_FILE
else
    echo "$(date): API健康检查失败，状态码: $response" >> $LOG_FILE
    # 发送告警
    # send_alert.sh "Crypto Arbitrage Bot API异常"
fi
```

### 2. 日志管理

#### 日志轮转配置
```bash
# /etc/logrotate.d/crypto-arbitrage-bot
/var/log/crypto-arbitrage-bot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 cryptobot cryptobot
    postrotate
        supervisorctl restart crypto-arbitrage-bot
    endscript
}
```

### 3. 性能监控

#### 系统资源监控
```bash
#!/bin/bash
# monitor.sh

echo "=== Crypto Arbitrage Bot 监控报告 ==="
echo "时间: $(date)"
echo

# 内存使用
echo "内存使用:"
ps aux | grep 'python.*app_all_arbitrage' | grep -v grep | awk '{print $4"%  "$11}'
echo

# CPU使用
echo "CPU使用:"
top -b -n1 | grep 'python.*app_all_arbitrage' | grep -v grep | awk '{print $9"%  "$12}'
echo

# 网络连接
echo "网络连接:"
netstat -an | grep :5000 | grep ESTABLISHED | wc -l | xargs echo "活跃连接数:"
echo

# 检查进程
echo "进程状态:"
supervisorctl status crypto-arbitrage-bot
```

### 4. 备份策略

#### 数据备份脚本
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/crypto-arbitrage-bot"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
if [ -f "data/crypto_arbitrage.db" ]; then
    cp data/crypto_arbitrage.db $BACKUP_DIR/crypto_arbitrage_$DATE.db
fi

# 备份配置文件
cp .env $BACKUP_DIR/env_$DATE.backup
cp -r logs $BACKUP_DIR/logs_$DATE/

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.backup" -mtime +30 -delete
find $BACKUP_DIR -name "logs_*" -mtime +30 -exec rm -rf {} +

echo "备份完成: $DATE"
```

---

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 服务无法启动

**症状**: Supervisor显示进程启动失败
```bash
# 检查状态
sudo supervisorctl status crypto-arbitrage-bot

# 查看详细日志
sudo tail -f /var/log/crypto-arbitrage-bot/supervisor.log
```

**解决方案**:
```bash
# 检查Python环境
sudo -u cryptobot /opt/crypto-arbitrage-bot/venv/bin/python --version

# 检查权限
sudo -u cryptobot ls -la /opt/crypto-arbitrage-bot/

# 手动启动测试
sudo -u cryptobot /opt/crypto-arbitrage-bot/venv/bin/python /opt/crypto-arbitrage-bot/web/app_all_arbitrage.py
```

#### 2. API返回空数据

**症状**: `/api/prices` 返回空对象
```bash
# 测试API连接
curl -v http://localhost:5000/api/prices
```

**解决方案**:
```bash
# 检查后台线程
grep "价格收集" /var/log/crypto-arbitrage-bot/app.log

# 检查网络连接
curl -s "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

# 重启服务
sudo supervisorctl restart crypto-arbitrage-bot
```

#### 3. WebSocket连接失败

**症状**: 页面显示离线状态
```bash
# 检查端口
netstat -an | grep 5000

# 检查防火墙
sudo ufw status
```

**解决方案**:
```bash
# 配置防火墙
sudo ufw allow 5000/tcp
sudo ufw reload

# 检查Nginx配置
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. 内存使用过高

**症状**: 系统内存不足
```bash
# 检查内存使用
free -h
ps aux | grep 'python.*app_all_arbitrage' | head -5
```

**解决方案**:
```bash
# 调整配置
# 编辑 .env 文件，增加缓存时间
CACHE_DURATION=600

# 减少历史数据长度
# 修改 web/app_all_arbitrage.py
price_history[crypto] = deque(maxlen=50)  # 减少到50条

# 重启服务
sudo supervisorctl restart crypto-arbitrage-bot
```

### 性能优化建议

1. **数据库优化**
   - 定期清理旧数据
   - 添加适当索引
   - 考虑使用PostgreSQL替代SQLite

2. **缓存优化**
   - 使用Redis作为缓存后端
   - 调整缓存时间
   - 实现智能缓存策略

3. **网络优化**
   - 使用CDN加速静态资源
   - 启用Gzip压缩
   - 优化Nginx配置

4. **监控优化**
   - 设置告警阈值
   - 实现自动故障恢复
   - 定期性能测试

---

## 📞 技术支持

### 日志文件位置
- **应用日志**: `/var/log/crypto-arbitrage-bot/app.log`
- **Supervisor日志**: `/var/log/crypto-arbitrage-bot/supervisor.log`
- **Nginx日志**: `/var/log/nginx/crypto-arbitrage-bot.*.log`

### 常用命令
```bash
# 查看服务状态
sudo supervisorctl status

# 重启服务
sudo supervisorctl restart crypto-arbitrage-bot

# 查看实时日志
sudo tail -f /var/log/crypto-arbitrage-bot/app.log

# 检查端口占用
sudo netstat -tlnp | grep 5000
```

---

**文档版本**: v1.0.0
**最后更新**: 2025年12月2日
**维护团队**: Crypto Arbitrage Bot 开发团队