/**
 * 优化版前端JavaScript
 * 性能优化重点：
 * 1. 请求合并和节流
 * 2. 智能缓存
 * 3. 批量数据获取
 * 4. 防抖和节流
 * 5. 错误重试机制
 */

class OptimizedFrontend {
    constructor() {
        this.cache = new Map();
        this.requestQueue = new Map();
        this.lastUpdate = {};
        this.updateIntervals = {};
        this.retryAttempts = new Map();
        this.maxRetries = 3;

        // 配置
        this.config = {
            updateInterval: 5000,        // 基础更新间隔
            fastUpdateInterval: 2000,    // 快速更新间隔
            slowUpdateInterval: 10000,   // 慢速更新间隔
            cacheTimeout: 30000,         // 缓存超时
            batchSize: 10,               // 批量请求大小
            debounceDelay: 300,          // 防抖延迟
            throttleDelay: 1000          // 节流延迟
        };

        this.init();
    }

    init() {
        console.log('🚀 优化版前端初始化...');
        this.setupOptimizedDataFetching();
        this.setupSmartCaching();
        this.setupErrorHandling();
        this.startOptimizedUpdates();

        console.log('✅ 优化版前端初始化完成');
    }

    // 生成缓存键
    generateCacheKey(endpoint, params = {}) {
        return `${endpoint}_${JSON.stringify(params)}`;
    }

