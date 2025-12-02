#!/bin/bash

# 全能 Web UI 启动脚本
# 支持展示所有 8 种套利机会的实时仪表板

set -e

echo "🚀 启动全能套利机器人 Web UI..."
echo "================================================"

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"

# 检查依赖
echo ""
echo "📦 检查依赖..."
python3 -c "import flask" 2>/dev/null || (echo "❌ 缺少 Flask，正在安装..." && pip3 install flask flask-socketio flask-cors)
python3 -c "import socketio" 2>/dev/null || (echo "❌ 缺少 socketio，正在安装..." && pip3 install python-socketio)

# 启动应用
echo ""
echo "🌐 启动 Web 服务..."
echo ""
echo "=========================================="
echo "💻 访问地址: http://localhost:5000"
echo "🔄 自动刷新间隔: 10-20 秒"
echo "🎯 支持 8 种套利策略实时监控"
echo "📊 支持 WebSocket 实时推送"
echo "=========================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 脚本目录: $SCRIPT_DIR"

# 切换到项目根目录
cd "$SCRIPT_DIR"
echo "📁 当前工作目录: $(pwd)"

# 使用增强版 app
python3 -c "
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.getcwd())

print(f'Python path: {sys.path[0]}')

try:
    # 测试 web 模块导入
    import web
    print('✅ Web module imported successfully')

    # 导入并启动应用
    from web.app_all_arbitrage import main
    main()
except ImportError as e:
    print(f'❌ Import error: {e}')
    print(f'Available directories: {os.listdir(os.getcwd())}')
    sys.exit(1)
" "$@"
