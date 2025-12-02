"""
全能 Web UI - 展示所有套利机会
支持多种套利策略的实时监控和管理
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
from collections import deque, defaultdict

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.multi_source_price_fetcher import multi_source_price_fetcher
from src.notifications.alert_manager import alert_manager
from src.trading.auto_executor import auto_executor
from src.trading.trading_engine import trading_engine, TradingMode
from src.utils.logger import logger
from src.config import CRYPTOS, SCAN_INTERVAL, AUTO_TRADE_ENABLED, ALERT_ENABLED, EXCHANGES
import asyncio

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'crypto-arbitrage-secret-key-2024'
CORS(app)

# 初始化 SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# ============ 全局变量 ============

# 实时数据
latest_prices = {}
latest_opportunities = defaultdict(list)  # {strategy_name: [opportunities]}
price_history = {}  # 存储历史价格
scan_status = "idle"
last_update = None
connected_clients = 0

# 策略列表
STRATEGIES = [
    "spot_arbitrage",
    "triangle_arbitrage", 
    "stablecoin_arbitrage",
    "dex_arbitrage",
    "cross_chain_arbitrage",
    "flash_loan_arbitrage",
    "options_arbitrage",
    "futures_arbitrage"
]

# 初始化历史数据存储
for crypto in CRYPTOS:
    price_history[crypto] = deque(maxlen=100)

# 初始化机器人
manager = None

def init_system():
    """初始化系统组件"""
    global manager
    try:
        # 不再使用旧的UnifiedArbitrageManager
        manager = None
        logger.info("✅ 系统初始化成功 - 使用多数据源API价格获取器")
        return True
    except Exception as e:
        logger.error(f"❌ 系统初始化失败: {str(e)}")
        return False


# ============ 实时价格数据收集 ============

def collect_prices():
    """后台收集实时价格"""
    global latest_prices, last_update

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            logger.info("📊 正在收集实时价格...")

            # 获取所有价格数据
            prices_data = multi_source_price_fetcher.fetch_all_prices(CRYPTOS)

            # 更新 latest_prices
            latest_prices = {}
            for crypto in CRYPTOS:
                if crypto in prices_data and prices_data[crypto]:
                    latest_prices[crypto] = prices_data[crypto]  # 直接存储价格数据

                    # 保存到历史记录（使用平均价格）
                    if prices_data[crypto]:
                        avg_price = sum(prices_data[crypto].values()) / len(prices_data[crypto])
                        price_history[crypto].append({
                            "timestamp": datetime.now().isoformat(),
                            "price": avg_price
                        })

            last_update = datetime.now().isoformat()

            # 广播更新给所有连接的客户端
            socketio.emit('price_update', {
                'prices': latest_prices,
                'timestamp': last_update
            }, to='*')
            
            logger.info(f"✅ 价格更新完成，已发送给 {connected_clients} 个客户端")
            
            # 每 30 秒更新一次
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ 价格收集错误: {str(e)}")
            time.sleep(30)


# ============ 套利机会扫描 ============

def scan_opportunities():
    """后台扫描套利机会"""
    global scan_status, latest_opportunities, latest_prices

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            scan_status = "scanning"
            logger.info("🔍 开始扫描套利机会...")

            # 获取最新价格并分析机会
            if latest_prices:
                opportunities = multi_source_price_fetcher.get_all_opportunities(CRYPTOS, latest_prices)

                if opportunities:
                    latest_opportunities["spot_arbitrage"] = opportunities
                    logger.info(f"✅ 现货套利: 发现 {len(opportunities)} 个机会")

                    # 发送告警
                    if ALERT_ENABLED and opportunities:
                        for opportunity in opportunities[:3]:  # 只发送前3个最佳机会
                            loop.run_until_complete(alert_manager.send_arbitrage_alert(opportunity))

                # 广播更新
                socketio.emit('opportunities_update', {
                    'opportunities': dict(latest_opportunities),
                    'timestamp': datetime.now().isoformat()
                }, to='*')

            scan_status = "idle"
            logger.info(f"✅ 扫描完成，已发送给 {connected_clients} 个客户端")

            # 每 30 秒扫描一次
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ 套利机会扫描错误: {str(e)}")
            scan_status = "error"
            time.sleep(60)


# ============ Flask 路由 ============

@app.route('/')
def index():
    """主页"""
    return render_template('index_all_arbitrage.html')


@app.route('/api/prices')
def get_prices():
    """获取实时价格 API"""
    return jsonify({
        'prices': latest_prices,
        'timestamp': last_update
    })


@app.route('/api/opportunities')
def get_opportunities():
    """获取所有套利机会 API"""
    return jsonify({
        'opportunities': dict(latest_opportunities),
        'status': scan_status,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/opportunities/<strategy>')
def get_strategy_opportunities(strategy):
    """获取特定策略的套利机会"""
    if strategy in latest_opportunities:
        return jsonify({
            'strategy': strategy,
            'opportunities': latest_opportunities[strategy],
            'count': len(latest_opportunities[strategy]),
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({'error': f'策略 {strategy} 未找到'}), 404


@app.route('/api/price-history/<crypto>')
def get_price_history(crypto):
    """获取价格历史"""
    if crypto in price_history:
        return jsonify({
            'crypto': crypto,
            'history': list(price_history[crypto]),
            'count': len(price_history[crypto])
        })
    else:
        return jsonify({'error': f'加密货币 {crypto} 未找到'}), 404


@app.route('/api/price-trend/<crypto>')
def get_price_trend(crypto):
    """获取价格趋势分析"""
    if crypto in CRYPTOS:
        try:
            trend = live_market_price_fetcher.get_price_trend(crypto, 60)  # 60分钟趋势
            return jsonify(trend)
        except Exception as e:
            return jsonify({'error': f'获取趋势失败: {str(e)}'}), 500
    else:
        return jsonify({'error': f'加密货币 {crypto} 未找到'}), 404


@app.route('/api/market-overview')
def get_market_overview():
    """获取市场总览"""
    overview = {
        'data_source': 'multi_source_api',
        'description': '多数据源API市场价格数据 (Binance, Coinbase, CryptoCompare, CoinGecko)',
        'last_update': last_update,
        'market_baselines': {
            'BTC': '~$102,500',
            'ETH': '~$3,850',
            'SOL': '~$248',
            'USDT': '~$1.001',
            'USDC': '~$1.000'
        },
        'supported_exchanges': [
            {'name': 'Binance', 'region': 'Global'},
            {'name': 'Coinbase', 'region': 'US/Europe'},
            {'name': 'OKX', 'region': 'Asia'},
            {'name': 'Bybit', 'region': 'Global'},
            {'name': 'Bitget', 'region': 'Asia'},
            {'name': 'Kraken', 'region': 'US/Europe'}
        ],
        'features': [
            '实时价格更新',
            '多交易所套利检测',
            '趋势分析',
            '智能告警',
            '自动交易模拟'
        ]
    }
    return jsonify(overview)


@app.route('/api/stats')
def get_stats():
    """获取统计数据"""
    total_opportunities = sum(len(opps) for opps in latest_opportunities.values())

    stats = {
        'total_opportunities': total_opportunities,
        'strategies_count': len(STRATEGIES),
        'cryptos_count': len(CRYPTOS),
        'connected_clients': connected_clients,
        'scan_status': scan_status,
        'last_update': last_update,
        'data_source': 'multi_source_api',
        'market_data_description': '多数据源API市场价格数据 (Binance, Coinbase, CryptoCompare, CoinGecko)',
        'opportunities_by_strategy': {
            strategy: len(latest_opportunities.get(strategy, []))
            for strategy in STRATEGIES
        }
    }

    return jsonify(stats)


@app.route('/api/strategy/<strategy>')
def get_strategy_info(strategy):
    """获取策略信息"""
    strategy_info = {
        'spot_arbitrage': {
            'name': '现货套利',
            'description': '在不同交易所的价格差异中获利',
            'risk': '低',
            'frequency': '高',
            'min_profit_rate': 0.2
        },
        'triangle_arbitrage': {
            'name': '三角套利',
            'description': '利用三个交易对的价格不一致',
            'risk': '中',
            'frequency': '中',
            'min_profit_rate': 0.5
        },
        'stablecoin_arbitrage': {
            'name': '稳定币套利',
            'description': '利用稳定币之间的汇率差异',
            'risk': '低',
            'frequency': '中',
            'min_profit_rate': 0.1
        },
        'dex_arbitrage': {
            'name': 'DEX 套利',
            'description': '在去中心化交易所间套利',
            'risk': '中',
            'frequency': '低',
            'min_profit_rate': 0.5
        },
        'cross_chain_arbitrage': {
            'name': '跨链套利',
            'description': '利用不同区块链间的价格差异',
            'risk': '中',
            'frequency': '低',
            'min_profit_rate': 1.0
        },
        'flash_loan_arbitrage': {
            'name': '闪电贷套利',
            'description': '使用闪电贷进行无本套利',
            'risk': '高',
            'frequency': '低',
            'min_profit_rate': 0.3
        },
        'options_arbitrage': {
            'name': '期权套利',
            'description': '利用期权市场的定价差异',
            'risk': '高',
            'frequency': '低',
            'min_profit_rate': 1.0
        },
        'futures_arbitrage': {
            'name': '期货套利',
            'description': '现货-期货价差套利',
            'risk': '中',
            'frequency': '高',
            'min_profit_rate': 0.2
        }
    }

    if strategy in strategy_info:
        return jsonify(strategy_info[strategy])
    else:
        return jsonify({'error': f'策略 {strategy} 未找到'}), 404


# ============ 交易执行相关API ============

@app.route('/api/trading/execute', methods=['POST'])
def execute_arbitrage():
    """执行套利交易"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据为空'}), 400

        opportunity_id = data.get('opportunity_id')
        opportunity_data = data.get('opportunity_data')

        if not opportunity_data:
            return jsonify({'error': '缺少套利机会数据'}), 400

        # 异步执行交易
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        execution = loop.run_until_complete(trading_engine.execute_arbitrage(opportunity_data))

        logger.info(f"🎯 套利交易执行请求: {opportunity_id} - 状态: {execution.status}")

        # 广播执行结果
        socketio.emit('trade_execution', {
            'execution': execution.to_dict(),
            'timestamp': datetime.now().isoformat()
        }, to='*')

        return jsonify({
            'success': True,
            'execution': execution.to_dict(),
            'message': f'套利交易{execution.status}'
        })

    except Exception as e:
        logger.error(f"❌ 执行套利交易失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/trading/orders')
def get_active_orders():
    """获取活跃订单"""
    try:
        orders = trading_engine.get_active_orders()
        return jsonify({
            'orders': orders,
            'count': len(orders),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ 获取活跃订单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/history')
def get_trading_history():
    """获取交易历史"""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 200)  # 最大限制200条

        history = trading_engine.get_execution_history(limit)

        return jsonify({
            'history': history,
            'count': len(history),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ 获取交易历史失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/statistics')
def get_trading_statistics():
    """获取交易统计"""
    try:
        stats = trading_engine.get_profit_statistics()

        # 获取最近7天的统计数据
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_executions = [
            e for e in trading_engine.execution_history
            if e.created_at >= seven_days_ago
        ]

        # 按币种统计
        crypto_stats = {}
        for execution in recent_executions:
            crypto = execution.crypto
            if crypto not in crypto_stats:
                crypto_stats[crypto] = {
                    'count': 0,
                    'total_profit': 0,
                    'avg_profit': 0,
                    'success_count': 0
                }

            crypto_stats[crypto]['count'] += 1
            crypto_stats[crypto]['total_profit'] += execution.actual_profit
            if execution.actual_profit > 0:
                crypto_stats[crypto]['success_count'] += 1

        # 计算平均值
        for crypto, data in crypto_stats.items():
            if data['count'] > 0:
                data['avg_profit'] = data['total_profit'] / data['count']
                data['success_rate'] = data['success_count'] / data['count']

        return jsonify({
            'overall_stats': stats,
            'recent_7days': {
                'total_executions': len(recent_executions),
                'crypto_breakdown': crypto_stats
            },
            'trading_mode': trading_engine.mode.value,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ 获取交易统计失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/cancel-order', methods=['POST'])
def cancel_order():
    """取消订单"""
    try:
        data = request.get_json()
        if not data or 'order_id' not in data:
            return jsonify({'error': '缺少订单ID'}), 400

        order_id = data['order_id']
        success = trading_engine.cancel_order(order_id)

        if success:
            logger.info(f"❌ 订单取消成功: {order_id}")
            socketio.emit('order_cancelled', {
                'order_id': order_id,
                'timestamp': datetime.now().isoformat()
            }, to='*')

            return jsonify({
                'success': True,
                'message': '订单已取消'
            })
        else:
            return jsonify({
                'success': False,
                'error': '订单不存在或无法取消'
            }), 404

    except Exception as e:
        logger.error(f"❌ 取消订单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/mode', methods=['POST'])
def set_trading_mode():
    """设置交易模式"""
    try:
        data = request.get_json()
        if not data or 'mode' not in data:
            return jsonify({'error': '缺少交易模式'}), 400

        mode_str = data['mode']

        # 验证模式
        valid_modes = ['live', 'simulation', 'dry_run']
        if mode_str not in valid_modes:
            return jsonify({
                'error': f'无效的交易模式，支持: {", ".join(valid_modes)}'
            }), 400

        # 映射到枚举
        mode_mapping = {
            'live': TradingMode.LIVE,
            'simulation': TradingMode.SIMULATION,
            'dry_run': TradingMode.DRY_RUN
        }

        trading_engine.set_mode(mode_mapping[mode_str])

        logger.info(f"🔄 交易模式已切换为: {mode_str}")

        return jsonify({
            'success': True,
            'mode': mode_str,
            'message': f'交易模式已切换为: {mode_str}'
        })

    except Exception as e:
        logger.error(f"❌ 设置交易模式失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/mode')
def get_trading_mode():
    """获取当前交易模式"""
    return jsonify({
        'mode': trading_engine.mode.value,
        'description': {
            'live': '实盘交易 - 使用真实资金进行交易',
            'simulation': '模拟交易 - 模拟交易执行过程',
            'dry_run': '试运行 - 仅验证交易逻辑，不实际执行'
        }.get(trading_engine.mode.value, ''),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/manual-scan', methods=['POST'])
def manual_scan():
    """手动触发一次扫描"""
    if manager:
        threading.Thread(target=lambda: manager.scan_all_opportunities()).start()
        return jsonify({'status': 'scanning', 'message': '已启动手动扫描'})
    else:
        return jsonify({'error': '管理器未初始化'}), 500


# ============ WebSocket 事件 ============

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    global connected_clients
    connected_clients += 1
    logger.info(f"✅ 客户端已连接 (总计: {connected_clients})")
    
    emit('connection_response', {
        'data': '已连接到套利监控系统',
        'status': 'connected'
    })


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    global connected_clients
    connected_clients -= 1
    logger.info(f"❌ 客户端已断开连接 (总计: {connected_clients})")


@socketio.on('request_prices')
def handle_price_request():
    """客户端请求价格数据"""
    emit('price_data', {
        'prices': latest_prices,
        'timestamp': datetime.now().isoformat()
    })


@socketio.on('request_opportunities')
def handle_opportunities_request():
    """客户端请求套利机会"""
    emit('opportunities_data', {
        'opportunities': dict(latest_opportunities),
        'timestamp': datetime.now().isoformat()
    })


@socketio.on('request_strategy_details')
def handle_strategy_details(data):
    """客户端请求策略详情"""
    strategy = data.get('strategy')
    emit('strategy_details', {
        'strategy': strategy,
        'opportunities': latest_opportunities.get(strategy, []),
        'count': len(latest_opportunities.get(strategy, []))
    })


# ============ 启动函数 ============

def start_background_tasks():
    """启动后台任务"""
    logger.info("🚀 启动后台任务线程...")
    
    # 价格收集线程
    price_thread = threading.Thread(target=collect_prices, daemon=True)
    price_thread.start()
    logger.info("✅ 价格收集线程已启动")
    
    # 机会扫描线程
    scan_thread = threading.Thread(target=scan_opportunities, daemon=True)
    scan_thread.start()
    logger.info("✅ 机会扫描线程已启动")


def main():
    """主函数"""
    logger.info("="*60)
    logger.info("🤖 启动全能 Web UI 仪表板 - 真实实时价格版")
    logger.info("💰 数据来源: 多数据源API (Binance, Coinbase, CryptoCompare, CoinGecko)")
    logger.info("="*60)
    
    # 初始化管理器
    if not init_system():
        logger.warning("⚠️  管理器初始化失败，部分功能不可用")
    
    # 启动后台任务
    start_background_tasks()
    
    # 启动 Web 服务
    logger.info("\n")
    logger.info("📡 Web 服务启动参数:")
    logger.info(f"  地址: http://localhost:5000")
    logger.info(f"  调试模式: OFF")
    logger.info(f"  WebSocket: 启用")
    logger.info("\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()
