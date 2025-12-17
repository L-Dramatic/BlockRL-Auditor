"""
T7: 可视化脚本
复现论文中的 Figure 3 - 自私挖矿奖励曲线
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端

# 设置中文字体支持（如果需要）
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def theoretical_selfish_mining_reward(alpha, gamma=0.5):
    """
    计算自私挖矿的理论相对奖励
    基于 Eyal & Sirer (2014) 的公式
    
    参数：
        alpha (float): 攻击者算力占比
        gamma (float): 跟随者比例
    
    返回：
        relative_reward (float): 相对奖励（相对于诚实挖矿）
    """
    if alpha >= 0.5:
        return 1.0  # 如果攻击者有超过50%算力，可以获得所有奖励
    
    # 自私挖矿公式
    # R = (alpha * (1 - alpha)^2 * (4*alpha + gamma*(1-2*alpha)) - alpha^3) / 
    #     (1 - alpha * (1 + (2-alpha)*alpha))
    
    numerator = alpha * (1 - alpha)**2 * (4*alpha + gamma*(1 - 2*alpha)) - alpha**3
    denominator = 1 - alpha * (1 + (2 - alpha) * alpha)
    
    if denominator == 0:
        return alpha
    
    relative_reward = numerator / denominator
    return relative_reward


def honest_mining_reward(alpha):
    """诚实挖矿的期望奖励（等于算力占比）"""
    return alpha


def plot_figure3(
    results=None,
    alphas=None,
    rewards=None,
    gamma=0.5,
    title="Bitcoin Selfish Mining: SquirRL vs Theoretical",
    output_path="./results/figure3.png",
    show_theoretical=True,
    show_honest=True,
    figsize=(10, 6)
):
    """
    绘制 Figure 3 风格的奖励曲线图
    
    参数：
        results (list): evaluate_multiple_alphas 返回的结果列表
        alphas (list): alpha值列表（如果不使用results）
        rewards (list): 对应的奖励列表（如果不使用results）
        gamma (float): 跟随者比例
        title (str): 图标题
        output_path (str): 输出路径
        show_theoretical (bool): 是否显示理论曲线
        show_honest (bool): 是否显示诚实挖矿曲线
        figsize (tuple): 图大小
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # 如果提供了results，从中提取数据
    if results is not None:
        alphas = [r['alpha'] for r in results]
        rewards = [r['relative_gain'] for r in results]
    
    # X轴范围
    x_range = np.linspace(0.01, 0.49, 100)
    
    # 1. 绘制诚实挖矿基准线
    if show_honest:
        honest_rewards = [honest_mining_reward(a) for a in x_range]
        ax.plot(x_range, honest_rewards, 'k--', 
                label='Honest Mining', linewidth=2, alpha=0.7)
    
    # 2. 绘制理论最优自私挖矿曲线
    if show_theoretical:
        theoretical_rewards = [theoretical_selfish_mining_reward(a, gamma) 
                              for a in x_range]
        ax.plot(x_range, theoretical_rewards, 'b-', 
                label=f'Theoretical SM (γ={gamma})', linewidth=2)
    
    # 3. 绘制 SquirRL 学习到的策略结果
    if alphas is not None and rewards is not None:
        ax.scatter(alphas, rewards, c='red', s=100, marker='o', 
                   label='SquirRL (DQN)', zorder=5)
        # 添加误差线（如果有）
        if results is not None and 'std_reward' in results[0]:
            stds = [r.get('std_reward', 0) / np.sqrt(r.get('n_episodes', 100)) 
                    for r in results]
            ax.errorbar(alphas, rewards, yerr=stds, fmt='none', 
                       color='red', capsize=3, alpha=0.7)
    
    # 设置图表属性
    ax.set_xlabel('Attacker Hash Power (α)', fontsize=12)
    ax.set_ylabel('Relative Reward', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, 0.6)
    
    # 添加注释
    ax.axhline(y=0.25, color='gray', linestyle=':', alpha=0.5)
    ax.text(0.02, 0.26, 'α=0.25 threshold', fontsize=9, alpha=0.7)
    
    # 保存图片
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"图表已保存到: {output_path}")
    
    # 同时保存为PDF（高质量）
    pdf_path = output_path.replace('.png', '.pdf')
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    print(f"PDF版本已保存到: {pdf_path}")
    
    plt.close()
    
    return fig


