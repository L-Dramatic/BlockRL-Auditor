"""
页面5: Block Withholding 博弈 - 精致版
- 矿池博弈可视化
- 纳什均衡收敛动画
- 策略对比分析
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots
import time


def calculate_pool_rewards(x1, x2, alpha1=0.3, alpha2=0.3):
    """计算两个矿池在 Block Withholding 攻击中的收益"""
    effective1 = alpha1 * (1 - x1)
    effective2 = alpha2 * (1 - x2)
    total_effective = effective1 + effective2 + (1 - alpha1 - alpha2)
    
    if total_effective <= 0:
        return alpha1, alpha2
    
    pool1_self = effective1 / total_effective
    pool1_steal = alpha1 * x1 * (effective2 / total_effective) if effective2 > 0 else 0
    
    pool2_self = effective2 / total_effective
    pool2_steal = alpha2 * x2 * (effective1 / total_effective) if effective1 > 0 else 0
    
    reward1 = pool1_self + pool1_steal - alpha2 * x2 * pool1_self
    reward2 = pool2_self + pool2_steal - alpha1 * x1 * pool2_self
    
    return max(0, reward1), max(0, reward2)


def find_nash_equilibrium(alpha1=0.3, alpha2=0.3, iterations=100):
    """通过迭代找到纳什均衡点"""
    x1_history = [0.0]
    x2_history = [0.0]
    reward1_history = []
    reward2_history = []
    
    x1, x2 = 0.0, 0.0
    learning_rate = 0.1
    
    for _ in range(iterations):
        r1, r2 = calculate_pool_rewards(x1, x2, alpha1, alpha2)
        reward1_history.append(r1)
        reward2_history.append(r2)
        
        best_x1, best_r1 = x1, r1
        for test_x1 in np.linspace(0, 0.5, 20):
            test_r1, _ = calculate_pool_rewards(test_x1, x2, alpha1, alpha2)
            if test_r1 > best_r1:
                best_r1 = test_r1
                best_x1 = test_x1
        
        best_x2, best_r2 = x2, r2
        for test_x2 in np.linspace(0, 0.5, 20):
            _, test_r2 = calculate_pool_rewards(x1, test_x2, alpha1, alpha2)
            if test_r2 > best_r2:
                best_r2 = test_r2
                best_x2 = test_x2
        
        x1 = x1 + learning_rate * (best_x1 - x1)
        x2 = x2 + learning_rate * (best_x2 - x2)
        
        x1_history.append(x1)
        x2_history.append(x2)
    
    return x1_history, x2_history, reward1_history, reward2_history


def render():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="page-title">⚔️ Block Withholding 博弈</h1>
        <p class="page-subtitle">可视化矿池之间的扣块攻击博弈过程与纳什均衡</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 博弈介绍
    with st.expander("📚 什么是 Block Withholding 攻击？", expanded=False):
        st.markdown("""
        <div style="padding: 1rem; color: #e2e8f0;">
        <b>Block Withholding (扣块攻击)</b> 是矿池之间的一种博弈攻击：
        
        <br><br>
        <b>1. 攻击方式</b>：矿池 A 派遣部分算力加入矿池 B，但只提交部分工作量证明（PoW），而隐藏找到的区块
        <br><br>
        <b>2. 攻击效果</b>：
        <ul>
        <li>矿池 B 的实际出块率降低</li>
        <li>矿池 A 从矿池 B 分得奖励（作为"矿工"）</li>
        <li>矿池 A 自己的挖矿不受影响</li>
        </ul>
        <br>
        <b>3. 博弈困境</b>：如果两个矿池互相攻击，可能形成纳什均衡，双方都受损
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 参数设置
    st.markdown('<div class="section-title">⚙️ 矿池参数配置</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem;">🔵</span>
            <span style="color: #3b82f6; font-weight: 600;">矿池 1</span>
        </div>
        """, unsafe_allow_html=True)
        alpha1 = st.slider(
            "矿池1算力占比",
            min_value=0.1,
            max_value=0.4,
            value=0.3,
            step=0.05,
            key="bw_alpha1",
            label_visibility="collapsed"
        )
        st.markdown(f'<div style="text-align: center; color: #3b82f6; font-size: 1.5rem; font-weight: bold;">{alpha1:.0%}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem;">🔴</span>
            <span style="color: #ef4444; font-weight: 600;">矿池 2</span>
        </div>
        """, unsafe_allow_html=True)
        alpha2 = st.slider(
            "矿池2算力占比",
            min_value=0.1,
            max_value=0.4,
            value=0.3,
            step=0.05,
            key="bw_alpha2",
            label_visibility="collapsed"
        )
        st.markdown(f'<div style="text-align: center; color: #ef4444; font-size: 1.5rem; font-weight: bold;">{alpha2:.0%}</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem;">⚪</span>
            <span style="color: #64748b; font-weight: 600;">散户</span>
        </div>
        """, unsafe_allow_html=True)
        remaining = 1 - alpha1 - alpha2
        st.markdown(f'<div style="text-align: center; color: #64748b; font-size: 1.5rem; font-weight: bold; margin-top: 2rem;">{remaining:.0%}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 博弈收敛
    st.markdown('<div class="section-title">🎬 博弈收敛过程</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        play_animation = st.button("▶️ 播放动画", type="primary", use_container_width=True)
    with col2:
        iterations = st.number_input("迭代次数", min_value=20, max_value=200, value=50, label_visibility="collapsed")
    
    # 计算纳什均衡
    x1_history, x2_history, r1_history, r2_history = find_nash_equilibrium(
        alpha1, alpha2, int(iterations)
    )
    
    chart_placeholder = st.empty()
    metrics_placeholder = st.empty()
    
    if play_animation:
        progress_bar = st.progress(0)
        
        for i in range(0, len(x1_history), max(1, len(x1_history)//30)):
            progress_bar.progress((i + 1) / len(x1_history))
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('策略空间轨迹', '策略演化', '收益变化', '算力分配'),
                specs=[
                    [{"type": "scatter"}, {"type": "scatter"}],
                    [{"type": "scatter"}, {"type": "pie"}]
                ]
            )
            
            # 1. 策略空间轨迹
            fig.add_trace(
                go.Scatter(
                    x=x1_history[:i+1], y=x2_history[:i+1],
                    mode='lines+markers',
                    line=dict(color='#8b5cf6', width=2),
                    marker=dict(size=6, color='#8b5cf6'),
                    showlegend=False
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=[x1_history[i]], y=[x2_history[i]],
                    mode='markers',
                    marker=dict(size=15, color='#f472b6', symbol='star'),
                    showlegend=False
                ),
                row=1, col=1
            )
            
            # 2. 策略演化
            fig.add_trace(
                go.Scatter(x=list(range(i+1)), y=x1_history[:i+1],
                          mode='lines', line=dict(color='#3b82f6', width=2),
                          name='x1', showlegend=False),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(x=list(range(i+1)), y=x2_history[:i+1],
                          mode='lines', line=dict(color='#ef4444', width=2),
                          name='x2', showlegend=False),
                row=1, col=2
            )
            
            # 3. 收益变化
            if i > 0:
                fig.add_trace(
                    go.Scatter(x=list(range(min(i, len(r1_history)))), 
                              y=r1_history[:min(i, len(r1_history))],
                              mode='lines', line=dict(color='#3b82f6', width=2),
                              showlegend=False),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=list(range(min(i, len(r2_history)))), 
                              y=r2_history[:min(i, len(r2_history))],
                              mode='lines', line=dict(color='#ef4444', width=2),
                              showlegend=False),
                    row=2, col=1
                )
            
            # 4. 饼图
            fig.add_trace(
                go.Pie(
                    values=[alpha1*(1-x1_history[i]), alpha1*x1_history[i], 
                           alpha2*(1-x2_history[i]), alpha2*x2_history[i], remaining],
                    labels=['P1挖矿', 'P1渗透', 'P2挖矿', 'P2渗透', '散户'],
                    marker_colors=['#3b82f6', '#93c5fd', '#ef4444', '#fca5a5', '#64748b'],
                    textinfo='percent',
                    textfont=dict(color='white')
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                height=550,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30,30,63,0.4)',
                font=dict(family='Inter', color='#e2e8f0'),
                showlegend=False
            )
            fig.update_xaxes(gridcolor='rgba(139,92,246,0.1)', tickfont=dict(color='#94a3b8'))
            fig.update_yaxes(gridcolor='rgba(139,92,246,0.1)', tickfont=dict(color='#94a3b8'))
            fig.update_annotations(font=dict(color='#e2e8f0', size=12))
            
            chart_placeholder.plotly_chart(fig, use_container_width=True)
            
            with metrics_placeholder.container():
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.5rem;">
                        <div style="color: #64748b; font-size: 0.7rem;">迭代</div>
                        <div style="color: #e2e8f0; font-size: 1.2rem; font-weight: bold;">{i}/{len(x1_history)-1}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.5rem;">
                        <div style="color: #3b82f6; font-size: 0.7rem;">x1 (矿池1)</div>
                        <div style="color: #3b82f6; font-size: 1.2rem; font-weight: bold;">{x1_history[i]:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m3:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.5rem;">
                        <div style="color: #ef4444; font-size: 0.7rem;">x2 (矿池2)</div>
                        <div style="color: #ef4444; font-size: 1.2rem; font-weight: bold;">{x2_history[i]:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m4:
                    conv = abs(x1_history[i]-x1_history[max(0,i-1)])+abs(x2_history[i]-x2_history[max(0,i-1)]) if i > 0 else 1
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.5rem;">
                        <div style="color: #22c55e; font-size: 0.7rem;">收敛度</div>
                        <div style="color: #22c55e; font-size: 1.2rem; font-weight: bold;">{conv:.4f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            time.sleep(0.08)
        
        progress_bar.empty()
        st.success("✅ 博弈收敛完成！")
    
    else:
        # 显示最终状态
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('策略空间轨迹', '策略演化', '收益变化', '最终算力分配'),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "pie"}]
            ]
        )
        
        # 完整轨迹
        fig.add_trace(
            go.Scatter(x=x1_history, y=x2_history, mode='lines+markers',
                      line=dict(color='#8b5cf6', width=2), marker=dict(size=4),
                      showlegend=False),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=[x1_history[0]], y=[x2_history[0]], mode='markers',
                      marker=dict(size=12, color='#22c55e', symbol='circle'),
                      name='起点', showlegend=False),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=[x1_history[-1]], y=[x2_history[-1]], mode='markers',
                      marker=dict(size=15, color='#f472b6', symbol='star'),
                      name='纳什均衡', showlegend=False),
            row=1, col=1
        )
        
        # 策略演化
        fig.add_trace(
            go.Scatter(x=list(range(len(x1_history))), y=x1_history,
                      mode='lines', line=dict(color='#3b82f6', width=2), showlegend=False),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=list(range(len(x2_history))), y=x2_history,
                      mode='lines', line=dict(color='#ef4444', width=2), showlegend=False),
            row=1, col=2
        )
        
        # 收益变化
        fig.add_trace(
            go.Scatter(x=list(range(len(r1_history))), y=r1_history,
                      mode='lines', line=dict(color='#3b82f6', width=2), showlegend=False),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=list(range(len(r2_history))), y=r2_history,
                      mode='lines', line=dict(color='#ef4444', width=2), showlegend=False),
            row=2, col=1
        )
        
        # 饼图
        fig.add_trace(
            go.Pie(
                values=[alpha1*(1-x1_history[-1]), alpha1*x1_history[-1], 
                       alpha2*(1-x2_history[-1]), alpha2*x2_history[-1], remaining],
                labels=['P1挖矿', 'P1渗透', 'P2挖矿', 'P2渗透', '散户'],
                marker_colors=['#3b82f6', '#93c5fd', '#ef4444', '#fca5a5', '#64748b'],
                textinfo='percent+label',
                textfont=dict(color='white', size=10)
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=550,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(30,30,63,0.4)',
            font=dict(family='Inter', color='#e2e8f0'),
            showlegend=False
        )
        fig.update_xaxes(gridcolor='rgba(139,92,246,0.1)', tickfont=dict(color='#94a3b8'))
        fig.update_yaxes(gridcolor='rgba(139,92,246,0.1)', tickfont=dict(color='#94a3b8'))
        fig.update_annotations(font=dict(color='#e2e8f0', size=12))
        
        chart_placeholder.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 纳什均衡分析
    st.markdown('<div class="section-title">📊 纳什均衡分析</div>', unsafe_allow_html=True)
    
    final_x1 = x1_history[-1]
    final_x2 = x2_history[-1]
    final_r1 = r1_history[-1] if r1_history else alpha1
    final_r2 = r2_history[-1] if r2_history else alpha2
    
    col1, col2 = st.columns(2)
    
    with col1:
        gain1 = (final_r1 - alpha1) / alpha1 * 100 if alpha1 > 0 else 0
        st.markdown(f"""
        <div class="glass-card" style="border-color: rgba(59,130,246,0.4);">
            <div style="text-align: center; margin-bottom: 1rem;">
                <span style="font-size: 2rem;">🔵</span>
                <div style="color: #3b82f6; font-size: 1.3rem; font-weight: 600;">矿池 1</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.8rem;">均衡渗透率</div>
                    <div style="color: #3b82f6; font-size: 1.5rem; font-weight: bold;">{final_x1:.3f}</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.8rem;">均衡收益</div>
                    <div style="color: #3b82f6; font-size: 1.5rem; font-weight: bold;">{final_r1:.4f}</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(59,130,246,0.2);">
                <span style="color: #64748b;">vs 诚实挖矿: </span>
                <span style="color: {'#22c55e' if gain1 >= 0 else '#ef4444'}; font-weight: bold;">{gain1:+.2f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        gain2 = (final_r2 - alpha2) / alpha2 * 100 if alpha2 > 0 else 0
        st.markdown(f"""
        <div class="glass-card" style="border-color: rgba(239,68,68,0.4);">
            <div style="text-align: center; margin-bottom: 1rem;">
                <span style="font-size: 2rem;">🔴</span>
                <div style="color: #ef4444; font-size: 1.3rem; font-weight: 600;">矿池 2</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.8rem;">均衡渗透率</div>
                    <div style="color: #ef4444; font-size: 1.5rem; font-weight: bold;">{final_x2:.3f}</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.8rem;">均衡收益</div>
                    <div style="color: #ef4444; font-size: 1.5rem; font-weight: bold;">{final_r2:.4f}</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(239,68,68,0.2);">
                <span style="color: #64748b;">vs 诚实挖矿: </span>
                <span style="color: {'#22c55e' if gain2 >= 0 else '#ef4444'}; font-weight: bold;">{gain2:+.2f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # 博弈结论
    st.markdown('<div class="section-title">💡 博弈结论</div>', unsafe_allow_html=True)
    
    total_loss = (alpha1 + alpha2) - (final_r1 + final_r2)
    
    if total_loss > 0.01:
        st.markdown(f"""
        <div class="glass-card" style="border-color: rgba(251,191,36,0.4); background: rgba(251,191,36,0.05);">
            <div style="color: #fbbf24; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">
                ⚠️ 囚徒困境
            </div>
            <div style="color: #94a3b8; line-height: 1.8;">
                两个矿池在纳什均衡下互相攻击，导致：<br><br>
                • 总收益损失: <b style="color: #ef4444;">{total_loss:.4f}</b> ({total_loss/(alpha1+alpha2)*100:.1f}%)<br>
                • 这是典型的「囚徒困境」——双方都选择攻击，但结果比合作更差<br>
                • 第三方诚实矿工（散户）反而从中受益<br><br>
                <span style="color: #fbbf24;">💡 启示：矿池间的博弈攻击最终可能导致两败俱伤</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="glass-card" style="border-color: rgba(34,197,94,0.4); background: rgba(34,197,94,0.05);">
            <div style="color: #22c55e; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">
                ✅ 合作均衡
            </div>
            <div style="color: #94a3b8; line-height: 1.8;">
                在当前参数下，双方倾向于合作（不攻击）：<br><br>
                • 攻击收益不足以弥补算力浪费<br>
                • 诚实挖矿是最优策略<br>
                • 市场处于健康的竞争状态
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    render()
