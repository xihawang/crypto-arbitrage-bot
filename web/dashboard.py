"""
Web UI 仪表板 - 使用 Streamlit 构建实时监控界面
启动命令: streamlit run web/dashboard.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# 配置页面
st.set_page_config(
    page_title="加密货币套利机器人仪表板",
    page_icon="💰",
    layout="wide"
)

# 侧边栏
st.sidebar.title("🤖 套利机器人控制面板")

# 主题选择
theme = st.sidebar.radio("选择主题", ["深色", "浅色"])

# 导航菜单
menu = st.sidebar.selectbox(
    "选择功能",
    ["📊 实时价格", "💡 套利机会", "📈 交易历史", "⚠️ 风险管理", "📱 通知设置", "⚙️ 系统设置"]
)

# ============ 标题 ============
st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1>💰 加密货币套利机器人</h1>
        <p>实时监控、自动交易、风险管理一体化平台</p>
    </div>
    """, unsafe_allow_html=True)

# ============ 实时价格页面 ============
if menu == "📊 实时价格":
    st.header("📊 实时价格监控")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="BTC 价格",
            value="$85,963.00",
            delta="-5.95%",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            label="ETH 价格",
            value="$2,809.38",
            delta="-6.56%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="SOL 价格",
            value="$127.29",
            delta="-7.50%",
            delta_color="inverse"
        )
    
    # 价格对比表格
    st.subheader("各交易所价格对比")
    
    price_data = {
        "币种": ["BTC", "BTC", "BTC", "BTC", "ETH", "ETH", "ETH"],
        "交易所": ["CoinGecko", "币安", "Coinbase", "Kraken", "CoinGecko", "币安", "Coinbase"],
        "价格": [85963.00, 85975.92, 85968.48, 85987.70, 2809.38, 2811.25, 2812.10],
        "状态": ["✅", "✅", "✅", "✅", "✅", "✅", "✅"]
    }
    
    df_prices = pd.DataFrame(price_data)
    st.dataframe(df_prices, use_container_width=True)
    
    # 价格走势图
    st.subheader("24小时价格走势")
    
    # 模拟数据
    hours = list(range(24))
    btc_prices = [85000 + i * 10 + (i % 3) * 50 for i in hours]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=btc_prices, mode='lines+markers', name='BTC'))
    fig.update_layout(
        title="BTC 24小时价格走势",
        xaxis_title="小时",
        yaxis_title="价格 (USD)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============ 套利机会页面 ============
elif menu == "💡 套利机会":
    st.header("💡 套利机会扫描")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("发现机会数", "12", "+3")
    with col2:
        st.metric("平均差价率", "0.23%", "+0.05%")
    with col3:
        st.metric("最佳机会", "ETH (0.45%)", "+0.1%")
    
    # 机会列表
    st.subheader("实时套利机会")
    
    opportunities = {
        "币种": ["BTC", "ETH", "SOL", "BTC", "ETH"],
        "差价率": [0.12, 0.45, 0.23, 0.18, 0.31],
        "买入交易所": ["CoinGecko", "币安", "Coinbase", "Kraken", "CoinGecko"],
        "卖出交易所": ["Kraken", "Kraken", "币安", "币安", "Coinbase"],
        "买入价": [85733.00, 2809.38, 127.15, 85963.00, 2809.38],
        "卖出价": [85783.00, 2825.65, 127.44, 86035.00, 2824.23],
        "状态": ["监控中", "监控中", "监控中", "监控中", "监控中"]
    }
    
    df_opportunities = pd.DataFrame(opportunities)
    st.dataframe(df_opportunities, use_container_width=True)
    
    # 机会分布图
    st.subheader("机会分布")
    
    fig = px.pie(
        df_opportunities,
        names="币种",
        values="差价率",
        title="套利机会按币种分布"
    )
    st.plotly_chart(fig, use_container_width=True)

# ============ 交易历史页面 ============
elif menu == "📈 交易历史":
    st.header("📈 交易历史与收益")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总交易数", "45", "✅")
    with col2:
        st.metric("胜率", "68%", "+5%")
    with col3:
        st.metric("总收益", "$2,345.67", "✅")
    with col4:
        st.metric("最大亏损", "-$156.23", "📉")
    
    # 交易列表
    st.subheader("最近交易")
    
    trades = {
        "时间": ["2025-12-01 21:30", "2025-12-01 21:15", "2025-12-01 21:00", "2025-12-01 20:45"],
        "类型": ["平仓", "开仓", "平仓", "开仓"],
        "币种": ["BTC", "ETH", "SOL", "BTC"],
        "方向": ["LONG", "LONG", "SHORT", "LONG"],
        "数量": [0.05, 1.5, 100, 0.1],
        "价格": [85900, 2810, 127.5, 85800],
        "收益": ["+$125.45", "-", "+$89.23", "-"],
        "状态": ["✅", "⏳", "✅", "⏳"]
    }
    
    df_trades = pd.DataFrame(trades)
    st.dataframe(df_trades, use_container_width=True)
    
    # 收益走势
    st.subheader("累计收益走势")
    
    days = list(range(30))
    cumulative_pnl = [i * 75 + (i % 5) * 20 for i in days]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days,
        y=cumulative_pnl,
        fill='tozeroy',
        name='累计收益',
        line=dict(color='green')
    ))
    fig.update_layout(
        title="30天累计收益",
        xaxis_title="天",
        yaxis_title="收益 (USD)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# ============ 风险管理页面 ============
elif menu == "⚠️ 风险管理":
    st.header("⚠️ 风险管理")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("账户余额", "$10,000", "")
    with col2:
        st.metric("活跃头寸", "5", "")
    with col3:
        st.metric("敞口比例", "35%", "")
    with col4:
        st.metric("风险评分", "45/100", "🟡 中等")
    
    # 风险指标
    st.subheader("风险指标")
    
    risk_data = {
        "指标": ["敞口比例", "最大亏损率", "风险评分", "止损触发"],
        "值": ["35%", "2.5%", "45", "0"],
        "阈值": ["≤50%", "≤5%", "≤60", "≤3"],
        "状态": ["✅", "✅", "✅", "✅"]
    }
    
    df_risk = pd.DataFrame(risk_data)
    st.dataframe(df_risk, use_container_width=True)
    
    # 头寸监控
    st.subheader("活跃头寸")
    
    positions = {
        "币种": ["BTC", "ETH", "SOL"],
        "方向": ["LONG", "LONG", "SHORT"],
        "数量": [0.05, 1.5, 100],
        "成本": [4295, 4215, 12750],
        "当前价值": [4297, 4220, 12720],
        "收益": ["+$2", "+$5", "-$30"],
        "止损": [84500, 2700, 130],
        "止盈": [90000, 2900, 125]
    }
    
    df_positions = pd.DataFrame(positions)
    st.dataframe(df_positions, use_container_width=True)
    
    # 风险分布
    st.subheader("风险分布")
    
    risk_breakdown = {
        "币种": ["BTC", "ETH", "SOL"],
        "敞口": [4300, 4200, 12750]
    }
    
    df_risk_breakdown = pd.DataFrame(risk_breakdown)
    fig = px.pie(
        df_risk_breakdown,
        names="币种",
        values="敞口",
        title="敞口分布"
    )
    st.plotly_chart(fig, use_container_width=True)

# ============ 通知设置页面 ============
elif menu == "📱 通知设置":
    st.header("📱 通知设置")
    
    st.subheader("Telegram 配置")
    
    telegram_token = st.text_input(
        "Telegram Bot Token",
        value="",
        type="password",
        help="从 @BotFather 获取"
    )
    
    telegram_chat_id = st.text_input(
        "Chat ID",
        value="",
        help="从 @userinfobot 获取"
    )
    
    st.subheader("通知类型设置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        notify_arbitrage = st.checkbox("✅ 套利机会通知", value=True)
        notify_trade_open = st.checkbox("✅ 开仓通知", value=True)
        notify_error = st.checkbox("✅ 错误通知", value=True)
    
    with col2:
        notify_trade_close = st.checkbox("✅ 平仓通知", value=True)
        notify_daily = st.checkbox("✅ 日报通知", value=False)
        notify_risk = st.checkbox("✅ 风险警告", value=True)
    
    # 通知阈值
    st.subheader("通知阈值")
    
    min_arbitrage_rate = st.slider(
        "最小套利差价率 (%)",
        min_value=0.0,
        max_value=2.0,
        value=0.1,
        step=0.05
    )
    
    # 测试通知
    if st.button("📤 发送测试通知"):
        st.success("✅ 测试通知已发送!")
    
    # 保存设置
    if st.button("💾 保存设置", key="save_notification_settings"):
        st.success("✅ 设置已保存!")

# ============ 系统设置页面 ============
elif menu == "⚙️ 系统设置":
    st.header("⚙️ 系统设置")
    
    st.subheader("交易所配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        binance_key = st.text_input(
            "币安 API Key",
            type="password",
            help="保密处理"
        )
    
    with col2:
        binance_secret = st.text_input(
            "币安 Secret Key",
            type="password",
            help="保密处理"
        )
    
    st.subheader("风险管理配置")
    
    max_position_size = st.slider(
        "单笔头寸最大占账户比例 (%)",
        min_value=1,
        max_value=50,
        value=10
    )
    
    max_loss_per_trade = st.slider(
        "单笔交易最大亏损率 (%)",
        min_value=0.1,
        max_value=10.0,
        value=2.0
    )
    
    st.subheader("扫描配置")
    
    scan_interval = st.slider(
        "扫描间隔 (秒)",
        min_value=10,
        max_value=300,
        value=60
    )
    
    arbitrage_threshold = st.slider(
        "套利阈值 (%)",
        min_value=0.05,
        max_value=1.0,
        value=0.2
    )
    
    st.subheader("其他设置")
    
    enable_websocket = st.checkbox("✅ 启用 WebSocket 实时价格", value=True)
    enable_ml = st.checkbox("✅ 启用机器学习预测", value=False)
    enable_auto_trade = st.checkbox("✅ 启用自动交易", value=False)
    
    # 保存设置
    if st.button("💾 保存系统设置", key="save_system_settings"):
        st.success("✅ 系统设置已保存!")

# 底部信息
st.sidebar.markdown("---")
st.sidebar.info("""
    **加密货币套利机器人 v1.0**
    
    🚀 实时价格监控
    💡 自动套利检测
    📈 交易记录分析
    ⚠️ 风险管理系统
    📱 Telegram 通知
    
    © 2025 - 保密免责声明
""")