    // 智能缓存检查
    getCachedData(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.config.cacheTimeout) {
            console.debug(`🎯 缓存命中: ${key}`);
            return cached.data;
        }
        return null;
    }

    // 设置缓存
    setCachedData(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });

        // 清理过期缓存
        this.cleanExpiredCache();
    }

    // 清理过期缓存
    cleanExpiredCache() {
        const now = Date.now();
        for (const [key, value] of this.cache.entries()) {
            if (now - value.timestamp > this.config.cacheTimeout * 2) {
                this.cache.delete(key);
            }
        }
    }

    // 防抖函数
    debounce(func, delay) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // 节流函数
    throttle(func, delay) {
        let lastCall = 0;
        return (...args) => {
            const now = Date.now();
            if (now - lastCall >= delay) {
                lastCall = now;
                return func.apply(this, args);
            }
        };
    }

    // 优化的API请求
    async optimizedRequest(endpoint, options = {}) {
        const cacheKey = this.generateCacheKey(endpoint, options.params);

        // 检查缓存
        const cachedData = this.getCachedData(cacheKey);
        if (cachedData && !options.forceRefresh) {
            return cachedData;
        }

        // 检查是否已有相同请求在进行中
        if (this.requestQueue.has(cacheKey)) {
            console.debug(`⏳ 请求去重: ${endpoint}`);
            return this.requestQueue.get(cacheKey);
        }

        // 创建请求Promise
        const requestPromise = this.executeRequest(endpoint, options, cacheKey);
        this.requestQueue.set(cacheKey, requestPromise);

        try {
            const result = await requestPromise;
            return result;
        } finally {
            this.requestQueue.delete(cacheKey);
        }
    }

    // 执行HTTP请求
    async executeRequest(endpoint, options, cacheKey) {
        const maxRetries = options.maxRetries || this.maxRetries;
        const retryKey = `${endpoint}_${cacheKey}`;
        let attempt = this.retryAttempts.get(retryKey) || 0;

        try {
            const url = options.fullUrl || `/api/v2/${endpoint}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // 缓存成功的响应
            if (data && !data.error) {
                this.setCachedData(cacheKey, data);
                this.retryAttempts.delete(retryKey); // 清除重试计数
            }

            return data;

        } catch (error) {
            console.error(`❌ 请求失败: ${endpoint}`, error);

            // 重试逻辑
            if (attempt < maxRetries) {
                attempt++;
                this.retryAttempts.set(retryKey, attempt);

                const delay = Math.pow(2, attempt) * 1000; // 指数退避
                console.log(`🔄 重试 ${endpoint} (${attempt}/${maxRetries}) - ${delay}ms后`);

                await this.sleep(delay);
                return this.executeRequest(endpoint, options, cacheKey);
            } else {
                this.retryAttempts.delete(retryKey);
                throw error;
            }
        }
    }

    // 睡眠函数
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // 批量数据获取 - 一次请求获取所有数据
    async fetchDashboardData(forceRefresh = false) {
        try {
            const data = await this.optimizedRequest('dashboard', {
                forceRefresh,
                maxRetries: 2
            });

            if (data && data.data) {
                const dashboardData = data.data;

                // 更新各个组件
                this.updatePrices(dashboardData.prices || {});
                this.updateOpportunities(dashboardData.opportunities || {});
                this.updateStats(dashboardData.stats || {});
                this.updatePerformanceInfo(dashboardData.performance || {});

                // 获取交易统计数据
                this.fetchTradingStatistics();

                console.log(`📊 仪表板数据更新完成 (来源: ${data.data_source || 'API'})`);
                return dashboardData;
            }

            return null;
        } catch (error) {
            console.error('仪表板数据获取失败:', error);
            this.showErrorMessage('无法获取最新数据，请检查网络连接');
            return null;
        }
    }

    // 设置优化的数据获取
    setupOptimizedDataFetching() {
        // 使用仪表板API替代多个独立API
        this.fetchDashboardDataDebounced = this.debounce(() => {
            this.fetchDashboardData();
        }, this.config.debounceDelay);

        this.fetchDashboardDataThrottled = this.throttle(() => {
            this.fetchDashboardData();
        }, this.config.throttleDelay);
    }

    // 更新价格数据
    updatePrices(prices) {
        if (!prices || Object.keys(prices).length === 0) return;

        // 更新价格显示
        Object.entries(prices).forEach(([crypto, exchangePrices]) => {
            if (exchangePrices && typeof exchangePrices === 'object') {
                const priceValues = Object.values(exchangePrices);
                if (priceValues.length > 0) {
                    const avgPrice = priceValues.reduce((a, b) => a + b, 0) / priceValues.length;
                    this.updatePriceDisplay(crypto, avgPrice, exchangePrices);
                }
            }
        });
    }

    // 更新价格显示
    updatePriceDisplay(crypto, avgPrice, exchangePrices) {
        const priceElements = document.querySelectorAll(`[data-crypto="${crypto}"]`);
        priceElements.forEach(element => {
            if (element.classList.contains('price-display')) {
                element.textContent = `$${avgPrice.toFixed(2)}`;
            }
        });
    }

    // 更新套利机会
    updateOpportunities(opportunities) {
        const spotOpportunities = opportunities.spot_arbitrage || [];

        // 更新机会列表
        this.updateOpportunitiesList(spotOpportunities);

        // 更新总收益
        this.updateTotalProfit(spotOpportunities);

        // 更新统计卡片
        this.updateStatCards(spotOpportunities);
    }

    // 更新机会列表
    updateOpportunitiesList(opportunities) {
        const listElement = document.getElementById('opportunitiesList');
        const tradingElement = document.getElementById('tradingOpportunities');

        if (!opportunities || opportunities.length === 0) {
            const emptyHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🔍</div>
                    <div>暂无套利机会</div>
                </div>
            `;

            if (listElement) listElement.innerHTML = emptyHTML;
            if (tradingElement) tradingElement.innerHTML = emptyHTML;
            return;
        }

        // 生成机会HTML
        const opportunitiesHTML = opportunities.map(opp => {
            const profitRate = parseFloat(opp.diff_rate || 0);
            const potentialProfit = parseFloat(opp.potential_profit || 0);
            const riskLevel = profitRate > 2 ? 'high' : profitRate > 1 ? 'medium' : 'low';

            return `
                <div class="opportunity-card ${riskLevel}">
                    <div class="opportunity-header">
                        <span>${opp.crypto || '交易对'}</span>
                        <div class="opportunity-profit">
                            ↑ ${profitRate.toFixed(2)}%
                        </div>
                    </div>
                    <div class="opportunity-details">
                        <div>💵 买入: ${opp.buy_exchange || '--'} @ $${(opp.buy_price || 0).toFixed(2)}</div>
                        <div>💰 卖出: ${opp.sell_exchange || '--'} @ $${(opp.sell_price || 0).toFixed(2)}</div>
                        <div>🎯 利润: $${potentialProfit.toFixed(2)}</div>
                        <div>⏰ ${new Date(opp.timestamp).toLocaleTimeString()}</div>
                    </div>
                    ${opp.crypto && opp.buy_exchange && opp.sell_exchange ? `
                        <div class="opportunity-actions">
                            <button
                                class="execute-btn"
                                onclick="executeTrade(${JSON.stringify(opp).replace(/"/g, '&quot;')})"
                                title="执行套利交易"
                            >
                                🎯 执行套利
                            </button>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');

        if (listElement) listElement.innerHTML = opportunitiesHTML;

        // 交易面板只显示前6个最佳机会
        if (tradingElement) {
            const topOpportunities = opportunities
                .sort((a, b) => parseFloat(b.diff_rate || 0) - parseFloat(a.diff_rate || 0))
                .slice(0, 6);

            const tradingHTML = topOpportunities.map(opp => {
                const profitRate = parseFloat(opp.diff_rate || 0);
                const potentialProfit = parseFloat(opp.potential_profit || 0);

                return `
                    <div class="opportunity-card">
                        <div class="opportunity-header">
                            <span class="crypto-symbol">${opp.crypto}</span>
                            <div class="opportunity-profit">
                                ↑ ${profitRate.toFixed(3)}%
                            </div>
                        </div>
                        <div class="opportunity-details">
                            <div>💵 买入: ${opp.buy_exchange} @ $${opp.buy_price?.toFixed(2) || '0.00'}</div>
                            <div>💰 卖出: ${opp.sell_exchange} @ $${opp.sell_price?.toFixed(2) || '0.00'}</div>
                            <div>🎯 收益: $${potentialProfit.toFixed(2)}</div>
                        </div>
                        <button class="execute-btn" onclick="executeTrade(${JSON.stringify(opp).replace(/"/g, '&quot;')})">
                            🎯 执行
                        </button>
                    </div>
                `;
            }).join('');

            tradingElement.innerHTML = tradingHTML;
        }
    }

    // 更新总收益
    updateTotalProfit(opportunities) {
        const totalProfitElement = document.getElementById('totalProfit');
        if (!totalProfitElement || !opportunities) return;

        const totalProfit = opportunities.reduce((sum, opp) => {
            return sum + parseFloat(opp.potential_profit || 0);
        }, 0);

        totalProfitElement.textContent = `$${totalProfit.toFixed(2)}`;
        console.log(`💰 总潜在收益更新: $${totalProfit.toFixed(2)} (来自 ${opportunities.length} 个机会)`);
    }

    // 更新统计卡片
    updateStatCards(opportunities) {
        const totalOpportunitiesElement = document.getElementById('totalOpportunities');
        if (totalOpportunitiesElement) {
            totalOpportunitiesElement.textContent = opportunities.length;
        }
    }

    // 更新统计信息
    updateStats(stats) {
        if (!stats) return;

        // 更新各种统计显示
        Object.entries(stats).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = typeof value === 'number' ? value.toFixed(2) : value;
            }
        });
    }

    // 更新性能信息
    updatePerformanceInfo(performance) {
        if (!performance) return;

        // 更新性能指示器
        const performanceElement = document.getElementById('performanceIndicator');
        if (performanceElement) {
            const executionTime = performance.execution_time || 0;
            let status = 'good';
            let color = '#10b981';

            if (executionTime > 2000) {
                status = 'slow';
                color = '#ef4444';
            } else if (executionTime > 1000) {
                status = 'moderate';
                color = '#f59e0b';
            }

            performanceElement.textContent = `${status} (${executionTime}ms)`;
            performanceElement.style.color = color;
        }
    }

    // 设置智能缓存
    setupSmartCaching() {
        // 页面可见性变化时的处理
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
                console.log('⏸️ 页面隐藏，暂停更新');
            } else {
                this.resumeUpdates();
                console.log('▶️ 页面显示，恢复更新');
                this.fetchDashboardData(true); // 强制刷新
            }
        });

        // 网络状态变化处理
        window.addEventListener('online', () => {
            console.log('🌐 网络连接恢复');
            this.fetchDashboardData(true);
        });

        window.addEventListener('offline', () => {
            console.log('📡 网络连接断开');
            this.showErrorMessage('网络连接断开，显示缓存数据');
        });
    }

    // 设置错误处理
    setupErrorHandling() {
        // 全局错误处理
        window.addEventListener('error', (event) => {
            console.error('全局错误:', event.error);
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('未处理的Promise拒绝:', event.reason);
        });
    }

    // 开始优化更新
    startOptimizedUpdates() {
        // 初始数据加载
        this.fetchDashboardData();

        // 设置更新间隔
        this.updateIntervals.main = setInterval(() => {
            this.fetchDashboardDataThrottled();
        }, this.config.updateInterval);

        // 设置页面可见性检测
        this.setupVisibilityDetection();

        console.log('⚡ 优化更新循环已启动');
    }

    // 设置页面可见性检测
    setupVisibilityDetection() {
        let lastVisibilityTime = Date.now();

        const checkVisibility = () => {
            if (!document.hidden && Date.now() - lastVisibilityTime > this.config.updateInterval) {
                this.fetchDashboardData();
                lastVisibilityTime = Date.now();
            }
        };

        // 页面获得焦点时检查
        window.addEventListener('focus', checkVisibility);

        // 定期检查（处理标签页切换）
        setInterval(checkVisibility, this.config.updateInterval);
    }

    // 暂停更新
    pauseUpdates() {
        Object.values(this.updateIntervals).forEach(interval => {
            clearInterval(interval);
        });
        this.updateIntervals = {};
    }

    // 恢复更新
    resumeUpdates() {
        if (Object.keys(this.updateIntervals).length === 0) {
            this.startOptimizedUpdates();
        }
    }

    // 显示错误消息
    showErrorMessage(message) {
        const errorElement = document.getElementById('errorMessage');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';

            setTimeout(() => {
                errorElement.style.display = 'none';
            }, 5000);
        }
    }

    // 获取交易统计数据
    async fetchTradingStatistics() {
        try {
            // 直接调用正确的API端点，不通过optimizedRequest
            const response = await fetch('/api/trading/statistics', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data && data.statistics) {
                this.updateTradingStatistics(data.statistics);
                console.log('📈 交易统计数据更新完成');
            } else {
                console.warn('统计数据格式异常:', data);
            }
        } catch (error) {
            console.error('获取交易统计数据失败:', error);
        }
    }

    // 更新交易统计数据
    updateTradingStatistics(stats) {
        try {
            // 更新总收益
            const totalProfitElement = document.getElementById('tradingTotalProfit');
            if (totalProfitElement) {
                totalProfitElement.textContent = `$${stats.total_profit.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })}`;
            }

            // 更新成功率
            const successRateElement = document.getElementById('successRate');
            if (successRateElement) {
                const successRate = (stats.success_rate * 100).toFixed(1);
                successRateElement.textContent = `${successRate}%`;
            }

            // 更新执行次数
            const totalExecutionsElement = document.getElementById('totalExecutions');
            if (totalExecutionsElement) {
                totalExecutionsElement.textContent = stats.total_executions.toString();
            }

            console.log(`📊 交易统计更新: 收益 $${stats.total_profit.toFixed(2)}, 成功率 ${(stats.success_rate * 100).toFixed(1)}%, 执行 ${stats.total_executions} 次`);
        } catch (error) {
            console.error('更新交易统计数据失败:', error);
        }
    }

    // 手动刷新数据
    refreshData() {
        console.log('🔄 手动刷新数据');
        this.fetchDashboardData(true);
    }

    // 获取性能统计
    getPerformanceStats() {
        return {
            cacheSize: this.cache.size,
            activeRequests: this.requestQueue.size,
            retryAttempts: this.retryAttempts.size,
            lastUpdate: this.lastUpdate
        };
    }
}

// 全局实例
window.optimizedFrontend = new OptimizedFrontend();

// 向后兼容的全局函数
window.refreshData = () => window.optimizedFrontend.refreshData();

// 页面加载完成后的优化
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 页面加载完成，启动优化版本');

    // 预加载关键数据
    setTimeout(() => {
        window.optimizedFrontend.fetchDashboardData();
    }, 100);
});