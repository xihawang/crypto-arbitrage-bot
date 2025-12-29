# 🐳 Docker 部署指南

本指南将帮助你使用Docker容器化部署加密货币套利机器人。

## ⚠️ macOS Docker Desktop 用户注意

如果在macOS上使用Docker Desktop遇到 "RuntimeError: can't start new thread" 错误，这是由于Docker Desktop的资源限制导致的。请：

1. 打开 Docker Desktop
2. 进入 Settings → Resources → Advanced
3. 增加以下配置：
   - CPUs: 至少 4 核
   - Memory: 至少 4GB
4. 点击 "Apply & Restart"
5. 重新构建镜像

或者在Docker Desktop设置中通过以下方式增加资源：
```bash
# 检查Docker资源
docker info
```

## 📋 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB可用内存（推荐4GB+）
- 至少5GB可用磁盘空间
- macOS用户需确保Docker Desktop有足够资源分配

## 🚀 快速开始

### 1. 配置环境变量

复制并编辑环境配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的交易所API密钥和参数：

```env
# 交易所API密钥
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# 交易配置
AUTO_TRADE_ENABLED=False
SIMULATION_MODE=True
DRY_RUN=True
MIN_PROFIT_THRESHOLD=0.01

# 系统配置
SCAN_INTERVAL=10
LOG_LEVEL=INFO
```

### 2. 使用启动脚本（推荐）

```bash
# 构建镜像
./run_docker.sh build

# 启动容器
./run_docker.sh start

# 查看日志
./run_docker.sh logs

# 查看状态
./run_docker.sh status
```

### 3. 手动Docker命令

如果你不使用启动脚本：

```bash
# 构建镜像
docker-compose build

# 启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

## 📦 可用命令

### 启动脚本命令

| 命令 | 说明 |
|------|------|
| `./run_docker.sh build` | 构建Docker镜像 |
| `./run_docker.sh start` | 启动容器 |
| `./run_docker.sh stop` | 停止容器 |
| `./run_docker.sh restart` | 重启容器 |
| `./run_docker.sh logs` | 查看容器日志 |
| `./run_docker.sh status` | 查看容器状态 |
| `./run_docker.sh shell` | 进入容器Shell |
| `./run_docker.sh cleanup` | 清理所有容器和镜像 |
| `./run_docker.sh update` | 更新容器 |

### Docker Compose命令

```bash
# 构建并启动
docker-compose up -d --build

# 查看运行中的容器
docker-compose ps

# 查看实时日志
docker-compose logs -f crypto-arbitrage-bot

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 停止并删除容器、卷、镜像
docker-compose down -v --rmi all
```

## 🌐 访问应用

容器启动后，可以通过以下地址访问：

- **本地访问**: http://localhost:5000
- **网络访问**: http://YOUR_SERVER_IP:5000

## 📂 数据持久化

Docker容器使用Docker卷来持久化数据：

- `bot-data`: 应用数据目录
- `bot-logs`: 日志文件目录

数据在容器删除后仍然保留，除非你明确删除卷：

```bash
# 删除卷（会丢失所有数据）
docker-compose down -v
```

## 🔧 配置选项

### 环境变量

所有配置通过环境变量传入，主要配置项：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `AUTO_TRADE_ENABLED` | `False` | 是否启用自动交易 |
| `SIMULATION_MODE` | `True` | 模拟交易模式 |
| `DRY_RUN` | `True` | 试运行模式 |
| `MIN_PROFIT_THRESHOLD` | `0.01` | 最小利润阈值(%) |
| `MAX_TRADE_SIZE` | `1000` | 最大交易金额 |
| `SCAN_INTERVAL` | `10` | 扫描间隔(秒) |
| `LOG_LEVEL` | `INFO` | 日志级别 |

### 资源限制

默认资源限制：
- CPU限制: 2核
- 内存限制: 2GB
- CPU保留: 0.5核
- 内存保留: 512MB

可以在 `docker-compose.yml` 中调整：

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # 增加CPU限制
      memory: 4G       # 增加内存限制
```

## 🐛 故障排查

### 容器无法启动

```bash
# 查看容器状态
docker-compose ps

# 查看容器日志
docker-compose logs crypto-arbitrage-bot

# 检查容器健康状态
docker inspect --format='{{.State.Health.Status}}' crypto-arbitrage-bot
```

### 端口冲突

如果5000端口已被占用，修改 `docker-compose.yml`：

```yaml
ports:
  - "5001:5000"  # 使用5001端口
```

### 数据库文件权限问题

```bash
# 进入容器
docker-compose exec crypto-arbitrage-bot /bin/bash

# 修复权限
chmod 644 /app/data/*.db
```

### 重建容器

```bash
# 停止容器
docker-compose down

# 删除旧镜像
docker rmi crypto-arbitrage-bot_crypto-arbitrage-bot

# 重新构建
./run_docker.sh build
./run_docker.sh start
```

## 📊 监控和日志

### 实时日志

```bash
# 查看所有日志
docker-compose logs -f

# 只看应用日志
docker-compose logs -f crypto-arbitrage-bot
```

### 容器监控

```bash
# 查看资源使用情况
docker stats crypto-arbitrage-bot

# 查看容器详情
docker inspect crypto-arbitrage-bot
```

## 🔄 更新和维护

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建并启动
./run_docker.sh update

# 或者手动
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 备份数据

```bash
# 备份数据卷
docker run --rm -v crypto-arbitrage-bot_bot-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/data-backup-$(date +%Y%m%d).tar.gz /data

# 备份日志
docker run --rm -v crypto-arbitrage-bot_bot-logs:/logs \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/logs-backup-$(date +%Y%m%d).tar.gz /logs
```

### 恢复数据

```bash
# 恢复数据卷
docker run --rm -v crypto-arbitrage-bot_bot-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/data-backup-20231203.tar.gz -C /
```

## 🔐 安全建议

1. **不要在代码中硬编码API密钥** - 始终使用环境变量
2. **使用`.env`文件** - 但确保它已被添加到`.gitignore`
3. **限制容器权限** - 默认配置已经使用了非root用户
4. **定期更新镜像** - 运行`./run_docker.sh update`
5. **监控日志** - 使用`./run_docker.sh logs`定期检查异常
6. **使用防火墙** - 只暴露必要的端口
7. **启用HTTPS** - 使用Nginx反向代理（见下方）

## 🌐 使用Nginx反向代理

启用Nginx服务：

```bash
# 启动Nginx
docker-compose --profile with-nginx up -d
```

Nginx会在80和443端口上提供服务，自动代理到应用容器。

## 📚 更多信息

- Docker文档: https://docs.docker.com/
- Docker Compose文档: https://docs.docker.com/compose/
- 项目主README: [README.md](../README.md)

## 💡 提示

1. **首次运行**：确保先运行 `./run_docker.sh build` 构建镜像
2. **生产环境**：建议配置真实的API密钥和适当的资源限制
3. **监控**：定期检查日志和容器状态
4. **备份**：定期备份重要数据

## 🆘 获取帮助

如果遇到问题：

1. 查看日志: `./run_docker.sh logs`
2. 检查状态: `./run_docker.sh status`
3. 进入容器调试: `./run_docker.sh shell`
4. 查看项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
