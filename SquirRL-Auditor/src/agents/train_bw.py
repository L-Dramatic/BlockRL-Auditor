"""
扩展4: Block Withholding 训练脚本
"""

import os
import sys
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.monitor import Monitor
from gymnasium.wrappers import TimeLimit

from src.environment.block_withholding import (
    make_bw_env,
    get_nash_equilibrium,
    compute_reward
)


def train_block_withholding(
    alpha_0=0.4,
    alpha_1=0.5,
    opponent_strategy="nash",
    total_timesteps=50000,
    learning_rate=1e-4,
    save_path="./models/bw",
    verbose=1
):
    """
    训练 Block Withholding 策略
    
    参数:
        alpha_0: 我方矿池算力
        alpha_1: 对手矿池算力
        opponent_strategy: 对手策略 ("nash", "honest", "aggressive")
        total_timesteps: 训练步数
        learning_rate: 学习率
        save_path: 模型保存路径
        verbose: 详细程度
    """
    
    # 计算理论纳什均衡
    nash_x, nash_y, nash_r1, nash_r2 = get_nash_equilibrium(alpha_0, alpha_1)
    
    print(f"\n{'='*60}")
    print("Block Withholding 训练配置")
    print(f"{'='*60}")
    print(f"  矿池0算力 (我方): {alpha_0}")
    print(f"  矿池1算力 (对手): {alpha_1}")
    print(f"  对手策略: {opponent_strategy}")
    print(f"  训练步数: {total_timesteps}")
    print(f"\n理论纳什均衡:")
    print(f"  x* (我方渗透): {nash_x:.4f}")
    print(f"  y* (对手渗透): {nash_y:.4f}")
    print(f"  均衡奖励: r1={nash_r1:.4f}, r2={nash_r2:.4f}")
    print(f"{'='*60}\n")
    
    # 创建环境
    env = make_bw_env(
        alpha_0=alpha_0,
        alpha_1=alpha_1,
        opponent_strategy=opponent_strategy,
        discrete=True,
        max_steps=100
    )
    env = TimeLimit(env, max_episode_steps=100)
    env = Monitor(env)
    
    # 创建模型
    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=learning_rate,
        buffer_size=10000,
        learning_starts=500,
        batch_size=32,
        gamma=0.99,
        exploration_fraction=0.3,
        exploration_final_eps=0.05,
        verbose=verbose,
        tensorboard_log=None
    )
    
    # 训练
    print("开始训练...")
    model.learn(
        total_timesteps=total_timesteps,
        progress_bar=verbose > 0
    )
    
    # 保存模型
    os.makedirs(save_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = os.path.join(save_path, f"bw_{alpha_0}_{alpha_1}_{timestamp}")
    model.save(model_path)
    print(f"\n模型已保存到: {model_path}")
    
    return model, env


def evaluate_bw_model(model, env, n_episodes=100, verbose=1):
    """
    评估 BW 模型
    """
    from src.environment.block_withholding import BlockWithholdingDiscreteEnv
    
    action_counts = [0] * 5
    total_reward = 0
    
    for ep in range(n_episodes):
        obs, info = env.reset()
        episode_reward = 0
        
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            action_counts[int(action)] += 1
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            done = terminated or truncated
        
        total_reward += episode_reward
    
    avg_reward = total_reward / n_episodes
    
    if verbose:
        print(f"\n评估结果 ({n_episodes} episodes):")
        print(f"  平均奖励: {avg_reward:.4f}")
        print(f"  动作分布:")
        action_labels = ["0% (诚实)", "25%", "50%", "75%", "100% (全扣)"]
        total_actions = sum(action_counts)
        for i, count in enumerate(action_counts):
            pct = count / total_actions * 100
            print(f"    {action_labels[i]}: {pct:.1f}%")
    
    return avg_reward, action_counts


def compare_strategies(alpha_0=0.4, alpha_1=0.5, n_episodes=100):
    """
    比较不同策略的效果
    """
    print(f"\n{'='*60}")
    print("策略比较")
    print(f"{'='*60}")
    
    # 计算纳什均衡
    nash_x, nash_y, nash_r1, nash_r2 = get_nash_equilibrium(alpha_0, alpha_1)
    print(f"\n理论纳什均衡: x*={nash_x:.4f}, y*={nash_y:.4f}")
    print(f"均衡奖励: r1={nash_r1:.4f}, r2={nash_r2:.4f}")
    
    # 测试固定策略
    strategies = [
        ("诚实 (0%)", 0.0),
        ("轻微 (25%)", 0.25),
        ("中等 (50%)", 0.5),
        ("激进 (75%)", 0.75),
        ("全扣 (100%)", 1.0),
        ("纳什均衡", nash_x / alpha_0 if alpha_0 > 0 else 0)
    ]
    
    print(f"\n固定策略测试 (对手使用纳什策略 y*={nash_y:.4f}):")
    
    for name, ratio in strategies:
        x = ratio * alpha_0
        rewards = compute_reward(alpha_0, alpha_1, x, nash_y)
        print(f"  {name}: x={x:.4f}, 奖励={rewards['pool_0']:.4f}")
    
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Block Withholding 训练")
    parser.add_argument("--alpha0", type=float, default=0.4, help="矿池0算力")
    parser.add_argument("--alpha1", type=float, default=0.5, help="矿池1算力")
    parser.add_argument("--opponent", type=str, default="nash",
                        choices=["nash", "honest", "aggressive"],
                        help="对手策略")
    parser.add_argument("--timesteps", type=int, default=50000, help="训练步数")
    parser.add_argument("--compare", action="store_true", help="只比较策略，不训练")
    parser.add_argument("--verbose", type=int, default=1, help="详细程度")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_strategies(args.alpha0, args.alpha1)
    else:
        model, env = train_block_withholding(
            alpha_0=args.alpha0,
            alpha_1=args.alpha1,
            opponent_strategy=args.opponent,
            total_timesteps=args.timesteps,
            verbose=args.verbose
        )
        
        # 评估
        print("\n" + "="*60)
        print("评估训练好的模型")
        print("="*60)
        evaluate_bw_model(model, env, n_episodes=50, verbose=1)
        
        # 比较策略
        compare_strategies(args.alpha0, args.alpha1)


if __name__ == "__main__":
    main()







