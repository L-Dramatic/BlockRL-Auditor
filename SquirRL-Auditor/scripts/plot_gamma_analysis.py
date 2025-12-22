"""
Gamma参数分析 - 可视化图表
展示不同gamma值对攻击收益的影响
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pathlib import Path

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 评估结果数据（从终端输出提取）
GAMMA_VALUES = [0.0, 0.25, 0.5, 0.75, 1.0]
REWARD_FRACTIONS = [0.3479, 0.3485, 0.3537, 0.4263, 0.4808]
ALPHA = 0.35

def plot_gamma_analysis():
    """绘制Gamma分析图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 计算超额收益
    excess_rewards = [r - ALPHA for r in REWARD_FRACTIONS]
    
    # 左图：收益率 vs Gamma
    ax1.plot(GAMMA_VALUES, REWARD_FRACTIONS, 'b-o', linewidth=2, markersize=10, label='Experimental')
    ax1.axhline(y=ALPHA, color='r', linestyle='--', linewidth=2, label=f'Honest Mining (α={ALPHA})')
    
    # 填充盈利区域
    ax1.fill_between(GAMMA_VALUES, ALPHA, REWARD_FRACTIONS, 
                     where=[r > ALPHA for r in REWARD_FRACTIONS],
                     color='green', alpha=0.3, label='Profit Zone')
    ax1.fill_between(GAMMA_VALUES, ALPHA, REWARD_FRACTIONS,
                     where=[r <= ALPHA for r in REWARD_FRACTIONS],
                     color='red', alpha=0.3, label='Loss Zone')
    
    ax1.set_xlabel('Gamma (γ) - Follower Fraction', fontsize=12)
    ax1.set_ylabel('Reward Fraction', fontsize=12)
    ax1.set_title('Selfish Mining Reward vs Follower Fraction\n(Bitcoin, α=0.35)', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(-0.05, 1.05)
    ax1.set_ylim(0.3, 0.55)
    
    # 添加数据标签
    for i, (g, r) in enumerate(zip(GAMMA_VALUES, REWARD_FRACTIONS)):
        offset = 0.015 if r > ALPHA else -0.02
        ax1.annotate(f'{r:.4f}', (g, r + offset), ha='center', fontsize=9)
    
    # 右图：超额收益柱状图
    colors = ['green' if e > 0 else 'red' for e in excess_rewards]
    bars = ax2.bar(GAMMA_VALUES, [e * 100 for e in excess_rewards], 
                   width=0.15, color=colors, edgecolor='black', alpha=0.7)
    
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('Gamma (γ) - Follower Fraction', fontsize=12)
    ax2.set_ylabel('Excess Reward (%)', fontsize=12)
    ax2.set_title('Excess Reward over Honest Mining\n(Bitcoin, α=0.35)', fontsize=14)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xlim(-0.15, 1.15)
    
    # 添加数据标签
    for bar, e in zip(bars, excess_rewards):
        height = bar.get_height()
        offset = 0.5 if height > 0 else -1.5
        ax2.annotate(f'{e*100:+.2f}%', 
                     xy=(bar.get_x() + bar.get_width()/2, height + offset),
                     ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    # 保存图表
    output_path = PROJECT_ROOT / "results" / "gamma_analysis.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"[OK] Gamma analysis chart saved to: {output_path}")
    
    # 保存PDF版本
    pdf_path = PROJECT_ROOT / "results" / "gamma_analysis.pdf"
    plt.savefig(pdf_path, bbox_inches='tight')
    print(f"[OK] PDF version saved to: {pdf_path}")
    
    plt.show()

def plot_gamma_analysis_chinese():
    """绘制Gamma分析图（中文版）"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 计算超额收益
    excess_rewards = [r - ALPHA for r in REWARD_FRACTIONS]
    
    # 左图：收益率 vs Gamma
    ax1.plot(GAMMA_VALUES, REWARD_FRACTIONS, 'b-o', linewidth=2, markersize=10, label='实验结果')
    ax1.axhline(y=ALPHA, color='r', linestyle='--', linewidth=2, label=f'诚实挖矿基准 (α={ALPHA})')
    
    # 填充盈利区域
    ax1.fill_between(GAMMA_VALUES, ALPHA, REWARD_FRACTIONS, 
                     where=[r > ALPHA for r in REWARD_FRACTIONS],
                     color='green', alpha=0.3, label='盈利区域')
    ax1.fill_between(GAMMA_VALUES, ALPHA, REWARD_FRACTIONS,
                     where=[r <= ALPHA for r in REWARD_FRACTIONS],
                     color='red', alpha=0.3, label='亏损区域')
    
    ax1.set_xlabel('跟随者比例 γ', fontsize=12)
    ax1.set_ylabel('奖励比例', fontsize=12)
    ax1.set_title('自私挖矿收益 vs 跟随者比例\n(Bitcoin协议, α=0.35)', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(-0.05, 1.05)
    ax1.set_ylim(0.3, 0.55)
    
    # 添加数据标签
    for i, (g, r) in enumerate(zip(GAMMA_VALUES, REWARD_FRACTIONS)):
        offset = 0.015 if r > ALPHA else -0.02
        ax1.annotate(f'{r:.4f}', (g, r + offset), ha='center', fontsize=9)
    
    # 右图：超额收益柱状图
    colors = ['green' if e > 0 else 'red' for e in excess_rewards]
    bars = ax2.bar(GAMMA_VALUES, [e * 100 for e in excess_rewards], 
                   width=0.15, color=colors, edgecolor='black', alpha=0.7)
    
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('跟随者比例 γ', fontsize=12)
    ax2.set_ylabel('超额收益 (%)', fontsize=12)
    ax2.set_title('相对于诚实挖矿的超额收益\n(Bitcoin协议, α=0.35)', fontsize=14)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xlim(-0.15, 1.15)
    
    # 添加数据标签
    for bar, e in zip(bars, excess_rewards):
        height = bar.get_height()
        offset = 0.5 if height > 0 else -1.5
        ax2.annotate(f'{e*100:+.2f}%', 
                     xy=(bar.get_x() + bar.get_width()/2, height + offset),
                     ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    # 保存图表
    output_path = PROJECT_ROOT / "results" / "gamma_analysis_cn.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"[OK] Chinese version saved to: {output_path}")
    
    plt.show()

def main():
    print("="*60)
    print("Gamma Analysis - Visualization")
    print("="*60)
    print(f"\nData Summary:")
    print(f"{'Gamma':<10} {'Reward':<12} {'Excess':<12}")
    print("-"*35)
    for g, r in zip(GAMMA_VALUES, REWARD_FRACTIONS):
        excess = r - ALPHA
        print(f"{g:<10} {r:<12.4f} {excess:+.4f}")
    
    print("\nGenerating charts...")
    plot_gamma_analysis()
    plot_gamma_analysis_chinese()
    
    print("\n[OK] All charts generated successfully!")

if __name__ == "__main__":
    main()

