"""
风险管理系统
实现头寸管理、止损/止盈、风险评分等功能
"""

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class Position:
    """头寸信息"""
    crypto: str
    exchange: str
    side: str  # "long" 或 "short"
    quantity: float
    entry_price: float
    current_price: float
    stop_loss: float  # 止损价格
    take_profit: float  # 止盈价格
    opened_at: datetime
    
    @property
    def pnl(self) -> float:
        """计算未实现收益/亏损"""
        if self.side == "long":
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity
    
    @property
    def pnl_rate(self) -> float:
        """计算收益率 (%)"""
        return (self.pnl / (self.entry_price * self.quantity)) * 100
    
    @property
    def risk_exposure(self) -> float:
        """风险敞口"""
        return abs(self.quantity * self.entry_price)


class RiskManager:
    """风险管理器"""
    
    def __init__(self, account_balance: float, max_position_size: float = 0.1,
                 max_loss_per_trade: float = 0.02):
        """初始化风险管理器
        
        Args:
            account_balance: 账户余额
            max_position_size: 单笔头寸最大占账户的比例 (默认 10%)
            max_loss_per_trade: 单笔交易最大亏损率 (默认 2%)
        """
        self.account_balance = account_balance
        self.max_position_size = max_position_size
        self.max_loss_per_trade = max_loss_per_trade
        self.positions: Dict[str, List[Position]] = {}
        self.closed_positions = []
        self.total_pnl = 0.0
    
    # ============ 头寸管理 ============
    
    def open_position(self, crypto: str, exchange: str, side: str, 
                     quantity: float, entry_price: float,
                     stop_loss: float, take_profit: float) -> Optional[Position]:
        """开启新头寸
        
        Args:
            crypto: 加密货币
            exchange: 交易所
            side: 方向 (long/short)
            quantity: 数量
            entry_price: 入场价格
            stop_loss: 止损价格
            take_profit: 止盈价格
            
        Returns:
            头寸对象
        """
        # 检查风险
        position_size = quantity * entry_price
        position_rate = position_size / self.account_balance
        
        if position_rate > self.max_position_size:
            logger.warning(f"❌ 头寸大小超过限制 ({position_rate:.2%} > {self.max_position_size:.2%})")
            return None
        
        # 检查止损风险
        if side == "long":
            max_loss = (entry_price - stop_loss) * quantity
        else:
            max_loss = (stop_loss - entry_price) * quantity
        
        max_loss_rate = max_loss / self.account_balance
        
        if max_loss_rate > self.max_loss_per_trade:
            logger.warning(f"❌ 止损风险过高 ({max_loss_rate:.2%} > {self.max_loss_per_trade:.2%})")
            return None
        
        # 创建头寸
        position = Position(
            crypto=crypto,
            exchange=exchange,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            opened_at=datetime.now()
        )
        
        # 保存头寸
        key = f"{crypto}_{exchange}"
        if key not in self.positions:
            self.positions[key] = []
        
        self.positions[key].append(position)
        
        logger.info(f"✅ 开启 {side.upper()} 头寸: {crypto} x {quantity} @ {entry_price}")
        logger.info(f"   止损: {stop_loss}, 止盈: {take_profit}")
        logger.info(f"   风险敞口: ${position.risk_exposure:,.2f}")
        
        return position
    
    def close_position(self, position: Position, exit_price: float) -> Dict:
        """平仓
        
        Args:
            position: 头寸对象
            exit_price: 平仓价格
            
        Returns:
            平仓结果
        """
        # 更新价格
        position.current_price = exit_price
        
        pnl = position.pnl
        pnl_rate = position.pnl_rate
        
        # 移除头寸
        key = f"{position.crypto}_{position.exchange}"
        if key in self.positions and position in self.positions[key]:
            self.positions[key].remove(position)
        
        # 保存已平仓头寸
        self.closed_positions.append(position)
        self.total_pnl += pnl
        
        logger.info(f"✅ 平仓: {position.crypto} x {position.quantity} @ {exit_price}")
        logger.info(f"   收益/亏损: ${pnl:,.2f} ({pnl_rate:.2f}%)")
        
        return {
            "position": position,
            "pnl": pnl,
            "pnl_rate": pnl_rate,
            "exit_price": exit_price,
            "closed_at": datetime.now()
        }
    
    # ============ 价格更新 ============
    
    def update_position_price(self, crypto: str, exchange: str, 
                             current_price: float) -> List[Dict]:
        """更新头寸价格并检查止损/止盈
        
        Args:
            crypto: 加密货币
            exchange: 交易所
            current_price: 当前价格
            
        Returns:
            需要处理的头寸列表
        """
        key = f"{crypto}_{exchange}"
        if key not in self.positions:
            return []
        
        closed_positions = []
        
        for position in self.positions[key]:
            position.current_price = current_price
            
            # 检查止损
            should_close = False
            reason = ""
            
            if position.side == "long":
                if current_price <= position.stop_loss:
                    should_close = True
                    reason = "止损"
                elif current_price >= position.take_profit:
                    should_close = True
                    reason = "止盈"
            else:  # short
                if current_price >= position.stop_loss:
                    should_close = True
                    reason = "止损"
                elif current_price <= position.take_profit:
                    should_close = True
                    reason = "止盈"
            
            if should_close:
                result = self.close_position(position, current_price)
                result["reason"] = reason
                closed_positions.append(result)
                logger.warning(f"🚨 {reason} 触发: {crypto} @ {current_price}")
        
        return closed_positions
    
    # ============ 风险评估 ============
    
    def calculate_portfolio_risk(self) -> Dict:
        """计算投资组合风险指标
        
        Returns:
            风险指标
        """
        total_exposure = 0.0
        total_potential_loss = 0.0
        position_count = 0
        
        for positions_list in self.positions.values():
            for position in positions_list:
                total_exposure += position.risk_exposure
                position_count += 1
                
                # 计算最大可能亏损
                if position.side == "long":
                    max_loss = (position.entry_price - position.stop_loss) * position.quantity
                else:
                    max_loss = (position.stop_loss - position.entry_price) * position.quantity
                
                total_potential_loss += max_loss
        
        # 计算指标
        exposure_rate = total_exposure / self.account_balance if self.account_balance > 0 else 0
        max_loss_rate = total_potential_loss / self.account_balance if self.account_balance > 0 else 0
        risk_score = min(100, (exposure_rate + max_loss_rate) * 100)  # 0-100
        
        return {
            "total_exposure": total_exposure,
            "exposure_rate": exposure_rate,
            "total_potential_loss": total_potential_loss,
            "max_loss_rate": max_loss_rate,
            "position_count": position_count,
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score)
        }
    
    def _get_risk_level(self, risk_score: float) -> str:
        """获取风险等级
        
        Args:
            risk_score: 风险评分 (0-100)
            
        Returns:
            风险等级
        """
        if risk_score < 20:
            return "✅ 极低"
        elif risk_score < 40:
            return "🟢 低"
        elif risk_score < 60:
            return "🟡 中等"
        elif risk_score < 80:
            return "🟠 高"
        else:
            return "🔴 极高"
    
    def get_position_performance(self) -> Dict:
        """获取头寸性能统计"""
        all_positions = self.closed_positions
        
        if not all_positions:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_pnl": 0
            }
        
        winning_trades = [p for p in all_positions if p.pnl > 0]
        losing_trades = [p for p in all_positions if p.pnl < 0]
        
        total_pnl = sum(p.pnl for p in all_positions)
        avg_pnl = total_pnl / len(all_positions) if all_positions else 0
        win_rate = len(winning_trades) / len(all_positions) * 100 if all_positions else 0
        
        return {
            "total_trades": len(all_positions),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_pnl": avg_pnl
        }
    
    # ============ 显示信息 ============
    
    def display_positions(self) -> None:
        """显示所有活跃头寸"""
        if not any(self.positions.values()):
            logger.info("📋 当前无活跃头寸")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 活跃头寸")
        print(f"{'='*80}\n")
        
        print(f"{'币种':<6} {'方向':<6} {'数量':<12} {'入场价':<12} {'当前价':<12} {'P&L':<12} {'P&L%':<8}")
        print("-" * 80)
        
        for positions_list in self.positions.values():
            for pos in positions_list:
                pnl = pos.pnl
                pnl_rate = pos.pnl_rate
                pnl_str = f"${pnl:,.2f}"
                pnl_rate_str = f"{pnl_rate:.2f}%"
                
                print(f"{pos.crypto:<6} {pos.side.upper():<6} {pos.quantity:<12.4f} ${pos.entry_price:<11,.2f} ${pos.current_price:<11,.2f} {pnl_str:<12} {pnl_rate_str:<8}")
    
    def display_risk_analysis(self) -> None:
        """显示风险分析"""
        risk_analysis = self.calculate_portfolio_risk()
        perf = self.get_position_performance()
        
        print(f"\n{'='*60}")
        print(f"📈 风险分析")
        print(f"{'='*60}\n")
        
        print(f"  账户余额: ${self.account_balance:,.2f}")
        print(f"  总敞口: ${risk_analysis['total_exposure']:,.2f} ({risk_analysis['exposure_rate']:.2%})")
        print(f"  最大亏损: ${risk_analysis['total_potential_loss']:,.2f} ({risk_analysis['max_loss_rate']:.2%})")
        print(f"  风险评分: {risk_analysis['risk_score']:.1f} / 100")
        print(f"  风险等级: {risk_analysis['risk_level']}\n")
        
        print(f"  总交易: {perf['total_trades']}")
        print(f"  胜率: {perf['win_rate']:.2f}%")
        print(f"  总收益: ${perf['total_pnl']:,.2f}")
        print(f"  平均收益: ${perf['avg_pnl']:,.2f}\n")


# 全局风险管理器实例
risk_manager = RiskManager(account_balance=10000)  # 默认 10000 USD 账户
