"""
SquirRL-Auditor: 区块链自私挖矿攻击分析系统
Streamlit Web 应用主入口 - 精致版
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 页面配置
st.set_page_config(
    page_title="SquirRL-Auditor",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# ================= 精致 CSS 样式 =================
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Playfair+Display:wght@600;700&display=swap');
    
    /* 全局样式 */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0d0d1f 100%);
    }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 隐藏左上角的页面导航 */
    [data-testid="stSidebarNav"] {display: none !important;}
    nav[data-testid="stSidebarNav"] {display: none !important;}
    .stSidebarNav {display: none !important;}
    
    /* 隐藏Streamlit自动生成的导航链接 */
    section[data-testid="stSidebarNav"] {display: none !important;}
    div[data-testid="stSidebarNav"] {display: none !important;}
    
    /* 侧边栏美化 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e3f 0%, #0f0f23 100%);
        border-right: 1px solid rgba(139, 92, 246, 0.2);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff;
    }
    
    /* 侧边栏所有文字都设为白色 */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* 主标题 */
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 50%, #22d3ee 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        letter-spacing: -2px;
        animation: glow 3s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 20px rgba(139, 92, 246, 0.3)); }
        to { filter: drop-shadow(0 0 40px rgba(139, 92, 246, 0.6)); }
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 300;
        color: #e2e8f0;
        text-align: center;
        margin-top: 0.5rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    
    /* 玻璃卡片效果 */
    .glass-card {
        background: rgba(30, 30, 63, 0.6);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(139, 92, 246, 0.5);
        transform: translateY(-5px);
        box-shadow: 
            0 20px 60px rgba(139, 92, 246, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    /* 功能卡片 */
    .feature-card {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(139, 92, 246, 0.15);
        padding: 1.5rem;
        height: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .feature-card:hover {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(99, 102, 241, 0.1) 100%);
        border-color: rgba(139, 92, 246, 0.4);
        transform: scale(1.02);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #e2e8f0;
        line-height: 1.6;
    }
    
    /* 指标卡片 */
    .metric-card {
        background: linear-gradient(135deg, #1e1e3f 0%, #2d2d5a 100%);
        border-radius: 16px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(139, 92, 246, 0.5);
        box-shadow: 0 10px 40px rgba(139, 92, 246, 0.15);
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a855f7 0%, #22d3ee 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #e2e8f0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    /* 导航按钮 */
    .nav-button {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(99, 102, 241, 0.1) 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .nav-button:hover {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.4) 0%, rgba(99, 102, 241, 0.2) 100%);
        border-color: rgba(139, 92, 246, 0.6);
        transform: translateX(5px);
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        border-color: transparent;
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);
    }
    
    /* 分隔线 */
    .fancy-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(139, 92, 246, 0.5) 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    /* 代码块美化 */
    .code-block {
        background: rgba(15, 15, 35, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        padding: 1.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: #22d3ee;
        overflow-x: auto;
    }
    
    /* 标签美化 */
    .tag {
        display: inline-block;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(99, 102, 241, 0.2) 100%);
        border-radius: 20px;
        padding: 0.3rem 1rem;
        font-size: 0.8rem;
        color: #a855f7;
        margin: 0.2rem;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }
    
    /* 动画粒子背景 */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    /* Streamlit 组件自定义 */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4);
    }
    
    .stSelectbox > div > div {
        background: rgba(30, 30, 63, 0.8);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 10px;
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #8b5cf6, #22d3ee);
    }
    
    /* Radio 按钮美化 */
    .stRadio > div {
        background: transparent;
    }
    
    .stRadio > div > label {
        background: rgba(30, 30, 63, 0.6);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        transition: all 0.3s ease;
        color: #ffffff !important;
    }
    
    .stRadio > div > label > div {
        color: #ffffff !important;
    }
    
    .stRadio > div > label > div > p {
        color: #ffffff !important;
    }
    
    .stRadio > div > label span {
        color: #ffffff !important;
    }
    
    /* 确保所有radio文本都是白色 */
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stRadio label div {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stRadio label p {
        color: #ffffff !important;
    }
    
    .stRadio > div > label:hover {
        border-color: rgba(139, 92, 246, 0.5);
        background: rgba(139, 92, 246, 0.1);
    }
    
    /* 展开器美化 */
    .streamlit-expanderHeader {
        background: rgba(30, 30, 63, 0.6);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 12px;
    }
    
    /* 数据表格美化 */
    .stDataFrame {
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* 进度条美化 */
    .stProgress > div > div {
        background: linear-gradient(90deg, #8b5cf6, #22d3ee);
        border-radius: 10px;
    }
    
    /* 警告框美化 */
    .stAlert {
        background: rgba(30, 30, 63, 0.8);
        border-radius: 12px;
    }
    
    /* Tab 美化 */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 30, 63, 0.6);
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #e2e8f0;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        color: white;
    }
    
    /* 页面标题 */
    .page-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    
    .page-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #cbd5e1;
        margin-bottom: 2rem;
    }
    
    /* Section 标题 */
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #e2e8f0;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(139, 92, 246, 0.5) 0%, transparent 100%);
    }
</style>
""", unsafe_allow_html=True)

