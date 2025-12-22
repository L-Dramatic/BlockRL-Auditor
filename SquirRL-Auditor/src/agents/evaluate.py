"""
T5: 模型评估脚本
评估训练好的自私挖矿策略模型
"""

import os
import sys
import argparse
import numpy as np
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from stable_baselines3 import DQN
from src.environment.gym_wrapper import make_env


def evaluate_model(
    model_path,
    protocol="bitcoin",
    alpha=0.35,
    gamma=0.5,
    n_episodes=100,
    max_steps_per_episode=10000,
    deterministic=True,
    verbose=1,
    **env_kwargs
):
    """
    评估训练好的模型
    
    参数：
        model_path (str): 模型路径
        protocol (str): 协议类型
        alpha (float): 攻击者算力占比
        gamma (float): 跟随者比例
        n_episodes (int): 评估的episode数量
        max_steps_per_episode (int): 每个episode的最大步数
        deterministic (bool): 是否使用确定性策略
        verbose (int): 详细程度
    
    返回：
        results (dict): 评估结果
    """
    
    # 加载模型
    if verbose:
        print(f"加载模型: {model_path}")
    model = DQN.load(model_path)
    
    # 创建环境
    env = make_env(protocol=protocol, alpha=alpha, gamma=gamma, **env_kwargs)
    
    # 评估指标
    episode_rewards = []
    episode_lengths = []
    episode_reward_fractions = []  # 新增：真正的相对奖励（攻击者区块占比）
    action_counts = defaultdict(int)
    
    if verbose:
        print(f"\n开始评估 ({n_episodes} episodes)...")
        print(f"  协议: {protocol}")
        print(f"  α: {alpha}")
        print(f"  γ: {gamma}")
        if 'utb_ratio' in env_kwargs:
            print(f"  UTB 比率: {env_kwargs['utb_ratio']}")
    
    for episode in range(n_episodes):
        state, info = env.reset()
        episode_reward = 0
        episode_length = 0
        
        for step in range(max_steps_per_episode):
            # 获取动作
            action, _ = model.predict(state, deterministic=deterministic)
            action_counts[int(action)] += 1
            
            # 执行动作
            next_state, reward, terminated, truncated, info = env.step(action)
            
            episode_reward += reward
            episode_length += 1
            state = next_state
            
            if terminated or truncated:
                break
        
        # 获取真正的相对奖励（攻击者区块占比）
        reward_fraction = info.get('reward_fraction', 0)
        if reward_fraction == 0:
            # 备用方案：从底层环境获取
            try:
                reward_fraction = env.env.reward_fraction
            except:
                attacker_blocks = info.get('attacker_blocks', 0)
                honest_blocks = info.get('honest_blocks', 0)
                total_blocks = attacker_blocks + honest_blocks
                reward_fraction = attacker_blocks / total_blocks if total_blocks > 0 else alpha
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        episode_reward_fractions.append(reward_fraction)
        
        if verbose and (episode + 1) % 10 == 0:
            print(f"  Episode {episode + 1}/{n_episodes}: "
                  f"reward_fraction={reward_fraction:.4f}, length={episode_length}")
    
    # 计算统计数据
    results = {
        'protocol': protocol,
        'alpha': alpha,
        'gamma': gamma,
        'n_episodes': n_episodes,
        'mean_reward': np.mean(episode_rewards),
        'std_reward': np.std(episode_rewards),
        'min_reward': np.min(episode_rewards),
        'max_reward': np.max(episode_rewards),
        'mean_length': np.mean(episode_lengths),
        'std_length': np.std(episode_lengths),
        'action_distribution': dict(action_counts),
        'episode_rewards': episode_rewards,
        'episode_lengths': episode_lengths,
        # 新增：真正的相对奖励统计（这是论文中的定义！）
        'mean_reward_fraction': np.mean(episode_reward_fractions),
        'std_reward_fraction': np.std(episode_reward_fractions),
        'episode_reward_fractions': episode_reward_fractions
    }
    
    # 诚实挖矿的期望奖励比例 = alpha
    honest_reward = alpha
    
    # 相对收益 = 攻击者实际获得的区块比例（这才是论文中的定义！）
    results['honest_baseline'] = honest_reward
    results['relative_gain'] = results['mean_reward_fraction']  # 修正：使用 reward_fraction
    results['excess_reward'] = results['mean_reward_fraction'] - alpha  # 超额收益
    
    if verbose:
        print(f"\n评估结果:")
        print(f"  相对奖励 (reward_fraction): {results['mean_reward_fraction']:.4f} ± {results['std_reward_fraction']:.4f}")
        print(f"  诚实挖矿基准 (alpha): {alpha:.4f}")
        print(f"  超额收益: {results['excess_reward']:.4f}")
        print(f"  平均episode长度: {results['mean_length']:.1f} ± {results['std_length']:.1f}")
        print(f"  动作分布: {results['action_distribution']}")
    
    return results