def plot_comparison(
    bitcoin_results,
    ghost_results=None,
    title="Bitcoin vs GHOST: Selfish Mining Comparison",
    output_path="./results/comparison.png",
    figsize=(10, 6)
):
    """
    绘制 Bitcoin 和 GHOST 协议的对比图
    
    参数：
        bitcoin_results (list): Bitcoin协议的评估结果
        ghost_results (list): GHOST协议的评估结果
        title (str): 图标题
        output_path (str): 输出路径
        figsize (tuple): 图大小
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # X轴范围
    x_range = np.linspace(0.01, 0.49, 100)
    
    # 诚实挖矿基准线
    honest_rewards = [honest_mining_reward(a) for a in x_range]
    ax.plot(x_range, honest_rewards, 'k--', 
            label='Honest Mining', linewidth=2, alpha=0.7)
    
    # Bitcoin 理论曲线
    bitcoin_theoretical = [theoretical_selfish_mining_reward(a, 0.5) 
                          for a in x_range]
    ax.plot(x_range, bitcoin_theoretical, 'b-', 
            label='Bitcoin Theoretical', linewidth=1.5, alpha=0.5)
    
    # Bitcoin 实验结果
    if bitcoin_results:
        alphas = [r['alpha'] for r in bitcoin_results]
        rewards = [r['relative_gain'] for r in bitcoin_results]
        ax.scatter(alphas, rewards, c='blue', s=80, marker='o', 
                   label='Bitcoin (SquirRL)', zorder=5)
    
    # GHOST 实验结果
    if ghost_results:
        alphas = [r['alpha'] for r in ghost_results]
        rewards = [r['relative_gain'] for r in ghost_results]
        ax.scatter(alphas, rewards, c='green', s=80, marker='s', 
                   label='GHOST (SquirRL)', zorder=5)
    
    # 设置图表属性
    ax.set_xlabel('Attacker Hash Power (α)', fontsize=12)
    ax.set_ylabel('Relative Reward', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, 0.6)
    
    # 保存图片
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"对比图已保存到: {output_path}")
    
    plt.close()
    
    return fig


def plot_training_curve(log_path, output_path="./results/training_curve.png"):
    """
    绘制训练曲线（如果有日志）
    
    参数：
        log_path (str): 日志文件路径
        output_path (str): 输出路径
    """
    # TODO: 从tensorboard日志或monitor日志读取数据
    pass


def demo_figure3():
    """演示：生成一个示例 Figure 3"""
    print("生成示例 Figure 3...")
    
    # 使用理论值作为示例数据点
    demo_alphas = [0.25, 0.30, 0.35, 0.40, 0.45]
    demo_rewards = [theoretical_selfish_mining_reward(a, 0.5) * 0.95  # 稍微低于理论值
                    for a in demo_alphas]
    
    plot_figure3(
        alphas=demo_alphas,
        rewards=demo_rewards,
        gamma=0.5,
        title="Bitcoin Selfish Mining (Demo)",
        output_path="./results/figure3_demo.png"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="可视化工具")
    parser.add_argument("--demo", action="store_true", help="生成演示图")
    parser.add_argument("--results", type=str, help="评估结果CSV文件")
    parser.add_argument("--output", type=str, default="./results/figure3.png",
                        help="输出路径")
    
    args = parser.parse_args()
    
    if args.demo:
        demo_figure3()
    elif args.results:
        # 从CSV加载结果
        import csv
        results = []
        with open(args.results, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['alpha'] = float(row['alpha'])
                row['relative_gain'] = float(row['relative_gain'])
                results.append(row)
        
        plot_figure3(results=results, output_path=args.output)
    else:
        # 默认生成演示图
        demo_figure3()

