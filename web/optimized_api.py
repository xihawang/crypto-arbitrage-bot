"""
优化版Web API
性能优化重点：
1. 请求去重和缓存
2. 数据预聚合
3. 响应压缩
4. 连接池管理
5. 错误处理优化
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps, lru_cache
from flask import Flask, request, jsonify, Response
from flask_caching import Cache
import gzip
import hashlib
from src.utils.logger import logger


class OptimizedAPI:
    """优化版API管理器"""

    def __init__(self, app: Flask):
        self.app = app
        self.setup_cache()
        self.setup_request_optimization()

        # 请求去重
        self.request_cache = {}
        self.request_lock = threading.Lock()

        # 响应缓存
        self.response_cache = {}
        self.cache_timestamps = {}

        # 数据预聚合
        self.pre_aggregated_data = {}
        self.aggregation_thread = None
        self.start_aggregation_thread()

        logger.info("✅ 优化版API管理器初始化完成")

    def setup_cache(self):
        """设置缓存系统"""
        cache_config = {
            'CACHE_TYPE': 'simple',
            'CACHE_DEFAULT_TIMEOUT': 300,  # 5分钟
            'CACHE_THRESHOLD': 1000,       # 最大缓存项数
            'CACHE_KEY_PREFIX': 'arbitrage_',
        }

        try:
            self.cache = Cache(self.app, config=cache_config)
            logger.info("✅ 缓存系统设置完成")
        except Exception as e:
            logger.warning(f"缓存系统设置失败，使用内存缓存: {e}")
            self.cache = None

    def setup_request_optimization(self):
        """设置请求优化"""
        # 添加响应头优化
        @self.app.after_request
        def add_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'

            # 启用gzip压缩
            if (len(response.data) > 1024 and
                'gzip' in request.headers.get('Accept-Encoding', '')):
                response.data = gzip.compress(response.data)
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(response.data)

            return response

    def generate_request_key(self, endpoint: str, args: Dict = None) -> str:
        """生成请求唯一key"""
        key_data = {
            'endpoint': endpoint,
            'args': args or {},
            'timestamp': int(time.time() // 5)  # 5秒内同一请求视为重复
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def deduplicate_request(self, key: str) -> Optional[Any]:
        """请求去重检查"""
        with self.request_lock:
            if key in self.request_cache:
                cached_response, timestamp = self.request_cache[key]
                # 5秒内的重复请求返回缓存
                if time.time() - timestamp < 5:
                    return cached_response
                else:
                    del self.request_cache[key]
            return None

    def cache_request(self, key: str, response: Any) -> None:
        """缓存请求结果"""
        with self.request_lock:
            self.request_cache[key] = (response, time.time())

            # 清理过期缓存
            current_time = time.time()
            expired_keys = [
                k for k, (_, timestamp) in self.request_cache.items()
                if current_time - timestamp > 10  # 10秒过期
            ]
            for k in expired_keys:
                del self.request_cache[k]

    def get_cached_response(self, cache_key: str, max_age: int = 1) -> Optional[Dict]:
        """获取缓存的响应"""
        if cache_key in self.response_cache:
            data, timestamp = self.response_cache[cache_key]
            if time.time() - timestamp < max_age:
                return data
            else:
                del self.response_cache[cache_key]
                del self.cache_timestamps[cache_key]
        return None

    def cache_response(self, cache_key: str, data: Dict) -> None:
        """缓存响应数据"""
        self.response_cache[cache_key] = (data, time.time())
        self.cache_timestamps[cache_key] = time.time()

        # 清理过期缓存
        current_time = time.time()
        expired_keys = [
            k for k, timestamp in self.cache_timestamps.items()
            if current_time - timestamp > 60  # 1分钟过期
        ]
        for k in expired_keys:
            if k in self.response_cache:
                del self.response_cache[k]
            del self.cache_timestamps[k]

    def start_aggregation_thread(self):
        """启动数据预聚合线程"""
        def aggregate_data():
            while True:
                try:
                    self.pre_aggregate_data()
                    time.sleep(30)  # 30秒聚合一次
                except Exception as e:
                    logger.error(f"数据聚合失败: {e}")
                    time.sleep(10)

        self.aggregation_thread = threading.Thread(target=aggregate_data, daemon=True)
        self.aggregation_thread.start()
        logger.info("✅ 数据预聚合线程已启动")

    def pre_aggregate_data(self):
        """预聚合数据"""
        try:
            # 预聚合价格数据
            from src.utils.optimized_price_fetcher import optimized_price_fetcher
            cryptos = ["BTC", "ETH", "SOL", "USDT", "USDC"]

            prices = optimized_price_fetcher.fetch_all_prices(cryptos)
            opportunities = optimized_price_fetcher.get_all_opportunities(cryptos, prices)

            # 计算聚合统计
            total_profit = sum(opp.get('potential_profit', 0) for opp in opportunities)
            high_profit_opps = [opp for opp in opportunities if opp.get('diff_rate', 0) > 0.5]

            self.pre_aggregated_data = {
                'timestamp': time.time(),
                'prices': prices,
                'opportunities': opportunities,
                'stats': {
                    'total_opportunities': len(opportunities),
                    'total_profit': total_profit,
                    'high_profit_count': len(high_profit_opps),
                    'best_opportunity': opportunities[0] if opportunities else None
                },
                'performance_stats': optimized_price_fetcher.get_performance_stats()
            }

            logger.debug("✅ 数据预聚合完成")

        except Exception as e:
            logger.error(f"数据预聚合失败: {e}")

    def optimized_endpoint(self, max_age: int = 1):
        """优化版API端点装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 生成缓存key
                endpoint_name = f.__name__
                args_json = json.dumps([args, kwargs], sort_keys=True)
                cache_key = f"{endpoint_name}_{hashlib.md5(args_json.encode()).hexdigest()}"

                # 检查响应缓存
                cached_data = self.get_cached_response(cache_key, max_age)
                if cached_data:
                    return jsonify(cached_data)

                # 检查请求去重
                request_key = self.generate_request_key(endpoint_name, request.args.to_dict())
                cached_response = self.deduplicate_request(request_key)
                if cached_response:
                    return cached_response

                try:
                    # 执行原始函数
                    start_time = time.time()
                    result = f(*args, **kwargs)
                    execution_time = time.time() - start_time

                    # 格式化响应
                    if isinstance(result, dict):
                        result['performance'] = {
                            'execution_time': round(execution_time * 1000, 2),
                            'timestamp': datetime.now().isoformat(),
                            'cached': False
                        }
                        response_data = result
                    else:
                        response_data = {
                            'data': result,
                            'performance': {
                                'execution_time': round(execution_time * 1000, 2),
                                'timestamp': datetime.now().isoformat(),
                                'cached': False
                            }
                        }

                    # 缓存结果
                    self.cache_response(cache_key, response_data)

                    # 缓存请求去重
                    response = jsonify(response_data)
                    self.cache_request(request_key, response)

                    return response

                except Exception as e:
                    logger.error(f"API端点 {endpoint_name} 执行失败: {e}")
                    error_response = {
                        'error': str(e),
                        'status': 'error',
                        'performance': {
                            'execution_time': 0,
                            'timestamp': datetime.now().isoformat(),
                            'cached': False
                        }
                    }
                    return jsonify(error_response), 500

            return decorated_function
        return decorator

    def get_pre_aggregated_data(self, data_type: str) -> Dict:
        """获取预聚合数据"""
        if not self.pre_aggregated_data:
            return {}

        age = time.time() - self.pre_aggregated_data['timestamp']
        if age > 60:  # 1分钟过期
            return {}

        return self.pre_aggregated_data.get(data_type, {})


