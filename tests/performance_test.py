"""
性能测试和分析脚本
用于评估套利机器人的性能和识别优化点
"""
import time
import logging
from datetime import datetime
import requests
from src.utils.logger import setup_logger

logger = setup_logger("performance_test")

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def test_api_response_time(self):
        """测试 API 响应时间"""
        logger.info("\n" + "="*60)
        logger.info("📊 API 响应时间测试")
        logger.info("="*60)
        
        apis = {
            "Binance": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            "Coinbase": "https://api.coinbase.com/v2/prices/BTC-USD/spot",
            "CoinGecko": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        }
        
        response_times = {}
        for exchange, url in apis.items():
            try:
                start = time.time()
                response = requests.get(url, timeout=5)
                end = time.time()
                
                response_time = (end - start) * 1000  # 转换为毫秒
                response_times[exchange] = response_time
                
                status = "✅" if response.status_code == 200 else "❌"
                logger.info(f"{status} {exchange}: {response_time:.2f}ms (状态码: {response.status_code})")
            except Exception as e:
                logger.error(f"❌ {exchange}: 连接失败 - {str(e)}")
                response_times[exchange] = None
        
        self.results['api_response_times'] = response_times
        return response_times
    
    def test_price_comparison_speed(self):
        """测试价格对比速度"""
        logger.info("\n" + "="*60)
        logger.info("⚡ 价格对比速度测试")
        logger.info("="*60)
        
        # 模拟多个交易所的价格数据
        exchanges_data = {
            "binance": {"BTC": 42500, "ETH": 2350, "SOL": 185},
            "coinbase": {"BTC": 42650, "ETH": 2400, "SOL": 186},
            "kraken": {"BTC": 42550, "ETH": 2370, "SOL": 184},
        }
        
        start = time.time()
        
        # 执行价格对比逻辑
        for crypto in ["BTC", "ETH", "SOL"]:
            prices = {exchange: data[crypto] for exchange, data in exchanges_data.items()}
            min_price = min(prices.values())
            max_price = max(prices.values())
            profit_rate = ((max_price - min_price) / min_price) * 100
        
        end = time.time()
        comparison_time = (end - start) * 1000
        
        logger.info(f"✅ 价格对比耗时: {comparison_time:.2f}ms")
        logger.info(f"   处理 {len(exchanges_data)} 个交易所, {len(exchanges_data[0])} 种加密货币")
        
        self.results['comparison_speed'] = comparison_time
        return comparison_time
    
    def test_database_operations(self):
        """测试数据库操作性能"""
        logger.info("\n" + "="*60)
        logger.info("💾 数据库操作性能测试")
        logger.info("="*60)
        
        db_metrics = {}
        
        try:
            from src.models.trade import Session, PriceSnapshot
            from datetime import datetime
            
            session = Session()
            
            # 测试插入性能
            logger.info("📝 测试数据插入...")
            start = time.time()
            
            test_snapshots = [
                PriceSnapshot(
                    crypto=f"TEST_{i}",
                    exchange="test_exchange",
                    price=50000 + i
                )
                for i in range(100)
            ]
            
            session.bulk_save_objects(test_snapshots)
            session.commit()
            
            end = time.time()
            insert_time = (end - start) * 1000
            logger.info(f"✅ 插入 100 条记录耗时: {insert_time:.2f}ms")
            
            # 测试查询性能
            logger.info("🔍 测试数据查询...")
            start = time.time()
            
            results = session.query(PriceSnapshot).filter(
                PriceSnapshot.crypto.like("TEST%")
            ).all()
            
            end = time.time()
            query_time = (end - start) * 1000
            logger.info(f"✅ 查询 {len(results)} 条记录耗时: {query_time:.2f}ms")
            
            # 清理测试数据
            for snapshot in results:
                session.delete(snapshot)
            session.commit()
            
            db_metrics['insert_time'] = insert_time
            db_metrics['query_time'] = query_time
            
        except Exception as e:
            logger.error(f"❌ 数据库测试失败: {str(e)}")
            db_metrics['error'] = str(e)
        
        self.results['database'] = db_metrics
        return db_metrics
    
    def generate_optimization_report(self):
        """生成优化建议报告"""
        logger.info("\n" + "="*60)
        logger.info("📋 优化建议报告")
        logger.info("="*60)
        
        recommendations = {
            "高优先级": [],
            "中优先级": [],
            "低优先级": []
        }
        
        # 分析 API 响应时间
        api_times = self.results.get('api_response_times', {})
        for exchange, response_time in api_times.items():
            if response_time and response_time > 1000:
                recommendations["高优先级"].append(
                    f"🔴 {exchange} API 响应时间过长 ({response_time:.0f}ms)，"
                    f"建议使用 WebSocket 或实现本地缓存"
                )
            elif response_time and response_time > 500:
                recommendations["中优先级"].append(
                    f"🟡 {exchange} API 响应时间 ({response_time:.0f}ms)，"
                    f"可考虑添加连接池"
                )
        
        # 分析数据库性能
        db_metrics = self.results.get('database', {})
        if db_metrics.get('insert_time', 0) > 100:
            recommendations["中优先级"].append(
                "🟡 数据库插入性能较低，建议批量操作或使用异步写入"
            )
        
        if db_metrics.get('query_time', 0) > 100:
            recommendations["中优先级"].append(
                "🟡 数据库查询性能较低，建议添加索引或使用缓存"
            )
        
        # 添加通用建议
        recommendations["中优先级"].extend([
            "🟡 实现异步处理优化扫描速度",
            "🟡 添加请求限流防止 API 频率限制",
            "🟡 实现本地价格缓存减少 API 调用"
        ])
        
        recommendations["低优先级"].extend([
            "🟢 添加 WebSocket 支持获取实时价格",
            "🟢 实现分布式套利机制支持多账户",
            "🟢 添加机器学习预测最优套利时间"
        ])
        
        # 打印建议
        for priority, items in recommendations.items():
            logger.info(f"\n{priority}:")
            for item in items:
                logger.info(f"  {item}")
        
        return recommendations
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("\n" + "="*70)
        logger.info("🤖 加密货币套利机器人 - 性能测试和分析")
        logger.info("="*70)
        
        self.start_time = datetime.now()
        
        # 运行所有测试
        self.test_api_response_time()
        self.test_price_comparison_speed()
        self.test_database_operations()
        
        # 生成报告
        recommendations = self.generate_optimization_report()
        
        self.end_time = datetime.now()
        
        # 总结
        logger.info("\n" + "="*70)
        logger.info("✅ 测试完成")
        logger.info(f"总耗时: {(self.end_time - self.start_time).total_seconds():.2f}秒")
        logger.info("="*70)
        
        return self.results, recommendations


if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    results, recommendations = analyzer.run_all_tests()
