"""
Web UI 仪表板 - 使用 Flask 提供的实时套利监控系统
访问地址: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
import threading
import time
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.price_fetcher_extended import extended_price_fetcher
from src.notifications.alert_manager import alert_manager
from src.trading.auto_executor import auto_executor
from src.utils.logger import logger
from src.config import CRYPTOS, SCAN_INTERVAL, AUTO_TRADE_ENABLED, ALERT_ENABLED, EXCHANGES
import asyncio

app = Flask(__name__, template_folder='templates')
CORS(app)

# 全局变量用于存储最新数据
latest_prices = {}
latest_opportunities = []
scan_status = "idle"
last_update = None


def background_price_scanner():
    """后台线程：持续扫描价格和套利机会"""
    global latest_prices, latest_opportunities, last_update, scan_status

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            scan_status = "scanning"

            # 获取所有价格
            latest_prices = loop.run_until_complete(extended_price_fetcher.fetch_all_prices(CRYPTOS))

            # 分析套利机会
            opportunities = []
            for crypto in CRYPTOS:
                analysis = extended_price_fetcher.analyze_price_diff(crypto)
                if analysis.get("arbitrage_possible"):
                    opportunity = {
                        "crypto": crypto,
                        "diff_rate": analysis.get("diff_rate"),
                        "buy_exchange": analysis.get("min_exchange"),
                        "buy_price": analysis.get("min_price"),
                        "sell_exchange": analysis.get("max_exchange"),
                        "sell_price": analysis.get("max_price"),
                        "timestamp": datetime.now().isoformat()
                    }
                    opportunities.append(opportunity)

                    # 发送告警
                    if ALERT_ENABLED:
                        loop.run_until_complete(alert_manager.send_arbitrage_alert(opportunity))

                    # 自动执行交易
                    if AUTO_TRADE_ENABLED:
                        execution_result = loop.run_until_complete(auto_executor.execute_arbitrage(opportunity))
                        if execution_result.get("status") in ["executed", "simulated"]:
                            opportunity["auto_executed"] = True
                            opportunity["execution_result"] = execution_result

            latest_opportunities = opportunities
            last_update = datetime.now().isoformat()
            scan_status = "idle"

            enabled_exchanges = len([e for e in EXCHANGES.values() if e.get("enabled", False)])
            logger.info(f"✅ 高频扫描完成 - {enabled_exchanges}个交易所 - 发现 {len(opportunities)} 个套利机会")

            time.sleep(SCAN_INTERVAL)  # 使用配置的扫描间隔

        except Exception as e:
            logger.error(f"❌ 后台扫描错误: {str(e)}")
            scan_status = "error"
            time.sleep(5)


# ============ API 路由 ============

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    return jsonify({
        "status": "running",
        "scan_status": scan_status,
        "last_update": last_update,
        "opportunities_count": len(latest_opportunities),
        "cryptos_tracked": len(CRYPTOS)
    })


@app.route('/api/prices', methods=['GET'])
def get_prices():
    """获取所有加密货币的价格"""
    crypto = request.args.get('crypto')
    
    if crypto:
        # 获取单个币种
        if crypto in latest_prices:
            return jsonify({
                "crypto": crypto,
                "prices": latest_prices[crypto],
                "timestamp": last_update
            })
        else:
            return jsonify({"error": "币种不存在"}), 404
    else:
        # 获取所有币种
        return jsonify({
            "prices": latest_prices,
            "timestamp": last_update,
            "count": len(latest_prices)
        })


@app.route('/api/price-summary/<crypto>', methods=['GET'])
def get_price_summary(crypto):
    """获取单币种的价格详细分析"""
    try:
        analysis = price_fetcher.analyze_price_diff(crypto)
        
        if analysis.get("status") == "error":
            return jsonify({"error": analysis.get("message")}), 404
        
        avg_price = price_fetcher.get_price_average(crypto)
        
        return jsonify({
            "crypto": crypto,
            "prices": analysis.get("prices"),
            "max_price": analysis.get("max_price"),
            "min_price": analysis.get("min_price"),
            "price_diff": analysis.get("price_diff"),
            "diff_rate": analysis.get("diff_rate"),
            "max_exchange": analysis.get("max_exchange"),
            "min_exchange": analysis.get("min_exchange"),
            "avg_price": avg_price,
            "arbitrage_possible": analysis.get("arbitrage_possible"),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/opportunities', methods=['GET'])
def get_opportunities():
    """获取所有套利机会"""
    # 按差价率排序
    sorted_opps = sorted(latest_opportunities, key=lambda x: x['diff_rate'], reverse=True)
    
    return jsonify({
        "opportunities": sorted_opps,
        "count": len(sorted_opps),
        "timestamp": last_update
    })


@app.route('/api/opportunity/<crypto>', methods=['GET'])
def get_opportunity(crypto):
    """获取特定币种的套利机会"""
    for opp in latest_opportunities:
        if opp['crypto'] == crypto:
            return jsonify(opp)
    
    return jsonify({"message": "暂无套利机会"}), 404


@app.route('/api/chart-data/<crypto>', methods=['GET'])
def get_chart_data(crypto):
    """获取图表数据（多交易所价格对比）"""
    try:
        prices = price_fetcher.get_price_multi(crypto)
        
        chart_data = {
            "labels": list(prices.keys()),
            "datasets": [
                {
                    "label": "价格 (USD)",
                    "data": [p.get("price") for p in prices.values()],
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 2
                }
            ]
        }
        
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    if not latest_prices or not latest_opportunities:
        return jsonify({
            "total_opportunities": 0,
            "total_cryptos": len(CRYPTOS),
            "avg_diff_rate": 0,
            "max_diff_rate": 0
        })
    
    diff_rates = [opp['diff_rate'] for opp in latest_opportunities]
    
    return jsonify({
        "total_opportunities": len(latest_opportunities),
        "total_cryptos": len(CRYPTOS),
        "avg_diff_rate": sum(diff_rates) / len(diff_rates) if diff_rates else 0,
        "max_diff_rate": max(diff_rates) if diff_rates else 0,
        "min_diff_rate": min(diff_rates) if diff_rates else 0,
        "last_scan": last_update
    })


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """手动刷新数据"""
    logger.info("📊 手动刷新价格数据...")
    
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


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    enabled_exchanges = [name for name, config in EXCHANGES.items() if config.get("enabled", False)]
    return jsonify({
        "cryptos": CRYPTOS,
        "exchanges": enabled_exchanges,
        "refresh_interval": SCAN_INTERVAL,
        "auto_trade_enabled": AUTO_TRADE_ENABLED,
        "alert_enabled": ALERT_ENABLED,
        "total_exchanges": len(EXCHANGES),
        "enabled_exchanges": len(enabled_exchanges),
        "api_version": "2.0"
    })


@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    """手动执行套利交易"""
    try:
        data = request.get_json()
        opportunity = data.get("opportunity")

        if not opportunity:
            return jsonify({"error": "缺少套利机会数据"}), 400

        # 异步执行交易
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(auto_executor.execute_arbitrage(opportunity))
        loop.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/trade-stats', methods=['GET'])
def get_trade_stats():
    """获取交易统计信息"""
    try:
        stats = auto_executor.get_daily_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/send-alert', methods=['POST'])
def send_alert():
    """发送测试告警"""
    try:
        data = request.get_json()
        title = data.get("title", "测试告警")
        message = data.get("message", "这是一个测试告警")
        level = data.get("level", "info")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(alert_manager.send_system_alert(title, message, level))
        loop.close()

        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/exchanges', methods=['GET'])
def get_exchanges():
    """获取所有交易所状态"""
    exchange_status = {}
    for name, config in EXCHANGES.items():
        exchange_status[name] = {
            "enabled": config.get("enabled", False),
            "has_api_key": bool(config.get("api_key")),
            "has_api_secret": bool(config.get("api_secret")),
            "base_url": config.get("base_url", "")
        }

    return jsonify(exchange_status)


# ============ 错误处理 ============

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
    enabled_exchanges = [name for name, config in EXCHANGES.items() if config.get("enabled", False)]

    print(f"\n{'='*60}")
    print("🚀 启动全能套利机器人 Web UI v2.0")
    print(f"{'='*60}")
    print("\n📍 访问地址: http://localhost:5000")
    print("📊 API 文档: http://localhost:5000/api")

    print(f"\n⚡ 高频扫描:")
    print(f"  - 扫描间隔: {SCAN_INTERVAL} 秒")
    print(f"  - 支持币种: {len(CRYPTOS)} 个 ({', '.join(CRYPTOS)})")
    print(f"  - 支持交易所: {len(enabled_exchanges)} 个 ({', '.join(enabled_exchanges)})")

    print(f"\n🔔 智能功能:")
    print(f"  - 实时告警: {'✅ 已启用' if ALERT_ENABLED else '❌ 已禁用'}")
    print(f"  - 自动交易: {'✅ 已启用' if AUTO_TRADE_ENABLED else '❌ 已禁用 (模拟模式)'}")
    print(f"  - 多交易所支持: 6个主流交易所")
    print(f"  - 套利机会自动发现和执行")

    print(f"\n🛡️ 安全特性:")
    print(f"  - 风险管理和止损")
    print(f"  - 模拟交易模式")
    print(f"  - 实时监控告警")

    print(f"\n按 Ctrl+C 停止服务器\n")

    # 启动后台价格扫描线程
    scanner_thread = threading.Thread(target=background_price_scanner, daemon=True)
    scanner_thread.start()

    # 启动 Flask 服务器
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