def setup_optimized_routes(app: Flask):
    """设置优化版路由"""
    api_optimizer = OptimizedAPI(app)

    # 优化版价格API
    @app.route('/api/v2/prices', methods=['GET'])
    @api_optimizer.optimized_endpoint(max_age=1)
    def get_prices_v2():
        """优化版价格API - 使用预聚合数据"""
        pre_aggregated = api_optimizer.get_pre_aggregated_data('prices')
        if pre_aggregated:
            return {
                'status': 'success',
                'data_source': 'pre_aggregated',
                'prices': pre_aggregated,
                'cache_status': 'hit'
            }

        # 回退到实时获取
        from src.utils.optimized_price_fetcher import optimized_price_fetcher
        cryptos = ["BTC", "ETH", "SOL", "USDT", "USDC"]
        prices = optimized_price_fetcher.fetch_all_prices(cryptos)

        return {
            'status': 'success',
            'data_source': 'realtime',
            'prices': prices,
            'cache_status': 'miss'
        }

    # 优化版机会API
    @app.route('/api/v2/opportunities', methods=['GET'])
    @api_optimizer.optimized_endpoint(max_age=2)
    def get_opportunities_v2():
        """优化版机会API - 使用预聚合数据"""
        pre_aggregated = api_optimizer.get_pre_aggregated_data('opportunities')
        if pre_aggregated:
            return {
                'status': 'success',
                'data_source': 'pre_aggregated',
                'opportunities': {
                    'spot_arbitrage': pre_aggregated
                },
                'cache_status': 'hit'
            }

        # 回退到实时计算
        from src.utils.optimized_price_fetcher import optimized_price_fetcher
        cryptos = ["BTC", "ETH", "SOL", "USDT", "USDC"]
        prices = optimized_price_fetcher.fetch_all_prices(cryptos)
        opportunities = optimized_price_fetcher.get_all_opportunities(cryptos, prices)

        return {
            'status': 'success',
            'data_source': 'realtime',
            'opportunities': {
                'spot_arbitrage': opportunities
            },
            'cache_status': 'miss'
        }

    # 优化版统计API
    @app.route('/api/v2/stats', methods=['GET'])
    @api_optimizer.optimized_endpoint(max_age=5)
    def get_stats_v2():
        """优化版统计API - 使用预聚合数据"""
        pre_aggregated_stats = api_optimizer.get_pre_aggregated_data('stats')
        performance_stats = api_optimizer.get_pre_aggregated_data('performance_stats')

        if pre_aggregated_stats:
            return {
                'status': 'success',
                'data_source': 'pre_aggregated',
                'stats': pre_aggregated_stats,
                'performance': performance_stats,
                'cache_status': 'hit'
            }

        # 基础统计数据
        from src.utils.optimized_price_fetcher import optimized_price_fetcher
        performance = optimized_price_fetcher.get_performance_stats()

        return {
            'status': 'success',
            'data_source': 'basic',
            'stats': {
                'total_opportunities': 0,
                'total_profit': 0,
                'high_profit_count': 0,
                'best_opportunity': None
            },
            'performance': performance,
            'cache_status': 'miss'
        }

    # 批量API - 一次请求获取多个数据
    @app.route('/api/v2/dashboard', methods=['GET'])
    @api_optimizer.optimized_endpoint(max_age=1)
    def get_dashboard_v2():
        """优化版仪表板API - 批量返回所有需要的数据"""
        # 尝试使用预聚合数据
        pre_aggregated = api_optimizer.pre_aggregated_data
        age = time.time() - pre_aggregated.get('timestamp', 0)

        if pre_aggregated and age < 30:  # 30秒内的数据
            return {
                'status': 'success',
                'data_source': 'pre_aggregated',
                'data': {
                    'prices': pre_aggregated.get('prices', {}),
                    'opportunities': {
                        'spot_arbitrage': pre_aggregated.get('opportunities', [])
                    },
                    'stats': pre_aggregated.get('stats', {}),
                    'performance': pre_aggregated.get('performance_stats', {}),
                    'cache_status': 'hit'
                }
            }

        # 回退到实时获取
        from src.utils.optimized_price_fetcher import optimized_price_fetcher
        cryptos = ["BTC", "ETH", "SOL", "USDT", "USDC"]

        start_time = time.time()
        prices = optimized_price_fetcher.fetch_all_prices(cryptos)
        opportunities = optimized_price_fetcher.get_all_opportunities(cryptos, prices)
        performance = optimized_price_fetcher.get_performance_stats()

        # 计算统计
        total_profit = sum(opp.get('potential_profit', 0) for opp in opportunities)
        stats = {
            'total_opportunities': len(opportunities),
            'total_profit': total_profit,
            'high_profit_count': len([opp for opp in opportunities if opp.get('diff_rate', 0) > 0.5]),
            'best_opportunity': opportunities[0] if opportunities else None
        }

        execution_time = time.time() - start_time

        return {
            'status': 'success',
            'data_source': 'realtime',
            'data': {
                'prices': prices,
                'opportunities': {
                    'spot_arbitrage': opportunities
                },
                'stats': stats,
                'performance': performance,
                'cache_status': 'miss'
            },
            'performance': {
                'total_execution_time': round(execution_time * 1000, 2),
                'timestamp': datetime.now().isoformat()
            }
        }

    # 性能监控API
    @app.route('/api/v2/performance', methods=['GET'])
    def get_performance_monitoring():
        """性能监控API"""
        from src.utils.optimized_price_fetcher import optimized_price_fetcher

        return {
            'api_optimizer': {
                'cached_requests': len(api_optimizer.request_cache),
                'cached_responses': len(api_optimizer.response_cache),
                'pre_aggregated_age': time.time() - api_optimizer.pre_aggregated_data.get('timestamp', 0)
            },
            'price_fetcher': optimized_price_fetcher.get_performance_stats(),
            'system': {
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time()
            }
        }

    logger.info("✅ 优化版API路由设置完成")
    return api_optimizer