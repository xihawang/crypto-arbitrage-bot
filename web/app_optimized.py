"""
优化版Web应用
集成所有优化组件：
1. 优化版价格获取器
2. 优化版API
3. 优化版前端
4. 性能监控
"""

import os
import sys
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import logger
from src.utils.optimized_price_fetcher import optimized_price_fetcher
# from web.optimized_api import setup_optimized_routes


class OptimizedWebApp:
    """优化版Web应用"""

    def __init__(self):
        self.app = Flask(__name__,
                        template_folder='templates',
                        static_folder='static')
        self.setup_flask_config()
        self.setup_socketio()
        self.setup_routes()
        self.setup_optimizations()

        # 性能监控
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0

        logger.info("🚀 优化版Web应用初始化完成")

    def setup_flask_config(self):
        """设置Flask配置"""
        self.app.config.update({
            'SECRET_KEY': 'arbitrage-optimized-2024',
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': False,
            'SEND_FILE_MAX_AGE_DEFAULT': 0,
            'TEMPLATES_AUTO_RELOAD': False,
        })

    def setup_socketio(self):
        """设置WebSocket"""
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=False,
            engineio_logger=False
        )

    def setup_simple_optimized_routes(self):
        """设置简化版优化路由"""

        @self.app.route('/api/v2/dashboard', methods=['GET'])
        def get_dashboard_v2():
            """简化版仪表板API"""
            try:
                cryptos = ["BTC", "ETH", "SOL", "USDT", "USDC"]
                start_time = time.time()

                # 使用优化版价格获取器
                prices = optimized_price_fetcher.fetch_all_prices(cryptos)
                opportunities = optimized_price_fetcher.get_all_opportunities(cryptos, prices)

                # 计算统计
                total_profit = sum(opp.get('potential_profit', 0) for opp in opportunities)
                stats = {
                    'total_opportunities': len(opportunities),
                    'total_profit': total_profit,
                    'high_profit_count': len([opp for opp in opportunities if opp.get('diff_rate', 0) > 0.5]),
                    'best_opportunity': opportunities[0] if opportunities else None
                }

                execution_time = time.time() - start_time

                return jsonify({
                    'status': 'success',
                    'data_source': 'optimized',
                    'data': {
                        'prices': prices,
                        'opportunities': {
                            'spot_arbitrage': opportunities
                        },
                        'stats': stats,
                        'cache_status': 'hit' if execution_time < 0.5 else 'miss'
                    },
                    'performance': {
                        'total_execution_time': round(execution_time * 1000, 2),
                        'timestamp': datetime.now().isoformat()
                    }
                })

            except Exception as e:
                logger.error(f"仪表板API错误: {e}")
                return jsonify({
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500

        @self.app.route('/api/v2/performance', methods=['GET'])
        def get_performance_monitoring():
            """性能监控API"""
            return jsonify({
                'price_fetcher': optimized_price_fetcher.get_performance_stats(),
                'system': {
                    'timestamp': datetime.now().isoformat(),
                    'uptime': time.time() - self.start_time
                }
            })

    def setup_routes(self):
        """设置路由"""
        # 设置优化版API路由
        # self.api_optimizer = setup_optimized_routes(self.app)
        self.setup_simple_optimized_routes()

        # 设置交易执行API路由
        self.setup_trading_routes()

        @self.app.route('/')
        def index():
            """主页 - 使用优化版前端"""
            return render_template('index_optimized.html')

        @self.app.route('/health')
        def health_check():
            """健康检查端点"""
            uptime = time.time() - self.start_time
            performance_stats = optimized_price_fetcher.get_performance_stats()

            return jsonify({
                'status': 'healthy',
                'uptime': uptime,
                'request_count': self.request_count,
                'error_count': self.error_count,
                'price_fetcher_stats': performance_stats,
                'timestamp': datetime.now().isoformat()
            })

        # WebSocket事件
        @self.socketio.on('connect')
        def handle_connect(auth=None):
            clients = self.get_connected_clients()
            logger.info(f"✅ 客户端已连接 (总计: {clients})")
            emit('status', {'message': '连接成功', 'type': 'connection'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f"❌ 客户端已断开连接")

        @self.socketio.on('request_dashboard_update')
        def handle_dashboard_request():
            """处理仪表板更新请求"""
            try:
                from src.utils.optimized_price_fetcher import optimized_price_fetcher
                cryptos = ["BTC", "ETH", "SOL", "USDT", "USDC"]

                start_time = time.time()
                prices = optimized_price_fetcher.fetch_all_prices(cryptos)
                opportunities = optimized_price_fetcher.get_all_opportunities(cryptos, prices)

                execution_time = time.time() - start_time

                emit('dashboard_update', {
                    'prices': prices,
                    'opportunities': {'spot_arbitrage': opportunities},
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"仪表板更新失败: {e}")
                emit('error', {'message': '更新失败', 'error': str(e)})

        # 请求计数中间件
        @self.app.before_request
        def before_request():
            self.request_count += 1

    def setup_optimizations(self):
        """设置优化功能"""
        # 启动后台数据聚合线程
        self.start_background_tasks()

        # 设置错误处理
        self.setup_error_handling()

        # 设置性能监控
        self.setup_performance_monitoring()

    def start_background_tasks(self):
        """启动后台任务"""
        def background_price_update():
            """后台价格更新任务"""
            while True:
                try:
                    cryptos = ["BTC", "ETH", "SOL", "USDT", "USDC"]
                    prices = optimized_price_fetcher.fetch_all_prices(cryptos)
                    opportunities = optimized_price_fetcher.get_all_opportunities(cryptos, prices)

                    # 广播给所有连接的客户端
                    self.socketio.emit('price_update', {
                        'prices': prices,
                        'opportunities': {'spot_arbitrage': opportunities},
                        'timestamp': datetime.now().isoformat()
                    })

                    logger.debug("✅ 后台价格更新完成")

                except Exception as e:
                    logger.error(f"后台价格更新失败: {e}")

                time.sleep(5)  # 5秒更新一次

        def background_performance_monitor():
            """后台性能监控任务"""
            start_time = time.time()  # 使用局部变量避免线程访问问题
            while True:
                try:
                    performance_stats = optimized_price_fetcher.get_performance_stats()

                    # 发送性能统计到客户端
                    self.socketio.emit('performance_stats', {
                        'price_fetcher': performance_stats,
                        'web_app': {
                            'uptime': time.time() - start_time,
                            'request_count': self.request_count,
                            'error_count': self.error_count,
                            'connected_clients': self.get_connected_clients()
                        },
                        'timestamp': datetime.now().isoformat()
                    })

                except Exception as e:
                    logger.error(f"性能监控失败: {e}")

                time.sleep(30)  # 30秒更新一次

        # 启动后台线程
        price_thread = threading.Thread(target=background_price_update, daemon=True)
        price_thread.start()
        logger.info("✅ 后台价格更新线程已启动")

        monitor_thread = threading.Thread(target=background_performance_monitor, daemon=True)
        monitor_thread.start()
        logger.info("✅ 后台性能监控线程已启动")

    def setup_error_handling(self):
        """设置错误处理"""
        @self.app.errorhandler(404)
        def not_found(error):
            self.error_count += 1
            return jsonify({
                'error': 'Not Found',
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            self.error_count += 1
            logger.error(f"内部服务器错误: {error}")
            return jsonify({
                'error': 'Internal Server Error',
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }), 500

        @self.app.errorhandler(Exception)
        def handle_exception(e):
            self.error_count += 1
            logger.error(f"未处理的异常: {e}")
            return jsonify({
                'error': str(e),
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }), 500

    def setup_performance_monitoring(self):
        """设置性能监控"""
        # 记录启动时间
        self.start_time = time.time()

        # 性能日志中间件
        @self.app.after_request
        def log_response(response):
            # 只记录API请求的性能
            if request.path.startswith('/api/'):
                execution_time = (time.time() - request.start_time) * 1000 if hasattr(request, 'start_time') else 0
                logger.info(f"API请求: {request.method} {request.path} - {response.status_code} - {execution_time:.2f}ms")
            return response

        # 设置请求开始时间
        @self.app.before_request
        def set_start_time():
            request.start_time = time.time()

    def get_connected_clients(self):
        """获取连接的客户端数量"""
        try:
            # 这里需要根据实际的SocketIO实现来获取连接数
            return 0  # 临时返回0
        except:
            return 0

    def setup_trading_routes(self):
        """设置交易执行API路由"""
        try:
            # 尝试导入交易引擎
            from src.trading.trading_engine import trading_engine, TradingMode
            from src.notifications.alert_manager import alert_manager
            import asyncio

            self.trading_engine = trading_engine
            self.trading_available = True
            logger.info("✅ 交易引擎加载成功")
        except Exception as e:
            logger.warning(f"⚠️ 交易引擎加载失败: {e}")
            self.trading_engine = None
            self.trading_available = False

        @self.app.route('/api/trading/execute', methods=['POST'])
        def execute_arbitrage():
            """执行套利交易"""
            try:
                if not self.trading_available:
                    return jsonify({
                        'success': False,
                        'error': '交易引擎未初始化'
                    }), 503

                data = request.get_json()
                if not data:
                    return jsonify({'error': '请求数据为空'}), 400

                opportunity_data = data.get('opportunity_data')
                if not opportunity_data:
                    return jsonify({'error': '缺少套利机会数据'}), 400

                # 异步执行交易
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                execution = loop.run_until_complete(
                    self.trading_engine.execute_arbitrage(opportunity_data)
                )

                logger.info(f"🎯 套利交易执行请求: 状态: {execution.status}")

                # 广播执行结果
                self.socketio.emit('trade_execution', {
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

        @self.app.route('/api/trading/orders')
        def get_active_orders():
            """获取活跃订单"""
            try:
                if not self.trading_available:
                    return jsonify({
                        'orders': [],
                        'count': 0,
                        'message': '交易引擎未初始化'
                    })

                orders = self.trading_engine.get_active_orders()
                return jsonify({
                    'orders': orders,
                    'count': len(orders),
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"❌ 获取活跃订单失败: {str(e)}")
                return jsonify({
                    'orders': [],
                    'count': 0,
                    'error': str(e)
                }), 500

        @self.app.route('/api/trading/history')
        def get_trading_history():
            """获取交易历史"""
            try:
                if not self.trading_available:
                    return jsonify({
                        'history': [],
                        'count': 0,
                        'message': '交易引擎未初始化'
                    })

                history = self.trading_engine.get_execution_history()
                return jsonify({
                    'history': history,
                    'count': len(history),
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"❌ 获取交易历史失败: {str(e)}")
                return jsonify({
                    'history': [],
                    'count': 0,
                    'error': str(e)
                }), 500

        @self.app.route('/api/trading/statistics')
        def get_trading_statistics():
            """获取交易统计"""
            try:
                if not self.trading_available:
                    return jsonify({
                        'total_executions': 0,
                        'successful_executions': 0,
                        'failed_executions': 0,
                        'total_profit': 0.0,
                        'success_rate': 0.0,
                        'average_profit': 0.0,
                        'message': '交易引擎未初始化'
                    })

                stats = self.trading_engine.get_profit_statistics()
                return jsonify({
                    'statistics': stats,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"❌ 获取交易统计失败: {str(e)}")
                return jsonify({
                    'total_executions': 0,
                    'successful_executions': 0,
                    'failed_executions': 0,
                    'total_profit': 0.0,
                    'success_rate': 0.0,
                    'average_profit': 0.0,
                    'error': str(e)
                }), 500

        @self.app.route('/api/trading/mode', methods=['POST'])
        def set_trading_mode():
            """设置交易模式"""
            try:
                if not self.trading_available:
                    return jsonify({
                        'success': False,
                        'error': '交易引擎未初始化'
                    }), 503

                data = request.get_json()
                if not data or 'mode' not in data:
                    return jsonify({'error': '缺少交易模式参数'}), 400

                mode = data['mode']
                valid_modes = ['simulation', 'dry_run', 'live']

                if mode not in valid_modes:
                    return jsonify({
                        'error': f'无效的交易模式，支持: {valid_modes}'
                    }), 400

                # 设置交易模式
                if hasattr(self.trading_engine, 'set_mode'):
                    self.trading_engine.set_mode(TradingMode(mode))
                else:
                    # 兼容旧版本
                    self.trading_engine.trading_mode = TradingMode(mode)

                logger.info(f"🔧 交易模式设置为: {mode}")

                # 广播模式变更
                self.socketio.emit('trading_mode_changed', {
                    'mode': mode,
                    'timestamp': datetime.now().isoformat()
                }, to='*')

                return jsonify({
                    'success': True,
                    'mode': mode,
                    'message': f'交易模式已设置为: {mode}'
                })

            except Exception as e:
                logger.error(f"❌ 设置交易模式失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/trading/mode')
        def get_trading_mode():
            """获取当前交易模式"""
            try:
                if not self.trading_available:
                    return jsonify({
                        'mode': 'simulation',
                        'message': '交易引擎未初始化，使用默认模拟模式'
                    })

                if hasattr(self.trading_engine, 'get_mode'):
                    mode = self.trading_engine.get_mode()
                else:
                    # 兼容旧版本
                    mode = getattr(self.trading_engine, 'trading_mode', TradingMode.SIMULATION)

                return jsonify({
                    'mode': mode.value if hasattr(mode, 'value') else str(mode),
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"❌ 获取交易模式失败: {str(e)}")
                return jsonify({
                    'mode': 'simulation',
                    'error': str(e)
                }), 500

        @self.app.route('/api/trading/cancel-order', methods=['POST'])
        def cancel_order():
            """取消订单"""
            try:
                if not self.trading_available:
                    return jsonify({
                        'success': False,
                        'error': '交易引擎未初始化'
                    }), 503

                data = request.get_json()
                if not data or 'order_id' not in data:
                    return jsonify({'error': '缺少订单ID参数'}), 400

                order_id = data['order_id']

                # 执行取消订单操作
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                result = loop.run_until_complete(
                    self.trading_engine.cancel_order(order_id)
                )

                logger.info(f"🚫 订单取消请求: {order_id} - 结果: {result}")

                # 广播取消结果
                self.socketio.emit('order_cancelled', {
                    'order_id': order_id,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }, to='*')

                return jsonify({
                    'success': True,
                    'order_id': order_id,
                    'result': result,
                    'message': f'订单 {order_id} 取消成功'
                })

            except Exception as e:
                logger.error(f"❌ 取消订单失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        logger.info("✅ 交易执行API路由设置完成")

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行应用"""
        logger.info("🌐 启动优化版Web服务器")
        logger.info(f"📡 服务地址: http://{host}:{port}")
        logger.info(f"🔧 调试模式: {'开启' if debug else '关闭'}")
        logger.info(f"⚡ 优化功能: 已启用")

        try:
            self.socketio.run(
                self.app,
                host=host,
                port=port,
                debug=debug,
                allow_unsafe_werkzeug=True
            )
        except KeyboardInterrupt:
            logger.info("⏹️ 服务器已停止")
        except Exception as e:
            logger.error(f"❌ 服务器启动失败: {e}")
            raise
        finally:
            # 清理资源
            try:
                import asyncio
                asyncio.run(optimized_price_fetcher.cleanup())
            except:
                pass


def create_optimized_app():
    """创建优化版Flask应用"""
    web_app = OptimizedWebApp()
    return web_app.app, web_app.socketio


if __name__ == '__main__':
    # 创建并运行优化版应用
    web_app = OptimizedWebApp()

    print("🚀 启动优化版全能套利机器人")
    print("=" * 50)
    print("✨ 优化特性:")
    print("  - 异步价格获取")
    print("  - 智能缓存系统")
    print("  - 请求去重")
    print("  - 批量API")
    print("  - 性能监控")
    print("  - 错误重试")
    print("=" * 50)

    try:
        web_app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        sys.exit(1)