def evaluate_multiple_alphas(
    model_dir,
    alphas=[0.25, 0.30, 0.35, 0.40, 0.45],
    protocol="bitcoin",
    gamma=0.5,
    n_episodes=100,
    verbose=1
):
    """
    评估多个alpha值对应的模型
    用于复现 Figure 3
    
    参数：
        model_dir (str): 模型目录
        alphas (list): alpha值列表
        protocol (str): 协议类型
        gamma (float): 跟随者比例
        n_episodes (int): 每个模型评估的episode数量
        verbose (int): 详细程度
    
    返回：
        all_results (list): 所有评估结果
    """
    
    all_results = []
    
    for alpha in alphas:
        # 查找对应的模型文件
        model_name = f"{protocol}_alpha_{alpha:.2f}"
        model_path = None
        
        # 尝试多种可能的文件名格式
        for filename in os.listdir(model_dir):
            if model_name in filename and filename.endswith('.zip'):
                model_path = os.path.join(model_dir, filename)
                break
        
        if model_path is None:
            if verbose:
                print(f"警告: 未找到 α={alpha} 的模型，跳过")
            continue
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"评估 α={alpha}")
            print(f"{'='*60}")
        
        results = evaluate_model(
            model_path=model_path,
            protocol=protocol,
            alpha=alpha,
            gamma=gamma,
            n_episodes=n_episodes,
            verbose=verbose
        )
        
        all_results.append(results)
    
    return all_results


def save_results(results, output_path):
    """保存评估结果到CSV"""
    import csv
    
    if isinstance(results, dict):
        results = [results]
    
    if not results:
        print("没有结果可保存")
        return
    
    # 获取列名（排除列表类型的列）
    columns = [k for k in results[0].keys() 
               if not isinstance(results[0][k], (list, dict))]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for r in results:
            row = {k: v for k, v in r.items() if k in columns}
            writer.writerow(row)
    
    print(f"结果已保存到: {output_path}")


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description="评估自私挖矿策略模型")
    
    parser.add_argument("model_path", type=str, help="模型路径或目录")
    parser.add_argument("--protocol", type=str, default="bitcoin",
                        choices=["bitcoin", "ghost"], help="协议类型")
    parser.add_argument("--alpha", type=float, default=0.35,
                        help="攻击者算力占比")
    parser.add_argument("--gamma", type=float, default=0.5,
                        help="跟随者比例")
    parser.add_argument("--episodes", type=int, default=100,
                        help="评估的episode数量")
    parser.add_argument("--output", type=str, default="./results/evaluation.csv",
                        help="结果输出路径")
    parser.add_argument("--multi-alpha", action="store_true",
                        help="评估多个alpha值（model_path应为目录）")
    parser.add_argument("--verbose", type=int, default=1, help="详细程度")
    
    args = parser.parse_args()
    
    if args.multi_alpha:
        results = evaluate_multiple_alphas(
            model_dir=args.model_path,
            protocol=args.protocol,
            gamma=args.gamma,
            n_episodes=args.episodes,
            verbose=args.verbose
        )
    else:
        results = evaluate_model(
            model_path=args.model_path,
            protocol=args.protocol,
            alpha=args.alpha,
            gamma=args.gamma,
            n_episodes=args.episodes,
            verbose=args.verbose
        )
    
    # 保存结果
    save_results(results if isinstance(results, list) else [results], 
                 args.output)


if __name__ == "__main__":
    main()