# ================= 侧边栏 =================
with st.sidebar:
    # Logo 和标题
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">⛏️</div>
        <div style="font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700; 
                    background: linear-gradient(135deg, #a855f7, #22d3ee); 
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            SquirRL
        </div>
        <div style="font-family: 'Inter', sans-serif; font-size: 0.75rem; color: #cbd5e1; 
                    letter-spacing: 2px; text-transform: uppercase;">
            Auditor
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 导航
    st.markdown("""
    <div style="font-family: 'Inter', sans-serif; font-size: 0.75rem; color: #e2e8f0; 
                letter-spacing: 2px; text-transform: uppercase; margin-bottom: 1rem;">
        导航菜单
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "",
        [
            "🏠 首页",
            "🎬 攻击模拟动画", 
            "📈 多协议对比",
            "🛡️ 防御效果评估",
            "📊 Gamma参数分析",
            "🎯 一键演示"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 快速状态
    st.markdown("""
    <div style="font-family: 'Inter', sans-serif; font-size: 0.75rem; color: #e2e8f0; 
                letter-spacing: 2px; text-transform: uppercase; margin-bottom: 1rem;">
        系统状态
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); 
                    border-radius: 8px; padding: 0.75rem; text-align: center;">
            <div style="color: #22c55e; font-size: 1.2rem;">●</div>
            <div style="color: #e2e8f0; font-size: 0.7rem;">运行中</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); 
                    border-radius: 8px; padding: 0.75rem; text-align: center;">
            <div style="color: #c4b5fd; font-family: 'JetBrains Mono'; font-size: 1rem;">v1.0</div>
            <div style="color: #e2e8f0; font-size: 0.7rem;">版本</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 底部信息
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-family: 'Inter', sans-serif; font-size: 0.7rem; color: #cbd5e1;">
            Powered by
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #e2e8f0;">
            Stable-Baselines3 + Streamlit
        </div>
    </div>
    """, unsafe_allow_html=True)


# ================= 主内容区 =================
if page == "🏠 首页":
    # Hero 区域
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0;">
        <h1 class="hero-title">SquirRL-Auditor</h1>
        <p class="hero-subtitle">Blockchain Incentive Mechanism Security Auditor</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 核心指标
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("3", "支持协议", "Bitcoin • GHOST • ETH"),
        ("1", "攻击类型", "自私挖矿"),
        ("DQN", "核心算法", "Deep Q-Network"),
        ("UTB", "防御机制", "Uncles-To-Block")
    ]
    
    for col, (value, label, desc) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
                <div style="font-size: 0.7rem; color: #cbd5e1; margin-top: 0.5rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 功能卡片
    st.markdown('<div class="section-title">🎯 核心功能</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    features = [
        ("🎬", "攻击模拟动画", "通过精美动画直观展示自私挖矿攻击的完整流程，理解区块隐藏与发布策略"),
        ("📈", "多协议对比", "交互式 3D 曲面图对比 Bitcoin、GHOST、Ethereum 的安全性差异"),
        ("🛡️", "防御效果评估", "评估 UTB 等防御机制的效果，用雷达图和柱状图展示防御前后对比"),
        ("📊", "Gamma参数分析", "研究网络跟随者比例(γ)对攻击效果的影响，验证理论预测"),
        ("🎯", "一键演示", "自动播放完整研究流程，专为答辩和展示设计")
    ]
    
    for i, (icon, title, desc) in enumerate(features):
        if i % 3 == 0:
            col1, col2, col3 = st.columns(3)
        with [col1, col2, col3][i % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <span class="feature-icon">{icon}</span>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 技术栈
    st.markdown('<div class="section-title">🔧 技术栈</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-family: 'Inter', sans-serif; font-weight: 600; color: #e2e8f0; margin-bottom: 1rem;">
                🧠 机器学习
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                <span class="tag">PyTorch</span>
                <span class="tag">Stable-Baselines3</span>
                <span class="tag">Gymnasium</span>
                <span class="tag">DQN</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-family: 'Inter', sans-serif; font-weight: 600; color: #e2e8f0; margin-bottom: 1rem;">
                🎨 可视化
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                <span class="tag">Streamlit</span>
                <span class="tag">Plotly</span>
                <span class="tag">3D Surface</span>
                <span class="tag">Animation</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 快速开始
    st.markdown('<div class="section-title">🚀 快速开始</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="code-block">
<span style="color: #cbd5e1;"># 启动 Web 应用</span>
<span style="color: #f472b6;">streamlit</span> run app/main.py

<span style="color: #cbd5e1;"># 命令行训练</span>
<span style="color: #f472b6;">python</span> -m src.cli train --protocol bitcoin --alpha 0.35

<span style="color: #cbd5e1;"># Docker 部署</span>
<span style="color: #f472b6;">docker-compose</span> up --build
    </div>
    """, unsafe_allow_html=True)

elif page == "🎬 攻击模拟动画":
    from app.pages import attack_animation
    attack_animation.render()

elif page == "📈 多协议对比":
    from app.pages import protocol_comparison
    protocol_comparison.render()

elif page == "🛡️ 防御效果评估":
    from app.pages import defense_evaluation
    defense_evaluation.render()

elif page == "📊 Gamma参数分析":
    from app.pages import gamma_analysis
    gamma_analysis.render()

elif page == "🎯 一键演示":
    from app.pages import auto_demo
    auto_demo.render()
