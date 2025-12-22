#!/usr/bin/env python
"""
SquirRL-Auditor 命令行工具

提供统一的命令行接口，支持：
- 训练自私挖矿策略模型
- 评估训练好的模型
- 生成可视化图表
- 比较不同协议的安全性

使用方法：
    python -m src.cli train --protocol bitcoin --alpha 0.35
    python -m src.cli evaluate ./models/model.zip --alpha 0.35
    python -m src.cli plot --results ./results/evaluation.csv
    python -m src.cli compare --protocols bitcoin ghost
"""

import argparse
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def cmd_train(args):
    """训练命令"""
    from src.agents.train import train_selfish_mining
    
    print(f"\n{'='*60}")
    print("SquirRL-Auditor: 开始训练")
    print(f"{'='*60}")
    
    # 准备环境参数
    env_kwargs = {}
    if args.protocol == 'utb':
        env_kwargs['utb_ratio'] = args.utb_ratio
    
    model, env = train_selfish_mining(
        protocol=args.protocol,
        alpha=args.alpha,
        gamma=args.gamma,
        total_timesteps=args.timesteps,
        learning_rate=args.lr,
        save_path=args.output,
        log_path=args.log_path,
        seed=args.seed,
        verbose=args.verbose,
        env_kwargs=env_kwargs
    )
    
    print(f"\n训练完成！模型保存在: {args.output}")


def cmd_evaluate(args):
    """评估命令"""
    from src.agents.evaluate import evaluate_model, evaluate_multiple_alphas, save_results
    
    print(f"\n{'='*60}")
    print("SquirRL-Auditor: 模型评估")
    print(f"{'='*60}")
    
    # 准备环境参数
    env_kwargs = {}
    if args.protocol == 'utb' and hasattr(args, 'utb_ratio'):
        env_kwargs['utb_ratio'] = args.utb_ratio
    
    if args.multi_alpha:
        # 评估多个alpha值
        results = evaluate_multiple_alphas(
            model_dir=args.model_path,
            alphas=args.alphas if args.alphas else [0.25, 0.30, 0.35, 0.40, 0.45],
            protocol=args.protocol,
            gamma=args.gamma,
            n_episodes=args.episodes,
            verbose=args.verbose,
            **env_kwargs
        )
    else:
        # 评估单个模型
        results = evaluate_model(
            model_path=args.model_path,
            protocol=args.protocol,
            alpha=args.alpha,
            gamma=args.gamma,
            n_episodes=args.episodes,
            verbose=args.verbose,
            **env_kwargs
        )
    
    # 保存结果
    if args.output:
        save_results(results if isinstance(results, list) else [results], args.output)


