#!/bin/bash

# 优化版Web UI启动脚本
# 使用生产级配置和更好的错误处理

set -e

echo "🚀 启动优化版加密货币套利机器人 Web UI..."
echo "================================================"
echo "✅ Python 版本: $(python --version)"

# 检查依赖
echo "📦 检查依赖..."
python -c "import flask, flask_socketio, requests; print('✅ 核心依赖已安装')" || {
    echo "❌ 缺少必要依赖，正在安装..."
    pip install flask flask-socketio requests python-dotenv
}

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export FLASK_ENV=production
export FLASK_DEBUG=0

echo "🌐 启动优化版 Web 服务..."
echo "================================================"
echo "💻 访问地址: http://localhost:5000"
echo "🔄 自动刷新间隔: 30-60 秒 (优化)"
echo "🎯 支持 8 种套利策略实时监控"
echo "📊 多数据源API (Binance, Coinbase, CryptoCompare, CoinGecko)"
echo "⚡ 智能缓存和错误处理"
echo "================================================"

echo "📁 脚本目录: $(dirname "$0")"
echo "📁 当前工作目录: $(pwd)"
echo "Python path: ${PYTHONPATH}"

# 检查Web模块是否可导入
python -c "from web.app_all_arbitrage import app; print('✅ Web module imported successfully')" || {
    echo "❌ 无法导入Web模块"
    exit 1
}

# 启动服务
echo
echo "📡 Web 服务启动参数:"
echo "  地址: http://localhost:5000"
echo "  调试模式: OFF (生产优化)"
echo "  WebSocket: 启用"
echo "  多进程: 支持"
echo "  数据源: 多数据源API"
echo "  缓存: 5分钟"
echo "  错误处理: 智能降级"
echo

# 使用Waitress作为生产服务器
if command -v waitress-serve &> /dev/null; then
    echo "🔧 使用Waitress生产服务器..."
    waitress-serve --host=0.0.0.0 --port=5000 --threads=4 web.app_all_arbitrage:app
else
    echo "⚠️  Waitress未安装，使用Flask开发服务器..."
    echo "📦 建议安装: pip install waitress"
    python -m flask run --host=0.0.0.0 --port=5000 --no-debug
fi