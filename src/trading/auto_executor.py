"""
自动交易执行器 - 智能套利交易执行
支持多交易所API、风险管理、模拟交易
"""

import asyncio
import aiohttp
import hashlib
import hmac
import base64
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from src.utils.logger import logger
from src.config import (
    AUTO_TRADE_ENABLED, EXCHANGES, MIN_PROFIT_THRESHOLD,
    MAX_TRADE_SIZE, TRADE_DELAY_SECONDS, SIMULATION_MODE, DRY_RUN,
    MAX_POSITION_SIZE, STOP_LOSS_PERCENT
)


class ExchangeAPI:
    """交易所API基类"""

    def __init__(self, exchange_name: str, config: Dict):
        self.exchange_name = exchange_name
        self.api_key = config.get("api_key", "")
        self.api_secret = config.get("api_secret", "")
        self.base_url = config.get("base_url", "")
        self.passphrase = config.get("passphrase", "")
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _generate_signature(self, method: str, url: str, body: str = "") -> str:
        """生成API签名（各交易所不同）"""
        # 基础HMAC签名，子类可重写
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def get_balance(self) -> Dict:
        """获取账户余额"""
        raise NotImplementedError("子类必须实现此方法")

    async def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        """下单"""
        raise NotImplementedError("子类必须实现此方法")

    async def get_order_status(self, order_id: str) -> Dict:
        """获取订单状态"""
        raise NotImplementedError("子类必须实现此方法")


