#!/bin/bash
# Web UI 启动脚本
# 用法: ./run_web_ui.sh

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║     加密货币套利机器人 - Web UI 仪表板                 ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 找不到 Python 3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 检查依赖..."
pip install -q flask flask-cors requests python-dotenv

# 获取本机 IP
IP_ADDRESS=$(ipconfig getifaddr en0 2>/dev/null || echo "localhost")

echo ""
echo "✅ 准备完毕"
echo ""
echo "📍 Web UI 访问地址:"
echo "   本地: http://localhost:5000"
echo "   网络: http://$IP_ADDRESS:5000"
echo ""
echo "🔌 API 端点:"
echo "   http://localhost:5000/api/status          - 系统状态"
echo "   http://localhost:5000/api/prices          - 实时价格"
echo "   http://localhost:5000/api/opportunities   - 套利机会"
echo "   http://localhost:5000/api/statistics      - 统计数据"
echo ""
echo "⚡ 启动 Web 服务器..."
echo "   按 Ctrl+C 停止服务器"
echo ""

# 启动 Flask 应用
cd /Users/longwang/crypto-arbitrage-bot
python3 -c "
import sys
sys.path.insert(0, '/Users/longwang/crypto-arbitrage-bot')
from web.app import main
main()
"
