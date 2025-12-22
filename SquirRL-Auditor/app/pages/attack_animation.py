"""
页面2: 攻击模拟动画 - 精致版
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time


def create_blockchain_viz(public_chain, private_chain, step_info="", highlight_action=None):
    """创建精致的区块链可视化"""
    fig = go.Figure()
    
    # 颜色方案
    colors = {
        'honest': '#22c55e',      # 绿色
        'attacker': '#8b5cf6',    # 紫色
        'orphan': '#475569',      # 灰色
        'highlight': '#f472b6',   # 粉色高亮
        'bg': 'rgba(30,30,63,0.6)'
    }
    
    block_width = 0.7
    block_height = 0.4
    
    # 绘制公共链
    y_public = 0
    for i, block in enumerate(public_chain):
        is_attacker = block.get('is_attacker', False)
        is_orphan = block.get('orphaned', False)
        
        color = colors['orphan'] if is_orphan else (colors['attacker'] if is_attacker else colors['honest'])
        opacity = 0.4 if is_orphan else 1.0
        
        # 区块形状（带圆角效果的矩形）
        fig.add_trace(go.Scatter(
            x=[i, i + block_width, i + block_width, i, i],
            y=[y_public - block_height/2, y_public - block_height/2, 
               y_public + block_height/2, y_public + block_height/2, y_public - block_height/2],
            mode='lines',
            fill='toself',
            fillcolor=color,
            line=dict(color='rgba(255,255,255,0.3)', width=2),
            opacity=opacity,
            hovertemplate=f"区块 #{block.get('id', i)}<br>{'攻击者' if is_attacker else '诚实矿工'}<extra></extra>",
            showlegend=False
        ))
        
        # 区块标签
        label = str(block.get('id', i))
        fig.add_annotation(
            x=i + block_width/2, y=y_public,
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(color='white', size=14, family='JetBrains Mono')
        )
        
        # 连接线
        if i > 0:
            fig.add_trace(go.Scatter(
                x=[i - 0.15, i],
                y=[y_public, y_public],
                mode='lines',
                line=dict(color='rgba(139,92,246,0.5)', width=3),
                showlegend=False
            ))
    
    # 绘制私有链
    y_private = 1.2
    for i, block in enumerate(private_chain):
        # 私有区块（虚线边框）
        fig.add_trace(go.Scatter(
            x=[i, i + block_width, i + block_width, i, i],
            y=[y_private - block_height/2, y_private - block_height/2, 
               y_private + block_height/2, y_private + block_height/2, y_private - block_height/2],
            mode='lines',
            fill='toself',
            fillcolor='rgba(139,92,246,0.3)',
            line=dict(color=colors['attacker'], width=2, dash='dash'),
            hovertemplate=f"私有区块 P{block.get('id', i)}<br>状态: 隐藏中<extra></extra>",
            showlegend=False
        ))
        
        # 锁定图标
        fig.add_annotation(
            x=i + block_width/2, y=y_private,
            text=f"🔒 P{block.get('id', i)}",
            showarrow=False,
            font=dict(color='#a855f7', size=12, family='JetBrains Mono')
        )
        
        if i > 0:
            fig.add_trace(go.Scatter(
                x=[i - 0.15, i],
                y=[y_private, y_private],
                mode='lines',
                line=dict(color='rgba(139,92,246,0.3)', width=2, dash='dot'),
                showlegend=False
            ))
    
    # 链标签
    fig.add_annotation(x=-0.8, y=y_public, text="📢 公共链", showarrow=False,
                      font=dict(size=14, color='#22c55e', family='Inter'), xanchor='right')
    fig.add_annotation(x=-0.8, y=y_private, text="🔒 私有链", showarrow=False,
                      font=dict(size=14, color='#a855f7', family='Inter'), xanchor='right')
    
    # 步骤信息框
    if step_info:
        fig.add_annotation(
            x=0.5, y=1.12,
            xref='paper', yref='paper',
            text=step_info,
            showarrow=False,
            font=dict(size=16, color='#e2e8f0', family='Inter'),
            bgcolor='rgba(139,92,246,0.2)',
            bordercolor='rgba(139,92,246,0.5)',
            borderwidth=2,
            borderpad=12
        )
    
    # 动作高亮
    if highlight_action:
        action_colors = {
            'mine_attacker': '#8b5cf6',
            'mine_honest': '#22c55e',
            'publish': '#f472b6',
            'orphan': '#ef4444'
        }
        if highlight_action in action_colors:
            fig.add_annotation(
                x=0.95, y=0.05,
                xref='paper', yref='paper',
                text=f"⚡ {highlight_action.upper()}",
                showarrow=False,
                font=dict(size=12, color=action_colors[highlight_action]),
                bgcolor='rgba(0,0,0,0.5)',
                borderpad=8
            )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30,30,63,0.4)',
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-1.5, max(len(public_chain), len(private_chain)) + 1]
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.8, 2.0]
        ),
        margin=dict(l=100, r=50, t=80, b=50)
    )
    
    return fig


def render():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="page-title">🎬 攻击模拟动画</h1>
        <p class="page-subtitle">通过动画直观理解自私挖矿攻击的完整过程</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 场景选择
    st.markdown('<div class="section-title">🎭 选择攻击场景</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        scenario = st.selectbox(
            "攻击场景",
            [
                "🎯 基础自私挖矿 (Selfish Mining)",
                "⚡ 领先发布 (Lead Publishing)",
                "🏃 追赶成功 (Catch-up)",
                "💔 被迫放弃 (Forced Abandon)"
            ],
            label_visibility="collapsed"
        )
    
    with col2:
        speed = st.select_slider(
            "速度",
            options=["🐢 慢", "🚶 中", "🚀 快"],
            value="🚶 中"
        )
        speed_map = {"🐢 慢": 2.0, "🚶 中": 1.2, "🚀 快": 0.6}
    
    with col3:
        auto_loop = st.checkbox("🔄 循环播放", value=False)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 控制按钮
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        play_btn = st.button("▶️ 播放", type="primary", use_container_width=True)
    with col2:
        step_btn = st.button("⏭️ 单步", use_container_width=True)
    with col3:
        reset_btn = st.button("🔄 重置", use_container_width=True)
    
    # 动画步骤定义
    scenarios = {
        "🎯 基础自私挖矿 (Selfish Mining)": [
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}], 'private': [],
             'info': '🏁 初始状态：公共链有3个区块', 'action': None},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}], 'private': [{'id': 3}],
             'info': '⛏️ 攻击者挖到区块 → 选择隐藏！', 'action': 'mine_attacker'},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}], 'private': [{'id': 3}, {'id': 4}],
             'info': '⛏️ 攻击者继续挖矿，领先2个区块', 'action': 'mine_attacker'},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': '3h'}], 'private': [{'id': 3}, {'id': 4}],
             'info': '⚠️ 诚实矿工挖到区块 3h', 'action': 'mine_honest'},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3, 'is_attacker': True}, {'id': 4, 'is_attacker': True}], 
             'private': [],
             'info': '💥 攻击者发布私有链！造成重组', 'action': 'publish'},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3, 'is_attacker': True}, {'id': 4, 'is_attacker': True}], 
             'private': [],
             'info': '✅ 攻击成功！区块 3h 被孤立', 'action': 'orphan'}
        ],
        "⚡ 领先发布 (Lead Publishing)": [
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}], 'private': [{'id': 3}],
             'info': '🏁 攻击者领先1个区块', 'action': None},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': '3h'}], 'private': [{'id': 3}],
             'info': '⚠️ 诚实矿工也挖到区块！危险', 'action': 'mine_honest'},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3, 'is_attacker': True}], 
             'private': [],
             'info': '📢 攻击者立即发布，制造分叉', 'action': 'publish'},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3, 'is_attacker': True}], 
             'private': [],
             'info': '🎲 γ比例矿工选择攻击者链', 'action': None}
        ],
        "🏃 追赶成功 (Catch-up)": [
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': '3h'}], 'private': [{'id': 3}],
             'info': '😰 攻击者落后1个区块', 'action': None},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': '3h'}], 'private': [{'id': 3}, {'id': 4}],
             'info': '⛏️ 攻击者奋力追赶！', 'action': 'mine_attacker'},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': '3h'}], 'private': [{'id': 3}, {'id': 4}, {'id': 5}],
             'info': '⛏️ 继续挖矿，终于超过！', 'action': 'mine_attacker'},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3, 'is_attacker': True}, {'id': 4, 'is_attacker': True}, {'id': 5, 'is_attacker': True}], 
             'private': [],
             'info': '💥 发布私有链，大逆转！', 'action': 'publish'}
        ],
        "💔 被迫放弃 (Forced Abandon)": [
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}], 'private': [{'id': 3}],
             'info': '🏁 攻击者有1个私有区块', 'action': None},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': '3h'}], 'private': [{'id': 3}],
             'info': '😰 诚实矿工挖到区块', 'action': 'mine_honest'},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': '3h'}, {'id': '4h'}], 'private': [{'id': 3}],
             'info': '😱 诚实矿工又挖到一个！', 'action': 'mine_honest'},
            {'public': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': '3h'}, {'id': '4h'}], 'private': [],
             'info': '💔 攻击者被迫放弃私有链', 'action': 'orphan'}
        ]
    }
    
    steps = scenarios.get(scenario, scenarios["🎯 基础自私挖矿 (Selfish Mining)"])
    
    # 状态管理
    if 'anim_step' not in st.session_state:
        st.session_state.anim_step = 0
    
    if reset_btn:
        st.session_state.anim_step = 0
    
    # 图表占位符
    chart_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    # 播放动画
    if play_btn:
        for i in range(len(steps)):
            step = steps[i]
            fig = create_blockchain_viz(
                step['public'], step['private'],
                step['info'], step.get('action')
            )
            chart_placeholder.plotly_chart(fig, use_container_width=True)
            
            # 进度指示
            progress_placeholder.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <span style="font-family: 'JetBrains Mono'; color: #94a3b8;">
                    步骤 {i+1} / {len(steps)}
                </span>
                <div style="display: flex; justify-content: center; gap: 0.5rem; margin-top: 0.5rem;">
                    {''.join(['<span style="width: 12px; height: 12px; border-radius: 50%; background: ' + ('#8b5cf6' if j <= i else 'rgba(139,92,246,0.2)') + '; display: inline-block;"></span>' for j in range(len(steps))])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(speed_map[speed])
        
        st.success("🎬 动画播放完成！")
    
    elif step_btn:
        st.session_state.anim_step = (st.session_state.anim_step + 1) % len(steps)
        step = steps[st.session_state.anim_step]
        fig = create_blockchain_viz(
            step['public'], step['private'],
            step['info'], step.get('action')
        )
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        
        progress_placeholder.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <span style="font-family: 'JetBrains Mono'; color: #94a3b8;">
                步骤 {st.session_state.anim_step + 1} / {len(steps)}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        step = steps[0]
        fig = create_blockchain_viz(step['public'], step['private'], step['info'])
        chart_placeholder.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 攻击原理说明
    st.markdown('<div class="section-title">📚 攻击原理</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🔄</span>
            <div class="feature-title">Adopt (采纳)</div>
            <div class="feature-desc">
                放弃私有链，采用公共链<br>
                <span style="color: #64748b;">当私有链落后太多时的止损策略</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📢</span>
            <div class="feature-title">Override (覆盖)</div>
            <div class="feature-desc">
                发布私有链，覆盖公共链<br>
                <span style="color: #64748b;">当私有链更长时的获利时机</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">⏳</span>
            <div class="feature-title">Wait (等待)</div>
            <div class="feature-desc">
                继续隐藏私有链<br>
                <span style="color: #64748b;">积累优势，等待最佳发布时机</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 统计数据
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 攻击统计（理论值）</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.3); 
                border-radius: 12px; padding: 0.75rem; margin-bottom: 1rem;">
        <span style="color: #a855f7;">💡 提示：</span>
        <span style="color: #94a3b8;">以下数据为理论分析值，实际结果可能因协议、算力分布等因素有所差异</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = [
        ("~65%", "攻击成功率", "在最优策略下（理论）"),
        ("+12.7%", "收益增幅", "相比诚实挖矿（理论）"),
        ("25%", "最小有效算力", "攻击开始有利（理论）"),
        ("33.3%", "绝对优势阈值", "攻击总是最优（理论）")
    ]
    
    for col, (value, label, desc) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
                <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.3rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    render()