class BinanceAPI(ExchangeAPI):
    """币安API"""

    def _generate_signature(self, params: str = "") -> str:
        return hmac.new(
            self.api_secret.encode('utf-8'),
            params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    async def get_balance(self) -> Dict:
        try:
            timestamp = int(time.time() * 1000)
            params = f"timestamp={timestamp}"
            signature = self._generate_signature(params)

            headers = {"X-MBX-APIKEY": self.api_key}
            url = f"{self.base_url}/api/v3/account?{params}&signature={signature}"

            async with self.session.get(url, headers=headers) as response:
                data = await response.json()
                return {
                    "status": "success" if response.status == 200 else "error",
                    "balances": {b["asset"]: float(b["free"]) for b in data.get("balances", [])}
                }
        except Exception as e:
            logger.error(f"币安获取余额失败: {e}")
            return {"status": "error", "message": str(e)}

    async def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        try:
            timestamp = int(time.time() * 1000)

            params = {
                "symbol": symbol,
                "side": side,
                "type": "MARKET" if price is None else "LIMIT",
                "quantity": f"{amount:.6f}",
                "timestamp": timestamp
            }

            if price:
                params["price"] = f"{price:.2f}"
                params["timeInForce"] = "GTC"

            params_str = "&".join([f"{k}={v}" for k, v in params.items()])
            signature = self._generate_signature(params_str)

            headers = {"X-MBX-APIKEY": self.api_key}
            url = f"{self.base_url}/api/v3/order?{params_str}&signature={signature}"

            async with self.session.post(url, headers=headers) as response:
                data = await response.json()
                return {
                    "status": "success" if response.status == 200 else "error",
                    "order_id": data.get("orderId"),
                    "data": data
                }
        except Exception as e:
            logger.error(f"币安下单失败: {e}")
            return {"status": "error", "message": str(e)}


class OKXAPI(ExchangeAPI):
    """OKX API"""

    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        sign_str = timestamp + method + path + body
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')

    async def get_balance(self) -> Dict:
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"
            path = "/api/v5/account/balance"
            signature = self._generate_signature(timestamp, "GET", path)

            headers = {
                "OK-ACCESS-KEY": self.api_key,
                "OK-ACCESS-SIGN": signature,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": self.passphrase
            }

            url = self.base_url + path
            async with self.session.get(url, headers=headers) as response:
                data = await response.json()
                if data.get("code") == "0":
                    balances = {}
                    for item in data.get("data", [])[0].get("details", []):
                        balances[item["ccy"]] = float(item["availBal"])
                    return {"status": "success", "balances": balances}
                else:
                    return {"status": "error", "message": data.get("msg", "Unknown error")}
        except Exception as e:
            logger.error(f"OKX获取余额失败: {e}")
            return {"status": "error", "message": str(e)}

    async def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"
            path = "/api/v5/trade/order"

            body = {
                "instId": symbol,
                "tdMode": "cash",
                "side": "buy" if side == "BUY" else "sell",
                "ordType": "market" if price is None else "limit",
                "sz": str(amount)
            }

            if price:
                body["px"] = str(price)

            body_str = str(body).replace("'", '"').replace(" ", "")
            signature = self._generate_signature(timestamp, "POST", path, body_str)

            headers = {
                "OK-ACCESS-KEY": self.api_key,
                "OK-ACCESS-SIGN": signature,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": self.passphrase,
                "Content-Type": "application/json"
            }

            url = self.base_url + path
            async with self.session.post(url, headers=headers, json=body) as response:
                data = await response.json()
                if data.get("code") == "0":
                    return {
                        "status": "success",
                        "order_id": data.get("data", [{}])[0].get("ordId"),
                        "data": data
                    }
                else:
                    return {"status": "error", "message": data.get("msg", "Unknown error")}
        except Exception as e:
            logger.error(f"OKX下单失败: {e}")
            return {"status": "error", "message": str(e)}


class AutoTradeExecutor:
    """自动交易执行器"""

    def __init__(self):
        self.exchanges = {}
        self.position_sizes = {}  # 持仓大小追踪
        self.daily_trades = []    # 今日交易记录
        self.daily_pnl = 0.0      # 今日盈亏

    def get_exchange_api(self, exchange_name: str) -> Optional[ExchangeAPI]:
        """获取交易所API实例"""
        if exchange_name in self.exchanges:
            return self.exchanges[exchange_name]

        config = EXCHANGES.get(exchange_name, {})
        if not config.get("enabled", False) or not config.get("api_key"):
            logger.warning(f"{exchange_name} 未启用或API配置不完整")
            return None

        # 创建对应的API实例
        if exchange_name == "binance":
            api = BinanceAPI(exchange_name, config)
        elif exchange_name == "okx":
            api = OKXAPI(exchange_name, config)
        else:
            logger.warning(f"{exchange_name} 暂不支持自动交易")
            return None

        self.exchanges[exchange_name] = api
        return api

    def validate_opportunity(self, opportunity: Dict) -> Tuple[bool, str]:
        """验证套利机会是否值得执行"""
        diff_rate = opportunity.get("diff_rate", 0)
        potential_profit = opportunity.get("potential_profit", 0)

        # 检查利润率
        if diff_rate < MIN_PROFIT_THRESHOLD * 100:
            return False, f"利润率过低: {diff_rate:.2f}% < {MIN_PROFIT_THRESHOLD * 100}%"

        # 检查预期利润
        if potential_profit < MIN_PROFIT_THRESHOLD * MAX_TRADE_SIZE:
            return False, f"预期利润过低: ${potential_profit:.2f}"

        # 检查交易大小
        if potential_profit > MAX_TRADE_SIZE:
            return False, f"交易风险过高: ${potential_profit:.2f} > ${MAX_TRADE_SIZE}"

        return True, "验证通过"

    async def check_balance(self, exchange_name: str, required_usdt: float) -> bool:
        """检查交易所余额是否足够"""
        api = self.get_exchange_api(exchange_name)
        if not api:
            return False

        try:
            async with api:
                balance_result = await api.get_balance()
                if balance_result["status"] == "success":
                    usdt_balance = balance_result["balances"].get("USDT", 0)
                    return usdt_balance >= required_usdt
        except Exception as e:
            logger.error(f"检查 {exchange_name} 余额失败: {e}")

        return False

    async def execute_arbitrage(self, opportunity: Dict) -> Dict:
        """执行套利交易"""
        if not AUTO_TRADE_ENABLED:
            return {"status": "error", "message": "自动交易未启用"}

        # 验证机会
        is_valid, reason = self.validate_opportunity(opportunity)
        if not is_valid:
            logger.info(f"套利机会验证失败: {reason}")
            return {"status": "rejected", "reason": reason}

        buy_exchange = opportunity["buy_exchange"]
        sell_exchange = opportunity["sell_exchange"]
        crypto = opportunity["crypto"]
        buy_price = opportunity["buy_price"]
        sell_price = opportunity["sell_price"]

        logger.info(f"🚀 开始执行套利: {crypto} - {buy_exchange} -> {sell_exchange}")

        # 模拟模式
        if SIMULATION_MODE:
            return await self._simulate_arbitrage(opportunity)

        # 试运行模式
        if DRY_RUN:
            return await self._dry_run_arbitrage(opportunity)

        # 实际交易模式
        return await self._execute_real_arbitrage(opportunity)

    async def _simulate_arbitrage(self, opportunity: Dict) -> Dict:
        """模拟套利交易"""
        crypto = opportunity["crypto"]
        buy_price = opportunity["buy_price"]
        sell_price = opportunity["sell_price"]
        trade_amount = min(MAX_TRADE_SIZE, 1000)  # 固定模拟金额

        # 计算费用和利润
        buy_fee = trade_amount * 0.001  # 0.1% 手续费
        sell_fee = (trade_amount / buy_price) * sell_price * 0.001

        gross_profit = (sell_price - buy_price) * (trade_amount / buy_price)
        net_profit = gross_profit - buy_fee - sell_fee

        result = {
            "status": "simulated",
            "trade_amount": trade_amount,
            "gross_profit": gross_profit,
            "fees": buy_fee + sell_fee,
            "net_profit": net_profit,
            "profit_rate": (net_profit / trade_amount) * 100,
            "execution_time": datetime.now().isoformat()
        }

        logger.info(f"🎯 模拟套利完成: 净利润 ${net_profit:.2f} ({result['profit_rate']:.2f}%)")
        return result

    async def _dry_run_arbitrage(self, opportunity: Dict) -> Dict:
        """试运行套利交易（不实际下单）"""
        buy_exchange = opportunity["buy_exchange"]
        sell_exchange = opportunity["sell_exchange"]
        crypto = opportunity["crypto"]

        # 检查余额
        buy_api = self.get_exchange_api(buy_exchange)
        sell_api = self.get_exchange_api(sell_exchange)

        if not buy_api or not sell_api:
            return {"status": "error", "message": "交易所API不可用"}

        trade_amount = min(MAX_TRADE_SIZE, 1000)

        # 检查购买所需余额
        async with buy_api:
            buy_balance = await buy_api.get_balance()
            if buy_balance["status"] != "success":
                return {"status": "error", "message": f"无法获取 {buy_exchange} 余额"}

            usdt_balance = buy_balance["balances"].get("USDT", 0)
            if usdt_balance < trade_amount:
                return {"status": "error", "message": f"{buy_exchange} USDT余额不足"}

        logger.info(f"🔍 试运行检查通过，所有条件满足")
        return {
            "status": "dry_run_completed",
            "trade_amount": trade_amount,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "message": "试运行成功，实际交易可以执行"
        }

    async def _execute_real_arbitrage(self, opportunity: Dict) -> Dict:
        """执行实际套利交易"""
        buy_exchange = opportunity["buy_exchange"]
        sell_exchange = opportunity["sell_exchange"]
        crypto = opportunity["crypto"]
        buy_price = opportunity["buy_price"]
        sell_price = opportunity["sell_price"]

        # 获取交易对符号
        symbol_map = {
            "binance": {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"},
            "okx": {"BTC": "BTC-USDT", "ETH": "ETH-USDT", "SOL": "SOL-USDT"},
            "bybit": {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"},
            "bitget": {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"}
        }

        buy_symbol = symbol_map.get(buy_exchange, {}).get(crypto)
        sell_symbol = symbol_map.get(sell_exchange, {}).get(crypto)

        if not buy_symbol or not sell_symbol:
            return {"status": "error", "message": "无法获取交易对符号"}

        # 计算交易数量
        trade_amount_usdt = min(MAX_TRADE_SIZE, 1000)
        buy_quantity = trade_amount_usdt / buy_price

        # 获取API实例
        buy_api = self.get_exchange_api(buy_exchange)
        sell_api = self.get_exchange_api(sell_exchange)

        if not buy_api or not sell_api:
            return {"status": "error", "message": "交易所API不可用"}

        try:
            # 执行买入订单
            logger.info(f"💰 在 {buy_exchange} 买入 {crypto}")
            async with buy_api:
                buy_result = await buy_api.place_order(buy_symbol, "BUY", buy_quantity)
                if buy_result["status"] != "success":
                    return {"status": "error", "message": f"买入失败: {buy_result.get('message')}"}

                # 等待订单执行
                await asyncio.sleep(TRADE_DELAY_SECONDS)

            # 执行卖出订单
            logger.info(f"💸 在 {sell_exchange} 卖出 {crypto}")
            async with sell_api:
                sell_result = await sell_api.place_order(sell_symbol, "SELL", buy_quantity)
                if sell_result["status"] != "success":
                    return {"status": "error", "message": f"卖出失败: {sell_result.get('message')}"}

            # 计算实际利润
            gross_profit = (sell_price - buy_price) * buy_quantity
            fees = trade_amount_usdt * 0.002  # 0.2% 总手续费
            net_profit = gross_profit - fees

            result = {
                "status": "executed",
                "buy_order_id": buy_result.get("order_id"),
                "sell_order_id": sell_result.get("order_id"),
                "trade_amount": trade_amount_usdt,
                "buy_quantity": buy_quantity,
                "gross_profit": gross_profit,
                "net_profit": net_profit,
                "profit_rate": (net_profit / trade_amount_usdt) * 100,
                "execution_time": datetime.now().isoformat()
            }

            # 更新统计
            self.daily_pnl += net_profit
            self.daily_trades.append(result)

            logger.info(f"✅ 套利执行完成: 净利润 ${net_profit:.2f} ({result['profit_rate']:.2f}%)")
            return result

        except Exception as e:
            logger.error(f"❌ 套利执行失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_daily_stats(self) -> Dict:
        """获取今日交易统计"""
        return {
            "total_trades": len(self.daily_trades),
            "total_pnl": self.daily_pnl,
            "avg_profit_per_trade": self.daily_pnl / len(self.daily_trades) if self.daily_trades else 0,
            "success_rate": sum(1 for t in self.daily_trades if t["net_profit"] > 0) / len(self.daily_trades) if self.daily_trades else 0,
            "trades": self.daily_trades[-10:]  # 最近10笔交易
        }


# 全局实例
auto_executor = AutoTradeExecutor()


async def execute_arbitrage(opportunity: Dict) -> Dict:
    """执行套利交易的便捷函数"""
    return await auto_executor.execute_arbitrage(opportunity)


if __name__ == "__main__":
    # 测试代码
    async def test_execution():
        opportunity = {
            "crypto": "BTC",
            "buy_exchange": "binance",
            "sell_exchange": "okx",
            "buy_price": 45000,
            "sell_price": 46650,
            "diff_rate": 3.5,
            "potential_profit": 1650
        }

        result = await execute_arbitrage(opportunity)
        print("执行结果:", result)

    asyncio.run(test_execution())