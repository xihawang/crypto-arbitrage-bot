"""
交易执行引擎
负责执行套利交易、订单管理、状态跟踪
"""

import asyncio
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from src.utils.logger import logger
from src.utils.multi_source_price_fetcher import multi_source_price_fetcher


class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "pending"          # 待执行
    SUBMITTED = "submitted"      # 已提交
    PARTIAL_FILLED = "partial_filled"  # 部分成交
    FILLED = "filled"           # 完全成交
    CANCELLED = "cancelled"      # 已取消
    FAILED = "failed"           # 执行失败


class OrderType(Enum):
    """订单类型枚举"""
    BUY = "buy"
    SELL = "sell"


class TradingMode(Enum):
    """交易模式枚举"""
    LIVE = "live"           # 实盘交易
    SIMULATION = "simulation"  # 模拟交易
    DRY_RUN = "dry_run"     # 试运行（不实际下单）


@dataclass
class Order:
    """订单数据模型"""
    id: str
    opportunity_id: str
    exchange: str
    type: OrderType
    symbol: str
    amount: float
    price: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    filled_amount: float = 0.0
    filled_price: float = 0.0
    fee: float = 0.0
    error_message: str = ""

    def to_dict(self):
        """转换为字典"""
        data = asdict(self)
        data['type'] = self.type.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class ArbitrageExecution:
    """套利执行记录"""
    id: str
    crypto: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    amount: float
    expected_profit: float
    actual_profit: float
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    buy_order: Optional[Order] = None
    sell_order: Optional[Order] = None
    notes: str = ""

    def to_dict(self):
        """转换为字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        if self.buy_order:
            data['buy_order'] = self.buy_order.to_dict()
        if self.sell_order:
            data['sell_order'] = self.sell_order.to_dict()
        return data


class TradingEngine:
    """交易执行引擎"""

    def __init__(self, mode: TradingMode = TradingMode.SIMULATION):
        self.mode = mode
        self.active_orders: Dict[str, Order] = {}
        self.execution_history: List[ArbitrageExecution] = []
        self.price_fetcher = multi_source_price_fetcher

        # 配置参数
        self.min_profit_threshold = 0.1  # 最小利润率阈值(%)
        self.max_position_size = 1000    # 最大头寸大小(USD)
        self.fee_rate = 0.001              # 交易费率(0.1%)

        logger.info(f"🔄 交易引擎初始化完成 - 模式: {mode.value}")

    async def execute_arbitrage(self, opportunity: Dict) -> ArbitrageExecution:
        """
        执行套利交易

        Args:
            opportunity: 套利机会数据

        Returns:
            ArbitrageExecution: 执行记录
        """
        execution_id = str(uuid.uuid4())

        # 验证套利机会
        validation_result = self._validate_opportunity(opportunity)
        if not validation_result['valid']:
            logger.warning(f"❌ 套利机会验证失败: {validation_result['reason']}")
            return self._create_failed_execution(execution_id, opportunity, validation_result['reason'])

        # 创建执行记录
        execution = ArbitrageExecution(
            id=execution_id,
            crypto=opportunity['crypto'],
            buy_exchange=opportunity['buy_exchange'],
            sell_exchange=opportunity['sell_exchange'],
            buy_price=opportunity['buy_price'],
            sell_price=opportunity['sell_price'],
            amount=self._calculate_position_size(opportunity),
            expected_profit=opportunity['potential_profit'],
            actual_profit=0.0,
            status="executing",
            created_at=datetime.now()
        )

        logger.info(f"🎯 开始执行套利: {execution.crypto} {execution.buy_exchange}→{execution.sell_exchange}")

        try:
            # 执行买入订单
            buy_order = await self._execute_buy_order(execution)
            execution.buy_order = buy_order

            if buy_order.status != OrderStatus.FILLED:
                execution.status = "buy_failed"
                execution.notes = f"买入订单失败: {buy_order.error_message}"
                execution.actual_profit = -self.fee_rate * execution.amount * execution.buy_price
                execution.completed_at = datetime.now()
                self.execution_history.append(execution)
                return execution

            # 执行卖出订单
            sell_order = await self._execute_sell_order(execution)
            execution.sell_order = sell_order

            # 计算实际利润
            execution.actual_profit = self._calculate_actual_profit(execution)
            execution.status = "completed" if sell_order.status == OrderStatus.FILLED else "partial_completed"
            execution.completed_at = datetime.now()

            logger.info(f"✅ 套利执行完成: {execution.crypto} 利润: ${execution.actual_profit:.2f}")

        except Exception as e:
            logger.error(f"❌ 套利执行异常: {str(e)}")
            execution.status = "failed"
            execution.notes = f"执行异常: {str(e)}"
            execution.actual_profit = -self.fee_rate * execution.amount * execution.buy_price
            execution.completed_at = datetime.now()

        self.execution_history.append(execution)
        return execution

    async def _execute_buy_order(self, execution: ArbitrageExecution) -> Order:
        """执行买入订单"""
        order_id = str(uuid.uuid4())

        order = Order(
            id=order_id,
            opportunity_id=execution.id,
            exchange=execution.buy_exchange,
            type=OrderType.BUY,
            symbol=f"{execution.crypto}/USDT",
            amount=execution.amount,
            price=execution.buy_price,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        logger.info(f"📈 执行买入订单: {execution.crypto} @ ${execution.buy_price} 数量: {execution.amount}")

        if self.mode == TradingMode.SIMULATION:
            # 模拟交易
            await asyncio.sleep(0.5)  # 模拟网络延迟
            order.status = OrderStatus.FILLED
            order.filled_amount = order.amount
            order.filled_price = order.price
            order.fee = order.amount * order.price * self.fee_rate
            order.updated_at = datetime.now()
            logger.info(f"✅ 模拟买入订单完成: {execution.crypto}")

        elif self.mode == TradingMode.DRY_RUN:
            # 试运行模式
            order.status = OrderStatus.FILLED
            order.filled_amount = order.amount
            order.filled_price = order.price
            order.fee = order.amount * order.price * self.fee_rate
            order.updated_at = datetime.now()
            logger.info(f"🧪 试运行买入订单: {execution.crypto}")

        else:
            # 实盘交易 - 这里需要集成实际交易所API
            logger.warning("⚠️ 实盘交易功能尚未实现，使用模拟模式")
            await self._simulate_real_order(order)

        self.active_orders[order_id] = order
        return order

    async def _execute_sell_order(self, execution: ArbitrageExecution) -> Order:
        """执行卖出订单"""
        order_id = str(uuid.uuid4())

        order = Order(
            id=order_id,
            opportunity_id=execution.id,
            exchange=execution.sell_exchange,
            type=OrderType.SELL,
            symbol=f"{execution.crypto}/USDT",
            amount=execution.amount,
            price=execution.sell_price,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        logger.info(f"📉 执行卖出订单: {execution.crypto} @ ${execution.sell_price} 数量: {execution.amount}")

        if self.mode == TradingMode.SIMULATION:
            # 模拟交易
            await asyncio.sleep(0.5)  # 模拟网络延迟
            order.status = OrderStatus.FILLED
            order.filled_amount = order.amount
            order.filled_price = order.price
            order.fee = order.amount * order.price * self.fee_rate
            order.updated_at = datetime.now()
            logger.info(f"✅ 模拟卖出订单完成: {execution.crypto}")

        elif self.mode == TradingMode.DRY_RUN:
            # 试运行模式
            order.status = OrderStatus.FILLED
            order.filled_amount = order.amount
            order.filled_price = order.price
            order.fee = order.amount * order.price * self.fee_rate
            order.updated_at = datetime.now()
            logger.info(f"🧪 试运行卖出订单: {execution.crypto}")

        else:
            # 实盘交易
            logger.warning("⚠️ 实盘交易功能尚未实现，使用模拟模式")
            await self._simulate_real_order(order)

        self.active_orders[order_id] = order
        return order

    async def _simulate_real_order(self, order: Order):
        """模拟真实订单执行"""
        # 这里可以集成真实的交易所API
        await asyncio.sleep(1.0)  # 模拟真实网络延迟

        # 90%成功率模拟
        import random
        if random.random() > 0.1:
            order.status = OrderStatus.FILLED
            order.filled_amount = order.amount * random.uniform(0.98, 1.0)  # 模拟部分成交
            order.filled_price = order.price * random.uniform(0.999, 1.001)  # 模拟滑点
            order.fee = order.filled_amount * order.filled_price * self.fee_rate
        else:
            order.status = OrderStatus.FAILED
            order.error_message = "模拟交易所API错误"

        order.updated_at = datetime.now()

    def _validate_opportunity(self, opportunity: Dict) -> Dict:
        """验证套利机会"""
        try:
            profit_rate = opportunity.get('diff_rate', 0)
            crypto = opportunity.get('crypto', '')

            # 检查利润率
            if profit_rate < self.min_profit_threshold:
                return {
                    'valid': False,
                    'reason': f"利润率 {profit_rate}% 低于最小阈值 {self.min_profit_threshold}%"
                }

            # 检查加密货币
            if crypto not in ['BTC', 'ETH', 'SOL']:
                return {
                    'valid': False,
                    'reason': f"不支持的加密货币: {crypto}"
                }

            # 检查价格合理性
            buy_price = opportunity.get('buy_price', 0)
            sell_price = opportunity.get('sell_price', 0)

            if buy_price <= 0 or sell_price <= 0:
                return {
                    'valid': False,
                    'reason': "价格数据异常"
                }

            if sell_price <= buy_price:
                return {
                    'valid': False,
                    'reason': "卖出价格低于买入价格"
                }

            return {'valid': True, 'reason': ''}

        except Exception as e:
            return {
                'valid': False,
                'reason': f"验证异常: {str(e)}"
            }

    def _calculate_position_size(self, opportunity: Dict) -> float:
        """计算头寸大小"""
        # 基于利润率和风险计算合适的头寸大小
        profit_rate = opportunity.get('diff_rate', 0)
        crypto = opportunity.get('crypto', '')

        # 基础头寸
        base_size = 100  # USD

        # 根据利润率调整头寸
        if profit_rate > 0.5:
            base_size = min(self.max_position_size, 500)
        elif profit_rate > 0.3:
            base_size = min(self.max_position_size, 300)
        elif profit_rate > 0.2:
            base_size = min(self.max_position_size, 200)

        # 根据加密货币调整
        if crypto == 'BTC':
            base_size = min(base_size, 1000)
        elif crypto == 'ETH':
            base_size = min(base_size, 2000)

        return base_size

    def _calculate_actual_profit(self, execution: ArbitrageExecution) -> float:
        """计算实际利润"""
        if not execution.buy_order or not execution.sell_order:
            return 0.0

        buy_cost = execution.buy_order.filled_amount * execution.buy_order.filled_price
        buy_cost += execution.buy_order.fee

        sell_revenue = execution.sell_order.filled_amount * execution.sell_order.filled_price
        sell_revenue -= execution.sell_order.fee

        return sell_revenue - buy_cost

    def _create_failed_execution(self, execution_id: str, opportunity: Dict, reason: str) -> ArbitrageExecution:
        """创建失败的执行记录"""
        return ArbitrageExecution(
            id=execution_id,
            crypto=opportunity.get('crypto', ''),
            buy_exchange=opportunity.get('buy_exchange', ''),
            sell_exchange=opportunity.get('sell_exchange', ''),
            buy_price=opportunity.get('buy_price', 0),
            sell_price=opportunity.get('sell_price', 0),
            amount=0,
            expected_profit=opportunity.get('potential_profit', 0),
            actual_profit=0,
            status="failed",
            created_at=datetime.now(),
            completed_at=datetime.now(),
            notes=reason
        )

    def get_active_orders(self) -> List[Dict]:
        """获取活跃订单"""
        return [order.to_dict() for order in self.active_orders.values()]

    def get_execution_history(self, limit: int = 50) -> List[Dict]:
        """获取执行历史"""
        return [execution.to_dict() for execution in self.execution_history[-limit:]]

    def get_profit_statistics(self) -> Dict:
        """获取收益统计"""
        completed_executions = [e for e in self.execution_history if e.status in ['completed', 'partial_completed']]

        if not completed_executions:
            return {
                'total_executions': 0,
                'total_profit': 0.0,
                'avg_profit': 0.0,
                'success_rate': 0.0,
                'profit_rate': 0.0
            }

        total_profit = sum(e.actual_profit for e in completed_executions)
        successful_executions = [e for e in completed_executions if e.actual_profit > 0]

        total_invested = sum(e.amount * e.buy_price for e in completed_executions)

        return {
            'total_executions': len(completed_executions),
            'total_profit': total_profit,
            'avg_profit': total_profit / len(completed_executions) if completed_executions else 0,
            'success_rate': len(successful_executions) / len(completed_executions) if completed_executions else 0,
            'profit_rate': (total_profit / total_invested * 100) if total_invested > 0 else 0,
            'best_trade': max(completed_executions, key=lambda x: x.actual_profit).actual_profit if completed_executions else 0,
            'worst_trade': min(completed_executions, key=lambda x: x.actual_profit).actual_profit if completed_executions else 0
        }

    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        if order_id not in self.active_orders:
            return False

        order = self.active_orders[order_id]

        if self.mode == TradingMode.SIMULATION:
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.now()
            logger.info(f"❌ 模拟取消订单: {order_id}")
            return True
        else:
            # 实盘取消逻辑
            logger.warning("⚠️ 实盘订单取消功能尚未实现")
            return False

    def set_mode(self, mode: TradingMode):
        """设置交易模式"""
        self.mode = mode
        logger.info(f"🔄 交易模式已切换为: {mode.value}")


# 全局交易引擎实例
trading_engine = TradingEngine(TradingMode.SIMULATION)


if __name__ == "__main__":
    # 测试代码
    async def test_trading_engine():
        # 创建测试套利机会
        test_opportunity = {
            'crypto': 'BTC',
            'buy_exchange': 'binance',
            'sell_exchange': 'coinbase',
            'buy_price': 50000,
            'sell_price': 50200,
            'diff_rate': 0.4,
            'potential_profit': 200
        }

        # 执行套利
        execution = await trading_engine.execute_arbitrage(test_opportunity)
        print("执行结果:")
        print(f"ID: {execution.id}")
        print(f"状态: {execution.status}")
        print(f"实际利润: ${execution.actual_profit}")

        # 查看统计
        stats = trading_engine.get_profit_statistics()
        print("\n收益统计:")
        print(stats)

    # 运行测试
    asyncio.run(test_trading_engine())