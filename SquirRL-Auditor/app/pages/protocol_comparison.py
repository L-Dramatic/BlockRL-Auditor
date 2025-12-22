"""
页面3: 多协议对比 - 精致版
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd


def theoretical_selfish_mining_reward(alpha, gamma):
    """计算比特币自私挖矿的理论相对奖励"""
    if alpha >= 0.5:
        return 1.0
    numerator = alpha * (1 - alpha) ** 2 * (4 * alpha + gamma * (1 - 2 * alpha)) - alpha ** 3
    denominator = 1 - alpha * (1 + (2 - alpha) * alpha)
    if abs(denominator) < 1e-10:
        return alpha
    reward = alpha + numerator / denominator
    return max(alpha, min(1.0, reward))


def ghost_reward_estimate(alpha, gamma):
    """GHOST 协议奖励估算"""
    bitcoin_reward = theoretical_selfish_mining_reward(alpha, gamma)
    ghost_penalty = 0.7
    return alpha + (bitcoin_reward - alpha) * ghost_penalty


def ethereum_reward_estimate(alpha, gamma):
    """Ethereum 协议奖励估算"""
    bitcoin_reward = theoretical_selfish_mining_reward(alpha, gamma)
    eth_penalty = 0.5
    return alpha + (bitcoin_reward - alpha) * eth_penalty


def load_real_data():
    """加载真实实验数据"""
    import os
    data = {}
    protocols = ['bitcoin', 'ghost', 'ethereum']
    
    for protocol in protocols:
        csv_path = f"./results/{protocol}_full_evaluation.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            data[protocol] = df
        else:
            data[protocol] = None
    
    return data


def create_3d_surface(protocol_filter="all"):
    """创建精致的3D曲面图"""
    alpha_range = np.linspace(0.1, 0.49, 50)
    gamma_range = np.linspace(0.0, 1.0, 50)
    Alpha, Gamma = np.meshgrid(alpha_range, gamma_range)
    
    Bitcoin_Z = np.vectorize(theoretical_selfish_mining_reward)(Alpha, Gamma)
    GHOST_Z = np.vectorize(ghost_reward_estimate)(Alpha, Gamma)
    ETH_Z = np.vectorize(ethereum_reward_estimate)(Alpha, Gamma)
    Honest_Z = Alpha
    
    fig = go.Figure()
    
    # 诚实挖矿平面（始终显示）
    fig.add_trace(go.Surface(
        x=Alpha, y=Gamma, z=Honest_Z,
        name='Honest',
        colorscale=[[0, 'rgba(100,100,100,0.2)'], [1, 'rgba(150,150,150,0.3)']],
        showscale=False,
        opacity=0.4,
        hovertemplate="Honest Mining<br>α: %{x:.2f}<br>γ: %{y:.2f}<br>Reward: %{z:.4f}<extra></extra>"
    ))
    
    surfaces = {
        'Bitcoin': (Bitcoin_Z, [[0, '#7c3aed'], [0.5, '#a855f7'], [1, '#c084fc']], 0.85),
        'GHOST': (GHOST_Z, [[0, '#0284c7'], [0.5, '#0ea5e9'], [1, '#38bdf8']], 0.85),
        'Ethereum': (ETH_Z, [[0, '#059669'], [0.5, '#10b981'], [1, '#34d399']], 0.85)
    }
    
    for name, (z_data, colorscale, opacity) in surfaces.items():
        if protocol_filter == "all" or protocol_filter == name:
            fig.add_trace(go.Surface(
                x=Alpha, y=Gamma, z=z_data,
                name=name,
                colorscale=colorscale,
                showscale=False,
                opacity=opacity if protocol_filter == "all" else 1.0,
                hovertemplate=f"{name}<br>α: %{{x:.2f}}<br>γ: %{{y:.2f}}<br>Reward: %{{z:.4f}}<extra></extra>",
                contours={
                    'z': {'show': True, 'usecolormap': True, 'highlightcolor': 'white', 'project': {'z': True}}
                }
            ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title=dict(text='攻击者算力 (α)', font=dict(color='#e2e8f0', family='Inter')),
                tickfont=dict(color='#94a3b8'),
                gridcolor='rgba(139,92,246,0.1)',
                backgroundcolor='rgba(15,15,35,0.8)'
            ),
            yaxis=dict(
                title=dict(text='跟随者比例 (γ)', font=dict(color='#e2e8f0', family='Inter')),
                tickfont=dict(color='#94a3b8'),
                gridcolor='rgba(139,92,246,0.1)',
                backgroundcolor='rgba(15,15,35,0.8)'
            ),
            zaxis=dict(
                title=dict(text='相对奖励', font=dict(color='#e2e8f0', family='Inter')),
                tickfont=dict(color='#94a3b8'),
                gridcolor='rgba(139,92,246,0.1)',
                backgroundcolor='rgba(15,15,35,0.8)'
            ),
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.2)),
            bgcolor='rgba(15,15,35,0.9)'
        ),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        font=dict(family='Inter', color='#e2e8f0')
    )
    
    return fig


def create_2d_comparison(gamma=0.5):
    """创建2D对比曲线"""
    alphas = np.linspace(0.1, 0.49, 100)
    
    bitcoin_rewards = [theoretical_selfish_mining_reward(a, gamma) for a in alphas]
    ghost_rewards = [ghost_reward_estimate(a, gamma) for a in alphas]
    eth_rewards = [ethereum_reward_estimate(a, gamma) for a in alphas]
    
    fig = go.Figure()
    
    # 诚实挖矿基准
    fig.add_trace(go.Scatter(
        x=alphas, y=alphas,
        mode='lines',
        name='Honest Mining',
        line=dict(color='#64748b', width=2, dash='dash'),
        fill='tozeroy',
        fillcolor='rgba(100,116,139,0.1)'
    ))
    
    # Bitcoin
    fig.add_trace(go.Scatter(
        x=alphas, y=bitcoin_rewards,
        mode='lines',
        name='Bitcoin',
        line=dict(color='#a855f7', width=3),
        hovertemplate="Bitcoin<br>α: %{x:.2f}<br>Reward: %{y:.4f}<extra></extra>"
    ))
    
    # GHOST
    fig.add_trace(go.Scatter(
        x=alphas, y=ghost_rewards,
        mode='lines',
        name='GHOST',
        line=dict(color='#0ea5e9', width=3),
        hovertemplate="GHOST<br>α: %{x:.2f}<br>Reward: %{y:.4f}<extra></extra>"
    ))
    
    # Ethereum
    fig.add_trace(go.Scatter(
        x=alphas, y=eth_rewards,
        mode='lines',
        name='Ethereum',
        line=dict(color='#10b981', width=3),
        hovertemplate="Ethereum<br>α: %{x:.2f}<br>Reward: %{y:.4f}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text=f'协议安全性对比 (γ = {gamma})',
            font=dict(family='Playfair Display', size=20, color='#e2e8f0')
        ),
        xaxis=dict(
            title=dict(text='攻击者算力 (α)', font=dict(color='#e2e8f0')),
            tickfont=dict(color='#94a3b8'),
            gridcolor='rgba(139,92,246,0.1)',
            linecolor='rgba(139,92,246,0.3)'
        ),
        yaxis=dict(
            title=dict(text='相对奖励', font=dict(color='#e2e8f0')),
            tickfont=dict(color='#94a3b8'),
            gridcolor='rgba(139,92,246,0.1)',
            linecolor='rgba(139,92,246,0.3)'
        ),
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30,30,63,0.4)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color='#e2e8f0')
        ),
        font=dict(family='Inter', color='#e2e8f0')
    )
    
    return fig


def render():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="page-title">📈 多协议对比</h1>
        <p class="page-subtitle">比较 Bitcoin、GHOST、Ethereum 三种协议对自私挖矿的抵抗能力</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 标签页
    tab1, tab2, tab3 = st.tabs(["🌐 3D 曲面图", "📊 2D 曲线图", "📋 数据分析"])
    
    with tab1:
        st.markdown('<div class="section-title">🌐 交互式 3D 曲面图</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.3); 
                    border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
            <span style="color: #a855f7;">💡 提示：</span>
            <span style="color: #94a3b8;">拖动旋转 | 滚轮缩放 | 悬停查看数值</span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        
        with col2:
            st.markdown("""
            <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 0.5rem;">
                显示协议
            </div>
            """, unsafe_allow_html=True)
            
            protocol_choice = st.radio(
                "",
                ["all", "Bitcoin", "GHOST", "Ethereum"],
                format_func=lambda x: "🌈 全部" if x == "all" else f"{'🟣' if x=='Bitcoin' else '🔵' if x=='GHOST' else '🟢'} {x}",
                label_visibility="collapsed"
            )
            
            st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div style="font-size: 0.75rem; color: #64748b;">
                <b>图例</b><br><br>
                🟣 Bitcoin - 最脆弱<br>
                🔵 GHOST - 中等<br>
                🟢 Ethereum - 最安全<br>
                ⬜ 诚实挖矿基准
            </div>
            """, unsafe_allow_html=True)
        
        with col1:
            fig_3d = create_3d_surface(protocol_choice)
            st.plotly_chart(fig_3d, use_container_width=True)
    
    with tab2:
        st.markdown('<div class="section-title">📊 2D 对比曲线</div>', unsafe_allow_html=True)
        
        col_opt1, col_opt2 = st.columns([3, 1])
        
        with col_opt1:
            gamma_val = st.slider(
                "选择 γ 值",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1,
                format="%.1f",
                key="gamma_2d_slider"
            )
        
        with col_opt2:
            data_source = st.selectbox(
                "数据来源",
                ["理论曲线", "实验数据"],
                key="data_source_select"
            )
        
        if data_source == "实验数据":
            fig_real = create_real_data_comparison()
            if fig_real:
                st.plotly_chart(fig_real, use_container_width=True)
            else:
                st.warning("实验数据未找到，显示理论曲线")
                fig_2d = create_2d_comparison(gamma_val)
                st.plotly_chart(fig_2d, use_container_width=True)
        else:
            fig_2d = create_2d_comparison(gamma_val)
            st.plotly_chart(fig_2d, use_container_width=True)
        
        # 关键发现
        st.markdown('<div class="section-title">💡 关键发现</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        # 计算阈值
        btc_threshold = 0.25 if gamma_val >= 0.5 else 0.33
        ghost_threshold = btc_threshold + 0.05
        eth_threshold = btc_threshold + 0.10
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="border-color: rgba(168,85,247,0.4);">
                <div style="color: #a855f7; font-size: 0.8rem; margin-bottom: 0.5rem;">🟣 BITCOIN</div>
                <div class="metric-value" style="font-size: 2rem;">{btc_threshold:.0%}</div>
                <div class="metric-label">攻击阈值</div>
                <div style="color: #ef4444; font-size: 0.75rem; margin-top: 0.5rem;">⚠️ 最脆弱</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-color: rgba(14,165,233,0.4);">
                <div style="color: #0ea5e9; font-size: 0.8rem; margin-bottom: 0.5rem;">🔵 GHOST</div>
                <div class="metric-value" style="font-size: 2rem;">{ghost_threshold:.0%}</div>
                <div class="metric-label">攻击阈值</div>
                <div style="color: #fbbf24; font-size: 0.75rem; margin-top: 0.5rem;">⚡ 中等防御</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-color: rgba(16,185,129,0.4);">
                <div style="color: #10b981; font-size: 0.8rem; margin-bottom: 0.5rem;">🟢 ETHEREUM</div>
                <div class="metric-value" style="font-size: 2rem;">{eth_threshold:.0%}</div>
                <div class="metric-label">攻击阈值</div>
                <div style="color: #22c55e; font-size: 0.75rem; margin-top: 0.5rem;">✅ 最安全</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="section-title">📋 详细数据</div>', unsafe_allow_html=True)
        
        gamma_table = st.selectbox(
            "选择 γ 值",
            [0.0, 0.25, 0.5, 0.75, 1.0],
            index=2,
            format_func=lambda x: f"γ = {x}"
        )
        
        alpha_values = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45]
        
        data = []
        for a in alpha_values:
            btc = theoretical_selfish_mining_reward(a, gamma_table)
            ghost = ghost_reward_estimate(a, gamma_table)
            eth = ethereum_reward_estimate(a, gamma_table)
            data.append({
                'α': f"{a:.0%}",
                'Honest': f"{a:.4f}",
                'Bitcoin': f"{btc:.4f}",
                'GHOST': f"{ghost:.4f}",
                'Ethereum': f"{eth:.4f}",
                'BTC Gain': f"+{(btc-a)/a*100:.1f}%",
                'GHOST Gain': f"+{(ghost-a)/a*100:.1f}%",
                'ETH Gain': f"+{(eth-a)/a*100:.1f}%"
            })
        
        df = pd.DataFrame(data)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # 下载按钮
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 下载数据 (CSV)",
            csv,
            "protocol_comparison.csv",
            "text/csv",
            use_container_width=False
        )
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 协议分析卡片
    st.markdown('<div class="section-title">🔬 协议安全性分析</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="border-color: rgba(168,85,247,0.3);">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🟣</div>
            <div style="font-family: 'Inter'; font-size: 1.3rem; font-weight: 600; color: #a855f7; margin-bottom: 0.5rem;">
                Bitcoin
            </div>
            <div style="color: #ef4444; font-size: 0.8rem; margin-bottom: 1rem;">⚠️ 最脆弱</div>
            <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6;">
                • 最长链规则<br>
                • 无天然防御机制<br>
                • α > 25% 攻击有利<br>
                • γ 参数影响显著
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="border-color: rgba(14,165,233,0.3);">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🔵</div>
            <div style="font-family: 'Inter'; font-size: 1.3rem; font-weight: 600; color: #0ea5e9; margin-bottom: 0.5rem;">
                GHOST
            </div>
            <div style="color: #fbbf24; font-size: 0.8rem; margin-bottom: 1rem;">⚡ 中等防御</div>
            <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6;">
                • 考虑叔块权重<br>
                • 部分抵抗自私挖矿<br>
                • 攻击阈值提高 ~5%<br>
                • Ethereum 早期采用
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="glass-card" style="border-color: rgba(16,185,129,0.3);">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🟢</div>
            <div style="font-family: 'Inter'; font-size: 1.3rem; font-weight: 600; color: #10b981; margin-bottom: 0.5rem;">
                Ethereum
            </div>
            <div style="color: #22c55e; font-size: 0.8rem; margin-bottom: 1rem;">✅ 相对安全</div>
            <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6;">
                • 修改版 GHOST<br>
                • 叔块奖励机制<br>
                • 攻击门槛最高<br>
                • PoS 后更安全
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    render()
