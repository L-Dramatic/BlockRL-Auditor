"""
生成 Bitcoin vs GHOST vs Ethereum 三协议对比图
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


def plot_three_protocols(bitcoin_csv, ghost_csv, ethereum_csv, output_path="./results/three_protocols_comparison.png"):
    """生成三协议对比图"""
    
    # 加载数据
    bitcoin_results = load_results(bitcoin_csv)
    ghost_results = load_results(ghost_csv)
    ethereum_results = load_results(ethereum_csv)
    
    # 提取数据
    bitcoin_alphas = [r['alpha'] for r in bitcoin_results]
    bitcoin_rewards = [r['relative_gain'] for r in bitcoin_results]
    bitcoin_stds = [r['std_reward_fraction'] for r in bitcoin_results]
    
    ghost_alphas = [r['alpha'] for r in ghost_results]
    ghost_rewards = [r['relative_gain'] for r in ghost_results]
    ghost_stds = [r['std_reward_fraction'] for r in ghost_results]
    
    ethereum_alphas = [r['alpha'] for r in ethereum_results]
    ethereum_rewards = [r['relative_gain'] for r in ethereum_results]
    ethereum_stds = [r['std_reward_fraction'] for r in ethereum_results]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 绘制诚实基准线
    x_range = np.linspace(0, 0.5, 100)
    ax.plot(x_range, x_range, 'k--', linewidth=2, label='Honest Mining (y=α)', alpha=0.7)
    
    # 理论最优曲线
    theory_alphas = x_range[x_range >= 1/3]
    theory_rewards = (theory_alphas * (1 - theory_alphas)) / (1 - 2*theory_alphas + theory_alphas**2)
    ax.plot(theory_alphas, theory_rewards, 'gray', linestyle='-.', linewidth=2, 
            label='Theoretical Optimal', alpha=0.6)
    
    # 绘制 Bitcoin 结果
    ax.errorbar(bitcoin_alphas, bitcoin_rewards, yerr=bitcoin_stds, 
                fmt='o-', color='#2196F3', linewidth=2.5, markersize=9,
                capsize=5, capthick=2, label='Bitcoin', alpha=0.9)
    
    # 绘制 GHOST 结果  
    ax.errorbar(ghost_alphas, ghost_rewards, yerr=ghost_stds,
                fmt='s-', color='#FF5722', linewidth=2.5, markersize=9,
                capsize=5, capthick=2, label='GHOST', alpha=0.9)
    
    # 绘制 Ethereum 结果
    ax.errorbar(ethereum_alphas, ethereum_rewards, yerr=ethereum_stds,
                fmt='^-', color='#4CAF50', linewidth=2.5, markersize=9,
                capsize=5, capthick=2, label='Ethereum', alpha=0.9)
    
    # 设置图表属性
    ax.set_xlabel('Attacker Hash Power (α)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Relative Reward', fontsize=14, fontweight='bold')
    ax.set_title('Selfish Mining: Bitcoin vs GHOST vs Ethereum', fontsize=16, fontweight='bold')
    ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(0.2, 0.5)
    ax.set_ylim(0.2, 0.65)
    
    # 添加关键点标注
    ax.axvline(x=1/3, color='red', linestyle=':', linewidth=1.5, alpha=0.5)
    ax.text(1/3, 0.22, 'Threshold\n(α=1/3)', ha='center', fontsize=10, 
            color='red', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # 保存
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 三协议对比图已保存到: {output_path}")
    
    # 也保存 PDF 版本
    pdf_path = output_path.replace('.png', '.pdf')
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    print(f"✅ PDF 版本已保存到: {pdf_path}")
    
    plt.close()
    
    # 打印对比分析
    print("\n" + "="*80)
    print("📊 Bitcoin vs GHOST vs Ethereum 对比分析")
    print("="*80)
    print(f"\n{'α':<8} {'Bitcoin':<12} {'GHOST':<12} {'Ethereum':<12} {'最安全协议':<15}")
    print("-" * 80)
    
    for ba, br in zip(bitcoin_alphas, bitcoin_rewards):
        gr = next((r for a, r in zip(ghost_alphas, ghost_rewards) if abs(a - ba) < 0.01), None)
        er = next((r for a, r in zip(ethereum_alphas, ethereum_rewards) if abs(a - ba) < 0.01), None)
        
        if gr is not None and er is not None:
            min_reward = min(br, gr, er)
            safest = "Bitcoin" if br == min_reward else ("GHOST" if gr == min_reward else "Ethereum")
            print(f"{ba:<8.2f} {br:<12.4f} {gr:<12.4f} {er:<12.4f} {safest:<15}")
    
    print("-" * 80)
    print("\n💡 结论：")
    print("  - 相对奖励越低，协议越安全（攻击者获利越少）")
    print("  - 可以看出不同协议在不同算力下的安全性表现")


def main():
    bitcoin_csv = "./results/bitcoin_full_evaluation.csv"
    ghost_csv = "./results/ghost_full_evaluation.csv"
    ethereum_csv = "./results/ethereum_full_evaluation.csv"
    
    # 检查文件是否存在
    if not os.path.exists(bitcoin_csv):
        print(f"❌ 未找到 Bitcoin 评估结果: {bitcoin_csv}")
        return
    
    if not os.path.exists(ghost_csv):
        print(f"❌ 未找到 GHOST 评估结果: {ghost_csv}")
        return
    
    if not os.path.exists(ethereum_csv):
        print(f"❌ 未找到 Ethereum 评估结果: {ethereum_csv}")
        print("请先运行: python scripts/batch_evaluate_ethereum.py")
        return
    
    plot_three_protocols(bitcoin_csv, ghost_csv, ethereum_csv)


if __name__ == "__main__":
    main()

