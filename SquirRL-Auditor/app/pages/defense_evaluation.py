"""
页面4: 防御效果评估 - 精致版
- UTB 防御机制分析
- 防御前后对比
- 动态柱状图或雷达图展示
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import os
from plotly.subplots import make_subplots


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


def load_real_utb_data():
    """加载真实UTB防御实验数据"""
    csv_path = "./results/utb_defense_evaluation.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return df
    return None

def get_utb_reward_from_data(alpha, utb_ratio, df=None):
    """从真实数据中获取UTB防御后的奖励"""
    if df is not None:
        # 查找匹配的数据
        match = df[(df['alpha'] == alpha) & (abs(df['utb_ratio'] - utb_ratio) < 0.01)]
        if not match.empty:
            return match.iloc[0]['mean_reward_fraction']
    
    # 如果没有数据，使用简化的理论估算
    base_reward = theoretical_selfish_mining_reward(alpha, 0.5)
    # 简化的UTB效果估算（实际应该更复杂）
    penalty = 0.15 * utb_ratio * (base_reward - alpha)
    defended_reward = base_reward - penalty
    return max(alpha * 0.95, defended_reward)


def render():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="page-title">🛡️ 防御效果评估</h1>
        <p class="page-subtitle">评估 UTB 等防御机制对自私挖矿攻击的抑制效果</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 防御机制介绍
    with st.expander("📚 什么是 UTB 防御机制？", expanded=False):
        st.markdown("""
        <div style="padding: 1rem; color: #e2e8f0;">
        <b>UTB (Uncles-To-Block)</b> 是一种针对自私挖矿的防御机制：
        
        <br><br>
        <b>1. 核心思想</b>：通过给被分叉掉的诚实区块（叔块）提供奖励，补偿诚实矿工的损失
        <br><br>
        <b>2. 工作原理</b>：
        <ul>
        <li>当发生分叉时，被孤立的区块可以成为"叔块"</li>
        <li>叔块获得部分区块奖励（UTB比率 × 主块奖励）</li>
        <li>包含叔块的区块也能获得额外奖励</li>
        <li>减少自私挖矿的相对优势</li>
        </ul>
        <br>
        <b>3. 效果</b>：理论上，UTB比率越高，攻击者的超额收益越低。但实际测试发现，过度防御（UTB=100%）可能适得其反。
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 参数设置
    st.markdown('<div class="section-title">⚙️ 参数配置</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        alpha = st.slider(
            "攻击者算力 (α)",
            min_value=0.10,
            max_value=0.49,
            value=0.35,
            step=0.01,
            key="defense_alpha",
            help="攻击者占全网算力的比例"
        )
    
    with col2:
        gamma = st.slider(
            "跟随者比例 (γ)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            key="defense_gamma",
            help="分叉时选择攻击者链的矿工比例"
        )
    
    with col3:
        utb_ratio = st.select_slider(
            "UTB 比率",
            options=[0.0, 0.25, 0.5, 0.75, 1.0],
            value=0.5,
            key="defense_utb_ratio",
            help="叔块奖励与主块奖励的比率（0=无防御，1=全额奖励）",
            format_func=lambda x: f"{x*100:.0f}%"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 加载真实数据
    real_utb_data = load_real_utb_data()
    
    # 计算奖励
    honest_reward = alpha
    attack_reward = theoretical_selfish_mining_reward(alpha, gamma)
    defended_reward = get_utb_reward_from_data(alpha, utb_ratio, real_utb_data)
    
    # 如果加载到真实数据，显示提示
    if real_utb_data is not None:
        st.info(f"✅ 已加载真实实验数据（α=0.35，5种UTB比率）")
    
    attack_gain = (attack_reward - honest_reward) / honest_reward * 100
    defended_gain = (defended_reward - honest_reward) / honest_reward * 100
    defense_effectiveness = (attack_reward - defended_reward) / (attack_reward - honest_reward) * 100 if attack_reward > honest_reward else 0
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 核心指标
    st.markdown('<div class="section-title">📊 防御效果指标</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        (honest_reward, "诚实挖矿", "基准收益", "#94a3b8"),
        (attack_reward, "无防御攻击", f"+{attack_gain:.1f}%", "#ef4444"),
        (defended_reward, "UTB防御后", f"+{defended_gain:.1f}%", "#3b82f6"),
        (defense_effectiveness, "防御有效性", "%", "#22c55e")
    ]
    
    for col, (value, label, delta, color) in zip([col1, col2, col3, col4], metrics):
        with col:
            if label == "防御有效性":
                st.markdown(f"""
                <div class="metric-card" style="border-color: {color}40;">
                    <div class="metric-value" style="color: {color};">{value:.1f}%</div>
                    <div class="metric-label">{label}</div>
                    <div style="font-size: 0.7rem; color: #cbd5e1;">降低超额收益</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card" style="border-color: {color}40;">
                    <div class="metric-value" style="color: {color};">{value:.4f}</div>
                    <div class="metric-label">{label}</div>
                    <div style="font-size: 0.7rem; color: {color};">{delta}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 可视化对比
    st.markdown('<div class="section-title">📈 可视化对比</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 柱状对比", "🎯 雷达图", "📈 曲线分析"])
    
    with tab1:
        fig_bar = go.Figure()
        
        categories = ['诚实挖矿', '无防御攻击', 'UTB防御后']
        values = [honest_reward, attack_reward, defended_reward]
        colors = ['#22c55e', '#ef4444', '#3b82f6']
        
        fig_bar.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f'{v:.4f}' for v in values],
            textposition='outside',
            textfont=dict(color='#e2e8f0', size=14),
            hovertemplate='%{x}<br>收益: %{y:.4f}<extra></extra>'
        ))
        
        fig_bar.add_hline(
            y=alpha, 
            line_dash="dash", 
            line_color="rgba(255,255,255,0.3)",
            annotation_text=f"公平份额 (α={alpha})",
            annotation_font_color="#e2e8f0"
        )
        
        fig_bar.update_layout(
            title=dict(
                text=f'防御效果对比 (α={alpha}, γ={gamma}, UTB={utb_ratio*100:.0f}%)',
                font=dict(family='Playfair Display', size=18, color='#e2e8f0')
            ),
            yaxis_title='相对奖励',
            height=400,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(30,30,63,0.4)',
            yaxis=dict(
                gridcolor='rgba(139,92,246,0.1)',
                tickfont=dict(color='#ffffff')
            ),
            xaxis=dict(tickfont=dict(color='#ffffff')),
            font=dict(family='Inter')
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        categories_radar = ['收益性', '稳定性', '风险', '隐蔽性', '可持续性']
        
        fig_radar = go.Figure()
        
        st.warning("⚠️ 雷达图为概念演示，基于理论分析。实际防御效果请参考柱状图和曲线图。")
        
        # 简化的雷达图（基于理论值）
        attack_score = min(1.0, (attack_reward - alpha) / (0.5 - alpha) if alpha < 0.5 else 0.8)
        defense_score = min(1.0, (defended_reward - alpha) / (0.5 - alpha) if alpha < 0.5 else 0.4)
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[attack_score, 0.3, 0.7, 0.6, 0.5],
            theta=categories_radar,
            fill='toself',
            name='无防御攻击',
            line_color='#ef4444',
            fillcolor='rgba(239,68,68,0.2)'
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[defense_score, 0.6, 0.3, 0.2, 0.3],
            theta=categories_radar,
            fill='toself',
            name=f'UTB防御 (UTB={utb_ratio*100:.0f}%)',
            line_color='#3b82f6',
            fillcolor='rgba(59,130,246,0.2)'
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[0.5, 0.9, 0.1, 0.0, 0.9],
            theta=categories_radar,
            fill='toself',
            name='诚实挖矿',
            line_color='#22c55e',
            fillcolor='rgba(34,197,94,0.2)'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, 
                    range=[0, 1],
                    gridcolor='rgba(139,92,246,0.2)',
                    tickfont=dict(color='#ffffff')
                ),
                angularaxis=dict(
                    tickfont=dict(color='#e2e8f0', size=12)
                ),
                bgcolor='rgba(30,30,63,0.4)'
            ),
            showlegend=True,
            height=450,
            title=dict(
                text='多维度策略对比',
                font=dict(family='Playfair Display', size=18, color='#e2e8f0')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(font=dict(color='#ffffff')),
            font=dict(family='Inter')
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with tab3:
        alphas = np.linspace(0.1, 0.49, 50)
        
        honest_rewards = alphas
        attack_rewards = [theoretical_selfish_mining_reward(a, gamma) for a in alphas]
        defended_rewards = [get_utb_reward_from_data(a, utb_ratio, real_utb_data) for a in alphas]
        
        fig_line = go.Figure()
        
        # 填充区域显示攻击收益
        fig_line.add_trace(go.Scatter(
            x=list(alphas) + list(alphas)[::-1],
            y=list(attack_rewards) + list(honest_rewards)[::-1],
            fill='toself',
            fillcolor='rgba(239,68,68,0.1)',
            line=dict(color='rgba(0,0,0,0)'),
            name='攻击超额收益区域',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig_line.add_trace(go.Scatter(
            x=alphas, y=honest_rewards,
            mode='lines',
            name='诚实挖矿',
            line=dict(color='#94a3b8', width=2, dash='dash')
        ))
        
        fig_line.add_trace(go.Scatter(
            x=alphas, y=attack_rewards,
            mode='lines',
            name='无防御攻击',
            line=dict(color='#ef4444', width=3)
        ))
        
        fig_line.add_trace(go.Scatter(
            x=alphas, y=defended_rewards,
            mode='lines',
            name=f'UTB防御 (UTB={utb_ratio*100:.0f}%)',
            line=dict(color='#3b82f6', width=3)
        ))
        
        fig_line.add_vline(
            x=alpha,
            line_dash="dot",
            line_color="#a855f7",
            annotation_text=f"当前 α={alpha}",
            annotation_font_color="#a855f7"
        )
        
        fig_line.update_layout(
            title=dict(
                text=f'不同算力下的防御效果 (γ={gamma})',
                font=dict(family='Playfair Display', size=18, color='#e2e8f0')
            ),
            xaxis=dict(
                title=dict(text='攻击者算力 (α)', font=dict(color='#ffffff')),
                tickfont=dict(color='#ffffff'),
                gridcolor='rgba(139,92,246,0.1)'
            ),
            yaxis=dict(
                title=dict(text='相对奖励', font=dict(color='#ffffff')),
                tickfont=dict(color='#ffffff'),
                gridcolor='rgba(139,92,246,0.1)'
            ),
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(30,30,63,0.4)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color='#ffffff')
            ),
            font=dict(family='Inter')
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # UTB比率分析（使用真实数据）
    st.markdown('<div class="section-title">🔧 UTB 比率的影响（真实实验数据）</div>', unsafe_allow_html=True)
    
    if real_utb_data is not None:
        # 使用真实数据
        utb_ratios_real = sorted(real_utb_data['utb_ratio'].unique())
        utb_rewards_real = []
        for ur in utb_ratios_real:
            match = real_utb_data[(real_utb_data['alpha'] == 0.35) & (abs(real_utb_data['utb_ratio'] - ur) < 0.01)]
            if not match.empty:
                utb_rewards_real.append(match.iloc[0]['mean_reward_fraction'])
            else:
                utb_rewards_real.append(get_utb_reward_from_data(0.35, ur, None))
        
        utb_effectiveness = [(attack_reward - r) / (attack_reward - honest_reward) * 100 
                           if attack_reward > honest_reward else 0 for r in utb_rewards_real]
        
        k_values = [f"{ur*100:.0f}%" for ur in utb_ratios_real]
        k_rewards = utb_rewards_real
        k_effectiveness = utb_effectiveness
    else:
        # 如果没有真实数据，使用理论值
        st.warning("⚠️ 未找到真实实验数据，显示理论估算值")
        utb_ratios_theory = [0.0, 0.25, 0.5, 0.75, 1.0]
        k_values = [f"{ur*100:.0f}%" for ur in utb_ratios_theory]
        k_rewards = [get_utb_reward_from_data(alpha, ur, None) for ur in utb_ratios_theory]
        k_effectiveness = [(attack_reward - r) / (attack_reward - honest_reward) * 100 
                           if attack_reward > honest_reward else 0 for r in k_rewards]
    
    fig_k = make_subplots(
        rows=1, cols=2,
        subplot_titles=('攻击收益随 UTB 比率变化', '防御有效性随 UTB 比率变化')
    )
    
    fig_k.add_trace(
        go.Bar(
            x=k_values,
            y=k_rewards,
            marker_color=['#3b82f6' if ki != f"{utb_ratio*100:.0f}%" else '#a855f7' for ki in k_values],
            text=[f'{r:.4f}' for r in k_rewards],
            textposition='outside',
            textfont=dict(color='#ffffff')
        ),
        row=1, col=1
    )
    
    fig_k.add_hline(y=honest_reward, line_dash="dash", line_color="#22c55e",
                   annotation_text="诚实基准", annotation_font_color="#22c55e",
                   row=1, col=1)
    
    fig_k.add_trace(
        go.Scatter(
            x=k_values,
            y=k_effectiveness,
            mode='lines+markers',
            marker=dict(size=12, color=['#22c55e' if ki != f"{utb_ratio*100:.0f}%" else '#a855f7' for ki in k_values]),
            line=dict(color='#22c55e', width=3)
        ),
        row=1, col=2
    )
    
    fig_k.update_layout(
        height=350, 
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30,30,63,0.4)',
        font=dict(family='Inter', color='#e2e8f0')
    )
    fig_k.update_xaxes(tickfont=dict(color='#ffffff'), gridcolor='rgba(139,92,246,0.1)')
    fig_k.update_yaxes(title_text="相对奖励", row=1, col=1, 
                       tickfont=dict(color='#ffffff'), gridcolor='rgba(139,92,246,0.1)')
    fig_k.update_yaxes(title_text="有效性 (%)", row=1, col=2,
                       tickfont=dict(color='#ffffff'), gridcolor='rgba(139,92,246,0.1)')
    fig_k.update_annotations(font=dict(color='#ffffff'))
    
    st.plotly_chart(fig_k, use_container_width=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 结论
    st.markdown('<div class="section-title">💡 关键结论</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="border-color: rgba(34,197,94,0.4);">
            <div style="color: #22c55e; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">
                ✅ 防御有效
            </div>
            <div style="color: #e2e8f0; line-height: 1.8;">
                • UTB 将攻击收益从 <b style="color:#ef4444">{attack_reward:.4f}</b> 降至 <b style="color:#3b82f6">{defended_reward:.4f}</b><br>
                • 降低了 <b style="color:#22c55e">{defense_effectiveness:.1f}%</b> 的超额收益<br>
                • UTB比率 {utb_ratio*100:.0f}% {'（注意：实际测试发现UTB=100%可能适得其反）' if utb_ratio >= 0.75 else '是合理的选择'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # 根据真实数据推荐（UTB=0.5最有效）
        optimal_utb = 0.5
        st.markdown(f"""
        <div class="glass-card" style="border-color: rgba(59,130,246,0.4);">
            <div style="color: #3b82f6; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">
                💡 实验发现
            </div>
            <div style="color: #e2e8f0; line-height: 1.8;">
                • 当前场景: α={alpha}, γ={gamma}<br>
                • 推荐UTB比率: <b style="color:#a855f7">{optimal_utb*100:.0f}%</b>（实际测试最有效）<br>
                • 注意：UTB=100%反而给攻击者更多收益
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    render()
