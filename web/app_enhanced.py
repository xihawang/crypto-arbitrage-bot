"""
增强版 Web UI - 包含 WebSocket 实时推送、历史数据、Telegram 通知等
访问地址: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import threading
import time
import sys
import os
from collections import deque
import sqlite3

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.price_fetcher import price_fetcher
from src.utils.logger import logger
from src.config import CRYPTOS

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)

# 初始化 SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# ============ 全局变量 ============

latest_prices = {}
latest_opportunities = []
price_history = {}  # 存储历史价格
scan_status = "idle"
last_update = None
connected_clients = 0

# 初始化历史数据存储 (每个币种保留最近100条记录)
for crypto in CRYPTOS:
    price_history[crypto] = deque(maxlen=100)


# ============ 数据库操作 ============

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('arbitrage_bot.db')
    c = conn.cursor()
    
    # 创建价格历史表
    c.execute('''CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY,
        crypto TEXT,
        exchange TEXT,
        price REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建套利机会表
    c.execute('''CREATE TABLE IF NOT EXISTS opportunities (
        id INTEGER PRIMARY KEY,
        crypto TEXT,
        buy_exchange TEXT,
        sell_exchange TEXT,
        buy_price REAL,
        sell_price REAL,
        diff_rate REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建交易记录表
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY,
        crypto TEXT,
        amount REAL,
        buy_exchange TEXT,
        sell_exchange TEXT,
        profit REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()


def save_price_to_db(crypto, exchange, price):
    """保存价格到数据库"""
    try:
        conn = sqlite3.connect('arbitrage_bot.db')
        c = conn.cursor()
        c.execute('INSERT INTO price_history (crypto, exchange, price) VALUES (?, ?, ?)',
                  (crypto, exchange, price))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"❌ 保存价格失败: {str(e)}")


def save_opportunity_to_db(opportunity):
    """保存套利机会到数据库"""
    try:
        conn = sqlite3.connect('arbitrage_bot.db')
        c = conn.cursor()
        c.execute('''INSERT INTO opportunities 
                     (crypto, buy_exchange, sell_exchange, buy_price, sell_price, diff_rate, status) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (opportunity['crypto'], 
                   opportunity['buy_exchange'],
                   opportunity['sell_exchange'],
                   opportunity['buy_price'],
                   opportunity['sell_price'],
                   opportunity['diff_rate'],
                   'detected'))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"❌ 保存机会失败: {str(e)}")


# ============ 后台扫描线程 ============

def background_price_scanner():
    """后台线程：持续扫描价格和套利机会"""
    global latest_prices, latest_opportunities, last_update, scan_status
    
    init_db()  # 初始化数据库
    
    while True:
        try:
            scan_status = "scanning"
            
            # 获取所有价格
            latest_prices = price_fetcher.get_all_prices(CRYPTOS)
            
            # 保存价格历史并推送
            for crypto, exchanges_data in latest_prices.items():
                for exchange, price_data in exchanges_data.items():
                    if "price" in price_data:
                        price = price_data["price"]
                        # 保存到内存历史
                        price_history[crypto].append({
                            "exchange": exchange,
                            "price": price,
                            "timestamp": datetime.now().isoformat()
                        })
                        # 保存到数据库
                        save_price_to_db(crypto, exchange, price)
            
            # 分析套利机会
            opportunities = []
            for crypto in CRYPTOS:
                analysis = price_fetcher.analyze_price_diff(crypto)
                if analysis.get("arbitrage_possible"):
                    opp = {
                        "crypto": crypto,
                        "diff_rate": analysis.get("diff_rate"),
                        "buy_exchange": analysis.get("min_exchange"),
                        "buy_price": analysis.get("min_price"),
                        "sell_exchange": analysis.get("max_exchange"),
                        "sell_price": analysis.get("max_price"),
                        "timestamp": datetime.now().isoformat()
                    }
                    opportunities.append(opp)
                    save_opportunity_to_db(opp)
            
            latest_opportunities = opportunities
            last_update = datetime.now().isoformat()
            scan_status = "idle"
            
            # 通过 WebSocket 推送数据给所有连接的客户端
            socketio.emit('price_update', {
                'prices': latest_prices,
                'opportunities': opportunities,
                'timestamp': last_update,
                'opportunities_count': len(opportunities)
            }, broadcast=True)
            
            logger.info(f"✅ 扫描完成 - 发现 {len(opportunities)} 个套利机会")
            
            time.sleep(30)  # 每 30 秒扫描一次 (可自定义)
            
        except Exception as e:
            logger.error(f"❌ 后台扫描错误: {str(e)}")
            scan_status = "error"
            time.sleep(10)


# ============ WebSocket 事件处理 ============

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    global connected_clients
    connected_clients += 1
    logger.info(f"👤 客户端连接 (共 {connected_clients} 个连接)")
    
    # 发送初始数据
    emit('connected', {
        'status': 'connected',
        'clients': connected_clients,
        'timestamp': datetime.now().isoformat()
    })


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    global connected_clients
    connected_clients -= 1
    logger.info(f"👤 客户端断开连接 (共 {connected_clients} 个连接)")


@socketio.on('subscribe_prices')
def handle_subscribe_prices():
    """订阅实时价格"""
    emit('price_update', {
        'prices': latest_prices,
        'opportunities': latest_opportunities,
        'timestamp': last_update
    })


@socketio.on('request_price_history')
def handle_price_history(data):
    """请求价格历史数据"""
    crypto = data.get('crypto')
    if crypto in price_history:
        emit('price_history', {
            'crypto': crypto,
            'history': list(price_history[crypto])
        })


# ============ REST API 路由 ============

@app.route('/')
def index():
    """主页"""
    return render_template('index_enhanced.html')


@app.route('/api/v2/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    return jsonify({
        "status": "running",
        "scan_status": scan_status,
        "last_update": last_update,
        "opportunities_count": len(latest_opportunities),
        "cryptos_tracked": len(CRYPTOS),
        "connected_clients": connected_clients
    })


@app.route('/api/v2/prices', methods=['GET'])
def get_prices():
    """获取所有加密货币的价格"""
    crypto = request.args.get('crypto')
    
    if crypto:
        if crypto in latest_prices:
            return jsonify({
                "crypto": crypto,
                "prices": latest_prices[crypto],
                "timestamp": last_update
            })
        else:
            return jsonify({"error": "币种不存在"}), 404
    else:
        return jsonify({
            "prices": latest_prices,
            "timestamp": last_update,
            "count": len(latest_prices)
        })


@app.route('/api/v2/price-history/<crypto>', methods=['GET'])
def get_price_history(crypto):
    """获取价格历史"""
    limit = request.args.get('limit', default=50, type=int)
    
    if crypto in price_history:
        history = list(price_history[crypto])[-limit:]
        return jsonify({
            "crypto": crypto,
            "history": history,
            "count": len(history)
        })
    else:
        return jsonify({"error": "币种不存在"}), 404


@app.route('/api/v2/opportunities', methods=['GET'])
def get_opportunities():
    """获取所有套利机会"""
    sorted_opps = sorted(latest_opportunities, key=lambda x: x['diff_rate'], reverse=True)
    
    return jsonify({
        "opportunities": sorted_opps,
        "count": len(sorted_opps),
        "timestamp": last_update
    })


@app.route('/api/v2/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    if not latest_opportunities:
        return jsonify({
            "total_opportunities": 0,
            "total_cryptos": len(CRYPTOS),
            "avg_diff_rate": 0,
            "max_diff_rate": 0,
            "scan_status": scan_status
        })
    
    diff_rates = [opp['diff_rate'] for opp in latest_opportunities]
    
    return jsonify({
        "total_opportunities": len(latest_opportunities),
        "total_cryptos": len(CRYPTOS),
        "avg_diff_rate": round(sum(diff_rates) / len(diff_rates), 4) if diff_rates else 0,
        "max_diff_rate": round(max(diff_rates), 4) if diff_rates else 0,
        "min_diff_rate": round(min(diff_rates), 4) if diff_rates else 0,
        "last_scan": last_update,
        "scan_status": scan_status
    })


@app.route('/api/v2/analytics/top-opportunities', methods=['GET'])
def get_top_opportunities():
    """获取top N 套利机会"""
    n = request.args.get('n', default=10, type=int)
    sorted_opps = sorted(latest_opportunities, key=lambda x: x['diff_rate'], reverse=True)
    return jsonify({
        "top_opportunities": sorted_opps[:n],
        "count": len(sorted_opps[:n])
    })


@app.route('/api/v2/analytics/price-range/<crypto>', methods=['GET'])
def get_price_range(crypto):
    """获取币种的价格范围"""
    if crypto not in price_history or len(price_history[crypto]) == 0:
        return jsonify({"error": "无数据"}), 404
    
    history = list(price_history[crypto])
    prices = [h['price'] for h in history]
    
    return jsonify({
        "crypto": crypto,
        "max": max(prices),
        "min": min(prices),
        "avg": sum(prices) / len(prices),
        "latest": prices[-1] if prices else 0,
        "data_points": len(prices)
    })


@app.route('/api/v2/refresh', methods=['POST'])
def refresh_data():
    """手动刷新数据"""
    global latest_prices, latest_opportunities, last_update, scan_status
    
    try:
        scan_status = "scanning"
        
        latest_prices = price_fetcher.get_all_prices(CRYPTOS)
        
        opportunities = []
        for crypto in CRYPTOS:
            analysis = price_fetcher.analyze_price_diff(crypto)
            if analysis.get("arbitrage_possible"):
                opportunities.append({
                    "crypto": crypto,
                    "diff_rate": analysis.get("diff_rate"),
                    "buy_exchange": analysis.get("min_exchange"),
                    "buy_price": analysis.get("min_price"),
                    "sell_exchange": analysis.get("max_exchange"),
                    "sell_price": analysis.get("max_price"),
                    "timestamp": datetime.now().isoformat()
                })
        
        latest_opportunities = opportunities
        last_update = datetime.now().isoformat()
        scan_status = "idle"
        
        # 推送更新到所有连接的客户端
        socketio.emit('price_update', {
            'prices': latest_prices,
            'opportunities': opportunities,
            'timestamp': last_update
        }, broadcast=True)
        
        return jsonify({
            "status": "success",
            "message": f"✅ 刷新完成，发现 {len(opportunities)} 个套利机会",
            "timestamp": last_update
        })
    except Exception as e:
        scan_status = "error"
        return jsonify({
            "status": "error",
            "message": f"❌ 刷新失败: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({"error": "Internal server error"}), 500


def main():
    """启动 Web 服务器"""
    print(f"\n{'='*60}")
    print("🚀 启动增强版 Web UI 仪表板 (v2.0)")
    print(f"{'='*60}")
    print("\n📍 访问地址: http://localhost:5000")
    print("📊 API 文档: http://localhost:5000/api/v2")
    print("\n✨ 新增功能:")
    print("  ⚡ WebSocket 实时推送 (30秒更新)")
    print("  📈 历史数据追踪")
    print("  💾 数据库存储")
    print("  📊 统计分析")
    print("  🔔 实时通知")
    print("  📱 移动端适配")
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 启动后台价格扫描线程
    scanner_thread = threading.Thread(target=background_price_scanner, daemon=True)
    scanner_thread.start()
    
    # 启动 SocketIO 服务器
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)


if __name__ == '__main__':
    main()
