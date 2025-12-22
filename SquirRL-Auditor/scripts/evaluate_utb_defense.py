"""
评估 UTB 防御机制的效果
对比不同 UTB 参数下自私挖矿的收益
"""

import os
import sys
import glob
import re
import csv
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.evaluate import evaluate_model


def find_utb_models(base_dir="./models"):
    """查找所有 UTB 模型"""
    models = []
    
    # 查找 best_utb_* 模型
    pattern = os.path.join(base_dir, "best_utb_*", "best_model.zip")
    model_paths = glob.glob(pattern)
    
    for model_path in model_paths:
        # 从目录名提取参数
        dir_name = os.path.basename(os.path.dirname(model_path))
        # 格式: best_utb_alpha_0.35_ratio_0.50_YYYYMMDD_HHMMSS
        
        alpha_match = re.search(r'alpha_([0-9.]+)', dir_name)
        ratio_match = re.search(r'ratio_([0-9.]+)', dir_name)
        
        if alpha_match and ratio_match:
            alpha = float(alpha_match.group(1))
            utb_ratio = float(ratio_match.group(1))
            models.append((alpha, utb_ratio, model_path))
    
    return sorted(models, key=lambda x: (x[0], x[1]))


def evaluate_utb_defense():
    """评估 UTB 防御效果"""
    
    print("="*60)
    print("评估 UTB Defense 防御效果")
    print("="*60)
    
    models = find_utb_models()
    
    if not models:
        print("❌ 未找到任何 UTB 模型！")
        print("请先运行: python scripts/train_utb_defense.py")
        return
    
    print(f"\n找到 {len(models)} 个模型：")
    for alpha, utb_ratio, path in models:
        print(f"  α={alpha:.2f}, UTB={utb_ratio:.2f}: {os.path.basename(path)}")
    
    print("\n开始评估...")
    print("="*60)
    
    results = []
    
    for i, (alpha, utb_ratio, model_path) in enumerate(models, 1):
        print(f"\n[{i}/{len(models)}] 评估 α={alpha:.2f}, UTB={utb_ratio:.2f}...")
        
        try:
            result = evaluate_model(
                model_path=model_path,
                protocol="utb",
                alpha=alpha,
                gamma=0.5,
                utb_ratio=utb_ratio,
                n_episodes=50,
                verbose=1
            )
            result['utb_ratio'] = utb_ratio
            results.append(result)
            print(f"✅ 完成: 相对奖励 = {result['mean_reward_fraction']:.4f}")
        except Exception as e:
            print(f"❌ 评估失败: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not results:
        print("\n❌ 没有成功评估的模型！")
        return
    
    # 保存结果到 CSV
    output_csv = "./results/utb_defense_evaluation.csv"
    os.makedirs("./results", exist_ok=True)
    
    with open(output_csv, 'w', newline='') as f:
        fieldnames = ['protocol', 'alpha', 'gamma', 'utb_ratio', 'n_episodes',
                      'mean_reward', 'std_reward', 'mean_reward_fraction', 
                      'std_reward_fraction', 'honest_baseline', 'relative_gain', 'excess_reward']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            writer.writerow({
                'protocol': r['protocol'],
                'alpha': r['alpha'],
                'gamma': r['gamma'],
                'utb_ratio': r['utb_ratio'],
                'n_episodes': r['n_episodes'],
                'mean_reward': r['mean_reward'],
                'std_reward': r['std_reward'],
                'mean_reward_fraction': r['mean_reward_fraction'],
                'std_reward_fraction': r['std_reward_fraction'],
                'honest_baseline': r['honest_baseline'],
                'relative_gain': r['relative_gain'],
                'excess_reward': r['excess_reward']
            })
    
    print(f"\n结果已保存到: {output_csv}")
    
    # 打印摘要
    print("\n" + "="*60)
    print("📊 UTB 防御效果摘要")
    print("="*60)
    print(f"\n{'UTB比率':<10} {'相对奖励':<12} {'超额收益':<12} {'防御效果':<12}")
    print("-" * 50)
    
    for r in results:
        utb_ratio = r['utb_ratio']
        reward = r['mean_reward_fraction']
        excess = r['excess_reward']
        print(f"{utb_ratio:<10.2f} {reward:<12.4f} {excess:+12.4f}")
    
    print("-" * 50)
    
    # 生成可视化
    plot_utb_defense(results)
    
    print("\n💡 分析：")
    print("  - UTB 比率越高，攻击者超额收益越低")
    print("  - 理想情况：UTB=1.0 应该使超额收益≈0")
    print("  - 如果 UTB=1.0 仍有正收益，说明防御不完全有效")


def plot_utb_defense(results):
    """绘制 UTB 防御效果图"""
    
    # 按 UTB 比率排序
    results = sorted(results, key=lambda x: x['utb_ratio'])
    
    utb_ratios = [r['utb_ratio'] for r in results]
    rewards = [r['mean_reward_fraction'] for r in results]
    stds = [r['std_reward_fraction'] for r in results]
    alpha = results[0]['alpha']
    honest_baseline = alpha
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 左图：相对奖励 vs UTB 比率
    ax1.errorbar(utb_ratios, rewards, yerr=stds, 
                 fmt='o-', color='#2196F3', linewidth=2, markersize=8,
                 capsize=4, capthick=2, label='Attacker Reward')
    ax1.axhline(y=honest_baseline, color='red', linestyle='--', 
                linewidth=2, label=f'Honest Mining (α={alpha})')
    ax1.set_xlabel('UTB Ratio', fontsize=12)
    ax1.set_ylabel('Relative Reward', fontsize=12)
    ax1.set_title(f'UTB Defense Effect (α={alpha})', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(min(rewards) - 0.05, max(max(rewards), honest_baseline) + 0.05)
    
    # 右图：超额收益 vs UTB 比率
    excess_rewards = [r['excess_reward'] for r in results]
    colors = ['red' if e > 0 else 'green' for e in excess_rewards]
    
    ax2.bar(utb_ratios, excess_rewards, color=colors, alpha=0.7, width=0.08)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('UTB Ratio', fontsize=12)
    ax2.set_ylabel('Excess Reward', fontsize=12)
    ax2.set_title('Defense Effectiveness', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for i, (ratio, excess) in enumerate(zip(utb_ratios, excess_rewards)):
        ax2.text(ratio, excess + 0.002 if excess > 0 else excess - 0.002,
                f'{excess:+.3f}', ha='center', va='bottom' if excess > 0 else 'top',
                fontsize=9)
    
    plt.tight_layout()
    
    # 保存
    output_png = "./results/utb_defense_effect.png"
    output_pdf = "./results/utb_defense_effect.pdf"
    
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.savefig(output_pdf, format='pdf', bbox_inches='tight')
    
    print(f"\n✅ 防御效果图已保存:")
    print(f"  PNG: {output_png}")
    print(f"  PDF: {output_pdf}")
    
    plt.close()


if __name__ == "__main__":
    evaluate_utb_defense()