def cmd_plot(args):
    """绑图命令"""
    from src.visualization.reward_plot import plot_figure3, demo_figure3
    
    print(f"\n{'='*60}")
    print("SquirRL-Auditor: 生成图表")
    print(f"{'='*60}")
    
    if args.demo:
        # 生成演示图
        demo_figure3()
    elif args.results:
        # 从结果文件生成图
        import csv
        results = []
        with open(args.results, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 转换所有数值字段
                row['alpha'] = float(row['alpha'])
                row['relative_gain'] = float(row.get('relative_gain', row.get('mean_reward_fraction', row.get('avg_reward_per_step', 0))))
                row['std_reward'] = float(row.get('std_reward', 0))
                row['n_episodes'] = int(float(row.get('n_episodes', 100)))
                row['mean_reward'] = float(row.get('mean_reward', 0))
                results.append(row)
        
        plot_figure3(
            results=results,
            title=args.title or "Selfish Mining Results",
            output_path=args.output or "./results/figure3.png"
        )
    else:
        print("请指定 --demo 或 --results 参数")


def cmd_compare(args):
    """比较不同协议的命令"""
    from src.visualization.reward_plot import plot_comparison, theoretical_selfish_mining_reward
    
    print(f"\n{'='*60}")
    print("SquirRL-Auditor: 协议安全性比较")
    print(f"{'='*60}")
    
    # 加载各协议的评估结果
    bitcoin_results = None
    ghost_results = None
    
    if args.bitcoin_results:
        import csv
        bitcoin_results = []
        with open(args.bitcoin_results, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['alpha'] = float(row['alpha'])
                row['relative_gain'] = float(row.get('relative_gain', 0))
                bitcoin_results.append(row)
    
    if args.ghost_results:
        import csv
        ghost_results = []
        with open(args.ghost_results, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['alpha'] = float(row['alpha'])
                row['relative_gain'] = float(row.get('relative_gain', 0))
                ghost_results.append(row)
    
    # 如果没有真实数据，使用理论值
    if bitcoin_results is None:
        print("使用Bitcoin理论值...")
        alphas = [0.25, 0.30, 0.35, 0.40, 0.45]
        bitcoin_results = [
            {'alpha': a, 'relative_gain': theoretical_selfish_mining_reward(a, 0.5)}
            for a in alphas
        ]
    
    plot_comparison(
        bitcoin_results=bitcoin_results,
        ghost_results=ghost_results,
        title=args.title or "Bitcoin vs GHOST: Selfish Mining Comparison",
        output_path=args.output or "./results/comparison.png"
    )


def cmd_info(args):
    """显示环境信息"""
    print(f"\n{'='*60}")
    print("SquirRL-Auditor: 环境信息")
    print(f"{'='*60}")
    
    from src.environment.gym_wrapper import make_env
    
    for protocol in ["bitcoin", "ghost"]:
        print(f"\n协议: {protocol.upper()}")
        print("-" * 40)
        try:
            env = make_env(protocol=protocol, alpha=0.35, gamma=0.5)
            print(f"  动作空间: {env.action_space}")
            print(f"  观察空间: {env.observation_space}")
            
            # 测试一步
            obs, info = env.reset(seed=42)
            print(f"  初始观察: {obs}")
            print(f"  初始信息: {info}")
            env.close()
        except Exception as e:
            print(f"  错误: {e}")
    
    print(f"\n{'='*60}")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="SquirRL-Auditor: 区块链自私挖矿攻击分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  训练Bitcoin模型:
    python -m src.cli train --protocol bitcoin --alpha 0.35 --timesteps 100000
  
  评估模型:
    python -m src.cli evaluate ./models/bitcoin_model.zip --alpha 0.35
  
  生成演示图:
    python -m src.cli plot --demo
  
  查看环境信息:
    python -m src.cli info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # ========== train 命令 ==========
    train_parser = subparsers.add_parser('train', help='训练自私挖矿策略模型')
    train_parser.add_argument('--protocol', type=str, default='bitcoin',
                              choices=['bitcoin', 'ghost', 'ethereum', 'utb'],
                              help='区块链协议 (default: bitcoin)')
    train_parser.add_argument('--alpha', type=float, default=0.35,
                              help='攻击者算力占比 (default: 0.35)')
    train_parser.add_argument('--gamma', type=float, default=0.5,
                              help='跟随者比例 (default: 0.5)')
    train_parser.add_argument('--utb-ratio', type=float, default=0.5,
                              help='UTB叔块奖励比率 (仅UTB协议, default: 0.5)')
    train_parser.add_argument('--timesteps', type=int, default=100000,
                              help='训练步数 (default: 100000)')
    train_parser.add_argument('--lr', type=float, default=1e-4,
                              help='学习率 (default: 1e-4)')
    train_parser.add_argument('--output', type=str, default='./models',
                              help='模型保存路径 (default: ./models)')
    train_parser.add_argument('--log-path', type=str, default='./logs',
                              help='日志保存路径 (default: ./logs)')
    train_parser.add_argument('--seed', type=int, default=None,
                              help='随机种子')
    train_parser.add_argument('--verbose', type=int, default=1,
                              help='详细程度 (default: 1)')
    
    # ========== evaluate 命令 ==========
    eval_parser = subparsers.add_parser('evaluate', help='评估训练好的模型')
    eval_parser.add_argument('model_path', type=str,
                             help='模型路径或目录')
    eval_parser.add_argument('--protocol', type=str, default='bitcoin',
                             choices=['bitcoin', 'ghost', 'ethereum', 'utb'],
                             help='区块链协议')
    eval_parser.add_argument('--alpha', type=float, default=0.35,
                             help='攻击者算力占比')
    eval_parser.add_argument('--gamma', type=float, default=0.5,
                             help='跟随者比例')
    eval_parser.add_argument('--utb-ratio', type=float, default=0.5,
                             help='UTB叔块奖励比率 (仅UTB协议)')
    eval_parser.add_argument('--episodes', type=int, default=100,
                             help='评估的episode数量')
    eval_parser.add_argument('--multi-alpha', action='store_true',
                             help='评估多个alpha值')
    eval_parser.add_argument('--alphas', type=float, nargs='+',
                             help='要评估的alpha值列表')
    eval_parser.add_argument('--output', type=str, default='./results/evaluation.csv',
                             help='结果输出路径')
    eval_parser.add_argument('--verbose', type=int, default=1,
                             help='详细程度')
    
    # ========== plot 命令 ==========
    plot_parser = subparsers.add_parser('plot', help='生成可视化图表')
    plot_parser.add_argument('--demo', action='store_true',
                             help='生成演示图')
    plot_parser.add_argument('--results', type=str,
                             help='评估结果CSV文件')
    plot_parser.add_argument('--title', type=str,
                             help='图表标题')
    plot_parser.add_argument('--output', type=str,
                             help='输出文件路径')
    
    # ========== compare 命令 ==========
    compare_parser = subparsers.add_parser('compare', help='比较不同协议')
    compare_parser.add_argument('--bitcoin-results', type=str,
                                help='Bitcoin评估结果文件')
    compare_parser.add_argument('--ghost-results', type=str,
                                help='GHOST评估结果文件')
    compare_parser.add_argument('--title', type=str,
                                help='图表标题')
    compare_parser.add_argument('--output', type=str,
                                help='输出文件路径')
    
    # ========== info 命令 ==========
    info_parser = subparsers.add_parser('info', help='显示环境信息')
    
    # 解析参数
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # 执行对应命令
    if args.command == 'train':
        cmd_train(args)
    elif args.command == 'evaluate':
        cmd_evaluate(args)
    elif args.command == 'plot':
        cmd_plot(args)
    elif args.command == 'compare':
        cmd_compare(args)
    elif args.command == 'info':
        cmd_info(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

