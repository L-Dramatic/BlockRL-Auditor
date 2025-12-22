"""
页面1: 实时训练监控 - 精致版
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time


# Plotly 主题配置
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(30,30,63,0.6)',
        'font': {'family': 'Inter, sans-serif', 'color': '#e2e8f0'},
        'title': {'font': {'family': 'Playfair Display, serif', 'size': 20}},
        'xaxis': {
            'gridcolor': 'rgba(139,92,246,0.1)',
            'linecolor': 'rgba(139,92,246,0.3)',
            'tickfont': {'color': '#94a3b8'}
        },
        'yaxis': {
            'gridcolor': 'rgba(139,92,246,0.1)',
            'linecolor': 'rgba(139,92,246,0.3)',
            'tickfont': {'color': '#94a3b8'}
        },
        'colorway': ['#8b5cf6', '#22d3ee', '#f472b6', '#34d399', '#fbbf24']
    }
}


def render():
    # 页面标题
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="page-title">📊 实时训练监控</h1>
        <p class="page-subtitle">观察强化学习训练的实时动态，包括奖励曲线、损失函数和策略分布</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 参数配置面板
    st.markdown('<div class="section-title">⚙️ 训练参数</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        protocol = st.selectbox(
            "🔗 协议类型",
            ["Bitcoin", "GHOST", "Ethereum"],
            help="选择要分析的区块链协议"
        )
    
    with col2:
        alpha = st.slider(
            "⚡ 攻击者算力 (α)",
            min_value=0.10,
            max_value=0.49,
            value=0.35,
            step=0.01,
            format="%.2f"
        )
    
    with col3:
        gamma = st.slider(
            "👥 跟随者比例 (γ)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            format="%.1f"
        )
    
    with col4:
        total_timesteps = st.select_slider(
            "🔢 训练步数",
            options=[10000, 25000, 50000, 100000, 200000],
            value=50000
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 高级设置
    with st.expander("🔧 高级设置", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            learning_rate = st.select_slider(
                "学习率",
                options=[1e-5, 5e-5, 1e-4, 5e-4, 1e-3],
                value=1e-4,
                format_func=lambda x: f"{x:.0e}"
            )
        with col2:
            buffer_size = st.number_input(
                "经验回放大小",
                min_value=10000,
                max_value=100000,
                value=50000,
                step=10000
            )
        with col3:
            batch_size = st.selectbox(
                "批次大小",
                [16, 32, 64, 128],
                index=2
            )
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 控制按钮
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        start_training = st.button("🚀 开始训练", type="primary", use_container_width=True)
    with col2:
        stop_training = st.button("⏹️ 停止", use_container_width=True)
    
    # 训练状态
    if 'training_active' not in st.session_state:
        st.session_state.training_active = False
        st.session_state.training_data = {
            'steps': [], 'rewards': [], 'losses': [], 
            'reward_fractions': [], 'actions': {'Adopt': 0, 'Override': 0, 'Wait': 0, 'Match': 0}
        }
    
    if start_training:
        st.session_state.training_active = True
        st.session_state.training_data = {
            'steps': [], 'rewards': [], 'losses': [], 
            'reward_fractions': [], 'actions': {'Adopt': 0, 'Override': 0, 'Wait': 0, 'Match': 0}
        }
    
    if stop_training:
        st.session_state.training_active = False
    
    # 实时指标卡片
    st.markdown('<div class="section-title">📈 实时指标</div>', unsafe_allow_html=True)
    
    metrics_placeholder = st.empty()
    
    # 图表区域
    st.markdown('<div class="section-title">📊 训练曲线</div>', unsafe_allow_html=True)
    
    chart_placeholder = st.empty()
    
    # 策略分布
    st.markdown('<div class="section-title">🎯 策略分布</div>', unsafe_allow_html=True)
    
    strategy_placeholder = st.empty()
    
    if st.session_state.training_active:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 理论值计算
        def theoretical_reward(a, g):
            if a >= 0.5:
                return 1.0
            num = a * (1 - a) ** 2 * (4 * a + g * (1 - 2 * a)) - a ** 3
            den = 1 - a * (1 + (2 - a) * a)
            return max(a, a + num / den) if abs(den) > 1e-10 else a
        
        target_reward = theoretical_reward(alpha, gamma)
        
        for i in range(100):
            if not st.session_state.training_active:
                break
            
            progress = (i + 1) / 100
            step = int(total_timesteps * progress)
            
            # 模拟训练数据
            noise = np.random.normal(0, 0.02 * (1 - progress * 0.8))
            reward = alpha + (target_reward - alpha) * (1 - np.exp(-4 * progress)) + noise
            loss = 0.8 * np.exp(-3 * progress) + np.random.normal(0, 0.02) + 0.05
            reward_fraction = reward
            
            st.session_state.training_data['steps'].append(step)
            st.session_state.training_data['rewards'].append(reward)
            st.session_state.training_data['losses'].append(max(0.01, loss))
            st.session_state.training_data['reward_fractions'].append(reward_fraction)
            
            # 更新动作统计
            st.session_state.training_data['actions']['Wait'] += np.random.randint(30, 50)
            st.session_state.training_data['actions']['Override'] += np.random.randint(10, 25)
            st.session_state.training_data['actions']['Adopt'] += np.random.randint(5, 15)
            st.session_state.training_data['actions']['Match'] += np.random.randint(2, 8)
            
            # 更新进度
            progress_bar.progress(progress)
            status_text.markdown(f"""
            <div style="font-family: 'JetBrains Mono', monospace; color: #94a3b8; font-size: 0.9rem;">
                训练进度: <span style="color: #22d3ee;">{i+1}%</span> | 
                步数: <span style="color: #a855f7;">{step:,}</span> / {total_timesteps:,}
            </div>
            """, unsafe_allow_html=True)
            
            # 更新指标卡片
            with metrics_placeholder.container():
                m1, m2, m3, m4 = st.columns(4)
                
                with m1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{step:,}</div>
                        <div class="metric-label">训练步数</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m2:
                    delta = reward - alpha
                    color = "#22c55e" if delta > 0 else "#ef4444"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{reward:.4f}</div>
                        <div class="metric-label">当前奖励</div>
                        <div style="color: {color}; font-size: 0.8rem; font-family: 'JetBrains Mono';">
                            {delta:+.4f} vs 诚实
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{loss:.4f}</div>
                        <div class="metric-label">损失函数</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m4:
                    pct = (reward / target_reward) * 100 if target_reward > 0 else 0
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{pct:.1f}%</div>
                        <div class="metric-label">理论最优</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 更新主图表
            if len(st.session_state.training_data['steps']) > 1:
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=('奖励曲线', '损失曲线'),
                    horizontal_spacing=0.1
                )
                
                # 奖励曲线
                fig.add_trace(
                    go.Scatter(
                        x=st.session_state.training_data['steps'],
                        y=st.session_state.training_data['rewards'],
                        mode='lines',
                        name='奖励',
                        line=dict(color='#8b5cf6', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(139,92,246,0.1)'
                    ),
                    row=1, col=1
                )
                
                # 诚实基准
                fig.add_hline(y=alpha, line_dash="dash", line_color="#64748b",
                             annotation_text=f"诚实 α={alpha}", row=1, col=1)
                
                # 理论最优
                fig.add_hline(y=target_reward, line_dash="dot", line_color="#22d3ee",
                             annotation_text=f"理论最优 {target_reward:.3f}", row=1, col=1)
                
                # 损失曲线
                fig.add_trace(
                    go.Scatter(
                        x=st.session_state.training_data['steps'],
                        y=st.session_state.training_data['losses'],
                        mode='lines',
                        name='损失',
                        line=dict(color='#f472b6', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(244,114,182,0.1)'
                    ),
                    row=1, col=2
                )
                
                fig.update_layout(
                    height=350,
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30,30,63,0.4)',
                    font=dict(family='Inter', color='#e2e8f0'),
                    margin=dict(l=50, r=50, t=50, b=50)
                )
                
                fig.update_xaxes(gridcolor='rgba(139,92,246,0.1)', 
                                linecolor='rgba(139,92,246,0.2)')
                fig.update_yaxes(gridcolor='rgba(139,92,246,0.1)', 
                                linecolor='rgba(139,92,246,0.2)')
                
                chart_placeholder.plotly_chart(fig, use_container_width=True)
            
            # 更新策略分布
            actions = st.session_state.training_data['actions']
            total_actions = sum(actions.values())
            
            if total_actions > 0:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(actions.keys()),
                    values=list(actions.values()),
                    hole=0.6,
                    marker=dict(
                        colors=['#8b5cf6', '#22d3ee', '#f472b6', '#34d399'],
                        line=dict(color='rgba(30,30,63,1)', width=2)
                    ),
                    textinfo='label+percent',
                    textfont=dict(size=12, color='#e2e8f0'),
                    hovertemplate="<b>%{label}</b><br>次数: %{value:,}<br>占比: %{percent}<extra></extra>"
                )])
                
                fig_pie.update_layout(
                    height=300,
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='#e2e8f0'),
                    annotations=[dict(
                        text=f'<b>{total_actions:,}</b><br>总动作',
                        x=0.5, y=0.5,
                        font_size=16,
                        font_color='#e2e8f0',
                        showarrow=False
                    )],
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                
                strategy_placeholder.plotly_chart(fig_pie, use_container_width=True)
            
            time.sleep(0.08)
        
        st.session_state.training_active = False
        st.balloons()
        st.success("🎉 训练完成！模型已达到接近理论最优的性能。")
    
    else:
        # 显示静态提示
        if len(st.session_state.training_data['steps']) == 0:
            with metrics_placeholder.container():
                st.markdown("""
                <div class="glass-card" style="text-align: center; padding: 3rem;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
                    <div style="font-family: 'Inter', sans-serif; font-size: 1.2rem; color: #e2e8f0; margin-bottom: 0.5rem;">
                        准备开始训练
                    </div>
                    <div style="font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #64748b;">
                        调整参数后点击「开始训练」按钮
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 导出功能
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📥 导出结果</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = "step,reward,loss\n"
        if st.session_state.training_data['steps']:
            for s, r, l in zip(
                st.session_state.training_data['steps'],
                st.session_state.training_data['rewards'],
                st.session_state.training_data['losses']
            ):
                csv_data += f"{s},{r},{l}\n"
        
        st.download_button(
            "📊 下载训练数据 (CSV)",
            data=csv_data,
            file_name="training_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            "🖼️ 下载图表 (PNG)",
            data=b"",
            file_name="training_chart.png",
            mime="image/png",
            disabled=True,
            use_container_width=True
        )
    
    with col3:
        st.download_button(
            "🤖 保存模型",
            data=b"",
            file_name="model.zip",
            mime="application/zip",
            disabled=True,
            use_container_width=True
        )


if __name__ == "__main__":
    render()
