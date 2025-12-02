"""
机器学习套利机会预测模块
使用历史价格数据训练模型预测套利机会
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ArbitragePredictor:
    """套利机会预测器"""
    
    def __init__(self, lookback_period: int = 60):
        """初始化预测器
        
        Args:
            lookback_period: 回看周期（分钟）
        """
        self.lookback_period = lookback_period
        self.scaler = StandardScaler()
        self.models = {}  # {crypto: model}
        self.price_history = {}  # {crypto: [(timestamp, prices_dict)]}
    
    def add_price_data(self, crypto: str, timestamp: datetime, prices: Dict[str, float]):
        """添加价格数据
        
        Args:
            crypto: 加密货币代码
            timestamp: 时间戳
            prices: {exchange_name: price} 格式的价格字典
        """
        if crypto not in self.price_history:
            self.price_history[crypto] = []
        
        self.price_history[crypto].append((timestamp, prices))
        
        # 仅保留最近 lookback_period 分钟的数据
        cutoff_time = datetime.now() - timedelta(minutes=self.lookback_period)
        self.price_history[crypto] = [
            (ts, p) for ts, p in self.price_history[crypto]
            if ts >= cutoff_time
        ]
    
    def _extract_features(self, crypto: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """提取特征
        
        Args:
            crypto: 加密货币代码
            
        Returns:
            (特征矩阵, 目标值)
        """
        if crypto not in self.price_history or len(self.price_history[crypto]) < 10:
            return None
        
        history = self.price_history[crypto]
        prices_list = [prices for _, prices in history]
        
        # 特征工程
        features = []
        targets = []
        
        for i in range(len(prices_list) - 1):
            current_prices = prices_list[i]
            next_prices = prices_list[i + 1]
            
            # 提取特征
            price_values = list(current_prices.values())
            
            if len(price_values) >= 2:
                price_mean = np.mean(price_values)
                price_std = np.std(price_values)
                price_max = np.max(price_values)
                price_min = np.min(price_values)
                price_diff_rate = (price_max - price_min) / price_min * 100
                
                feature_vector = [
                    price_mean,
                    price_std,
                    price_max,
                    price_min,
                    price_diff_rate,
                    len(price_values)
                ]
                
                # 目标值：下一时刻的价差率
                next_price_values = list(next_prices.values())
                next_price_max = np.max(next_price_values)
                next_price_min = np.min(next_price_values)
                next_diff_rate = (next_price_max - next_price_min) / next_price_min * 100
                
                features.append(feature_vector)
                targets.append(next_diff_rate)
        
        if features:
            return np.array(features), np.array(targets)
        
        return None
    
    def train_model(self, crypto: str, model_type: str = "rf") -> bool:
        """训练预测模型
        
        Args:
            crypto: 加密货币代码
            model_type: 模型类型 ("rf" 随机森林 或 "gb" 梯度提升)
            
        Returns:
            是否训练成功
        """
        try:
            result = self._extract_features(crypto)
            if result is None:
                logger.warning(f"❌ {crypto} 数据不足，无法训练模型")
                return False
            
            X, y = result
            
            # 数据标准化
            X_scaled = self.scaler.fit_transform(X)
            
            # 选择模型
            if model_type == "gb":
                model = GradientBoostingRegressor(n_estimators=50, learning_rate=0.1)
            else:
                model = RandomForestRegressor(n_estimators=50, max_depth=10)
            
            # 训练
            model.fit(X_scaled, y)
            self.models[crypto] = {
                "model": model,
                "scaler": self.scaler,
                "trained_at": datetime.now()
            }
            
            logger.info(f"✅ {crypto} 模型训练完成 (样本数: {len(X)})")
            return True
        
        except Exception as e:
            logger.error(f"❌ {crypto} 模型训练失败: {str(e)}")
            return False
    
    def predict_arbitrage_opportunity(self, crypto: str, current_prices: Dict[str, float]) -> Optional[Dict]:
        """预测套利机会
        
        Args:
            crypto: 加密货币代码
            current_prices: 当前价格字典
            
        Returns:
            预测结果
        """
        if crypto not in self.models:
            return None
        
        try:
            model_data = self.models[crypto]
            model = model_data["model"]
            scaler = model_data["scaler"]
            
            # 构建特征
            price_values = list(current_prices.values())
            
            if len(price_values) < 2:
                return None
            
            price_mean = np.mean(price_values)
            price_std = np.std(price_values)
            price_max = np.max(price_values)
            price_min = np.min(price_values)
            price_diff_rate = (price_max - price_min) / price_min * 100
            
            feature_vector = np.array([[
                price_mean,
                price_std,
                price_max,
                price_min,
                price_diff_rate,
                len(price_values)
            ]])
            
            # 预测
            X_scaled = scaler.transform(feature_vector)
            predicted_diff_rate = model.predict(X_scaled)[0]
            
            # 返回预测结果
            return {
                "crypto": crypto,
                "current_diff_rate": price_diff_rate,
                "predicted_diff_rate": predicted_diff_rate,
                "trend": "up" if predicted_diff_rate > price_diff_rate else "down",
                "confidence": abs(predicted_diff_rate - price_diff_rate) / (price_diff_rate + 0.001),
                "timestamp": datetime.now()
            }
        
        except Exception as e:
            logger.error(f"❌ {crypto} 预测失败: {str(e)}")
            return None
    
    def predict_batch(self, cryptos: List[str], current_prices_dict: Dict[str, Dict[str, float]]) -> List[Dict]:
        """批量预测
        
        Args:
            cryptos: 加密货币列表
            current_prices_dict: {crypto: {exchange: price}}
            
        Returns:
            预测结果列表
        """
        predictions = []
        
        for crypto in cryptos:
            if crypto in current_prices_dict:
                prediction = self.predict_arbitrage_opportunity(crypto, current_prices_dict[crypto])
                if prediction:
                    predictions.append(prediction)
        
        return predictions
    
    def get_model_performance(self, crypto: str) -> Optional[Dict]:
        """获取模型性能指标"""
        if crypto not in self.models:
            return None
        
        try:
            result = self._extract_features(crypto)
            if result is None:
                return None
            
            X, y = result
            model = self.models[crypto]["model"]
            scaler = self.models[crypto]["scaler"]
            
            X_scaled = scaler.transform(X)
            score = model.score(X_scaled, y)
            
            y_pred = model.predict(X_scaled)
            mse = np.mean((y - y_pred) ** 2)
            mae = np.mean(np.abs(y - y_pred))
            
            return {
                "crypto": crypto,
                "r2_score": score,
                "mse": mse,
                "mae": mae,
                "trained_at": self.models[crypto]["trained_at"]
            }
        
        except Exception as e:
            logger.error(f"❌ 获取模型性能失败: {str(e)}")
            return None


# 全局预测器实例
arbitrage_predictor = ArbitragePredictor()
