"""
生成 Bitcoin vs GHOST 协议对比图
"""

import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_results(csv_path):
    """从 CSV 加载评估结果"""
    results = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['alpha'] = float(row['alpha'])
            row['relative_gain'] = float(row.get('relative_gain', row.get('mean_reward_fraction', 0)))
            row['std_reward_fraction'] = float(row.get('std_reward_fraction', 0))
            results.append(row)
    return sorted(results, key=lambda x: x['alpha'])


def plot_bitcoin_vs_ghost(bitcoin_csv, ghost_csv, output_path="./results/bitcoin_vs_ghost.png"):
    """生成 Bitcoin vs GHOST 对比图"""
    
    # 加载数据
    bitcoin_results = load_results(bitcoin_csv)
    ghost_results = load_results(ghost_csv)
    
    # 提取数据
    bitcoin_alphas = [r['alpha'] for r in bitcoin_results]
    bitcoin_rewards = [r['relative_gain'] for r in bitcoin_results]
    bitcoin_stds = [r['std_reward_fraction'] for r in bitcoin_results]
    
    ghost_alphas = [r['alpha'] for r in ghost_results]
    ghost_rewards = [r['relative_gain'] for r in ghost_results]
    ghost_stds = [r['std_reward_fraction'] for r in ghost_results]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 绘制诚实基准线
    x_range = np.linspace(0, 0.5, 100)
    ax.plot(x_range, x_range, 'k--', linewidth=2, label='Honest Mining (y=α)', alpha=0.7)
    
    # 理论最优曲线（来自 Eyal & Sirer 论文）
    theory_alphas = x_range[x_range >= 1/3]
    theory_rewards = (theory_alphas * (1 - theory_alphas)) / (1 - 2*theory_alphas + theory_alphas**2)
    ax.plot(theory_alphas, theory_rewards, 'g-.', linewidth=2, 
            label='Theoretical Optimal (Bitcoin)', alpha=0.7)
    
    # 绘制 Bitcoin 结果
    ax.errorbar(bitcoin_alphas, bitcoin_rewards, yerr=bitcoin_stds, 
                fmt='o-', color='#2196F3', linewidth=2, markersize=8,
                capsize=4, capthick=2, label='Bitcoin (DRL)', alpha=0.9)
    
    # 绘制 GHOST 结果  
    ax.errorbar(ghost_alphas, ghost_rewards, yerr=ghost_stds,
                fmt='s-', color='#FF5722', linewidth=2, markersize=8,
                capsize=4, capthick=2, label='GHOST (DRL)', alpha=0.9)
    
    # 设置图表属性
    ax.set_xlabel('Attacker Hash Power (α)', fontsize=12)
    ax.set_ylabel('Relative Reward', fontsize=12)
    ax.set_title('Selfish Mining: Bitcoin vs GHOST Protocol', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.2, 0.5)
    ax.set_ylim(0.2, 0.7)
    
    # 添加注释
    ax.annotate('Selfish mining\nbecomes profitable', 
                xy=(0.33, 0.33), xytext=(0.28, 0.45),
                arrowprops=dict(arrowstyle='->', color='gray'),
                fontsize=9, color='gray')
    
    plt.tight_layout()
    
    # 保存
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 对比图已保存到: {output_path}")
    
    # 也保存 PDF 版本
    pdf_path = output_path.replace('.png', '.pdf')
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    print(f"✅ PDF 版本已保存到: {pdf_path}")
    
    plt.close()
    
    # 打印对比分析
    print("\n" + "="*60)
    print("📊 Bitcoin vs GHOST 对比分析")
    print("="*60)
    print(f"\n{'α':<8} {'Bitcoin':<12} {'GHOST':<12} {'差异':<12}")
    print("-" * 50)
    
    for ba, br in zip(bitcoin_alphas, bitcoin_rewards):
        # 找到对应的 GHOST 结果
        ghost_r = next((gr for ga, gr in zip(ghost_alphas, ghost_rewards) if abs(ga - ba) < 0.01), None)
        if ghost_r is not None:
            diff = br - ghost_r
            print(f"{ba:<8.2f} {br:<12.4f} {ghost_r:<12.4f} {diff:+.4f}")
    
    print("-" * 50)
    print("\n💡 分析结论：")
    print("  - 如果 GHOST 收益 < Bitcoin：GHOST 协议更安全")
    print("  - 如果 GHOST 收益 ≈ Bitcoin：两者抗自私挖矿能力相当")
    print("  - 如果 GHOST 收益 > Bitcoin：GHOST 更容易被攻击")


def main():
    bitcoin_csv = "./results/bitcoin_full_evaluation.csv"
    ghost_csv = "./results/ghost_full_evaluation.csv"
    
    # 检查文件是否存在
    if not os.path.exists(bitcoin_csv):
        print(f"❌ 未找到 Bitcoin 评估结果: {bitcoin_csv}")
        print("请先运行: python scripts/batch_evaluate.py")
        return
    
    if not os.path.exists(ghost_csv):
        print(f"❌ 未找到 GHOST 评估结果: {ghost_csv}")
        print("请先运行: python scripts/batch_evaluate_ghost.py")
        return
    
    plot_bitcoin_vs_ghost(bitcoin_csv, ghost_csv)


if __name__ == "__main__":
    main()

