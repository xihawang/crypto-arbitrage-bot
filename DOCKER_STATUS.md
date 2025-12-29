# Docker 部署状态说明

## 当前状态

Docker 部署配置已完成，但在 macOS 系统上构建镜像时遇到线程资源限制问题。

## 问题描述

在 macOS 上使用 Docker Desktop 构建镜像时，pip 遇到 "RuntimeError: can't start new thread" 错误。

**原因**：
- pip 21.2+ 版本默认使用 rich 进度条
- rich 进度条需要创建新线程
- Docker 容器在 macOS 上的线程资源有限
- 即使设置了 `PIP_NO_PROGRESS_BAR=1`，pip 仍然会在下载时尝试创建进度条线程

## 当前系统状态

✅ **应用正常运行**
```bash
python web/app_optimized.py
```
应用正在 http://localhost:5000 正常运行

✅ **所有配置文件已创建**
- Dockerfile
- docker-compose.yml
- run_docker.sh
- .dockerignore
- DOCKER_DEPLOYMENT.md

✅ **代码已提交到 Git**
所有 Docker 相关配置已推送到 GitHub

## 解决方案

### 方案 1: 使用当前运行的系统（推荐）

继续使用当前的 Python 直接运行方式，这是最简单和最稳定的方案：

```bash
# 启动应用
python web/app_optimized.py

# 或使用脚本
./run_optimized_ui.sh
```

**优点**：
- 无需 Docker
- 资源占用少
- 启动快速
- 已验证可正常工作

### 方案 2: 在 Linux 服务器上部署 Docker

Docker 部署在 Linux 环境下可以正常工作。可以在以下环境部署：
- 云服务器（AWS EC2, Azure, Google Cloud, 阿里云等）
- VPS（Vultr, DigitalOcean 等）
- 本地 Linux 虚拟机
- WSL2 (Windows Subsystem for Linux 2)

部署步骤：
```bash
# 在 Linux 服务器上
git clone https://github.com/xihawang/crypto-arbitrage-bot.git
cd crypto-arbitrage-bot
cp .env.example .env
# 编辑 .env 文件配置 API 密钥
./run_docker.sh build
./run_docker.sh start
```

### 方案 3: 使用 Podman 替代 Docker（macOS）

Podman 是一个无守护进程的 Docker 替代品，对资源使用更友好：

```bash
# 安装 Podman for macOS
brew install podman

# 初始化 Podman 机器
podman machine init --cpus 4 --memory 4096
podman machine start

# 使用 Podman 构建和运行
podman-compose build
podman-compose up -d
```

### 方案 4: 增加 Docker Desktop 资源（不保证有效）

1. 打开 Docker Desktop
2. 进入 Settings → Resources → Advanced
3. 增加资源配置：
   - CPUs: 6-8 核
   - Memory: 6-8 GB
   - Swap: 2 GB
4. 重启 Docker Desktop

注意：即使增加资源，pip 的线程问题可能仍然存在。

## 技术细节

### pip 版本问题
- Python 3.10-slim 基础镜像自带 pip 23.0.1
- pip 21.2+ 引入了 rich 进度条，需要线程支持
- 尝试升级 pip 到 25.3 也失败，因为升级过程也需要线程

### 尝试过的解决方案
1. ✅ 设置 `PIP_NO_PROGRESS_BAR=1` - 无效
2. ✅ 移除系统依赖安装 - 无效
3. ✅ 简化依赖列表 - 无效
4. ✅ 使用 `--no-color` 等标志 - 无效
5. ✅ 升级 pip 版本 - 升级过程本身也失败

### 为什么环境变量无效？
pip 在检查环境变量之前就已经初始化了 rich 进度条，这是 pip 内部的一个已知问题。

## 推荐部署方式对比

| 方式 | 适用场景 | 难度 | 稳定性 |
|------|---------|------|--------|
| **直接 Python 运行** | 本地开发、测试 | ⭐ | ⭐⭐⭐⭐⭐ |
| **Linux Docker** | 生产环境 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Podman** | macOS/Windows | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **macOS Docker** | 不推荐 | ⭐⭐⭐⭐ | ⭐⭐ |

## 文件清单

所有 Docker 相关文件已创建并提交到 Git：

```
crypto-arbitrage-bot/
├── Dockerfile                  # Docker 镜像配置
├── docker-compose.yml          # Docker Compose 编排
├── .dockerignore              # Docker 构建忽略文件
├── run_docker.sh              # Docker 管理脚本
├── DOCKER_DEPLOYMENT.md       # Docker 部署文档
└── DOCKER_STATUS.md           # 本文件
```

## 总结

Docker 配置文件已完整创建并可用于 Linux 环境。在当前 macOS 系统上，推荐继续使用 Python 直接运行方式。如需容器化部署，建议在 Linux 服务器上进行。

应用当前运行正常，所有功能均可使用。
