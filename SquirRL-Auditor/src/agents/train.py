"""
T3: Stable-Baselines3 训练脚本
使用现代强化学习框架训练自私挖矿策略
"""

import os
import sys
import argparse
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from gymnasium.wrappers import TimeLimit

from src.environment.gym_wrapper import make_env


def train_selfish_mining(
    protocol="bitcoin",
    alpha=0.35,
    gamma=0.5,
    total_timesteps=100000,
    learning_rate=1e-4,
    buffer_size=50000,
    learning_starts=1000,
    batch_size=32,
    tau=1.0,
    gamma_discount=0.99,
    target_update_interval=1000,
    exploration_fraction=0.1,
    exploration_initial_eps=1.0,
    exploration_final_eps=0.05,
    save_path="./models",
    log_path="./logs",
    seed=None,
    verbose=1,
    env_kwargs=None
):
    """
    训练自私挖矿策略
    
    参数：
        protocol (str): 协议类型 ("bitcoin" 或 "ghost")
        alpha (float): 攻击者算力占比
        gamma (float): 跟随者比例
        total_timesteps (int): 总训练步数
        learning_rate (float): 学习率
        buffer_size (int): 经验回放buffer大小
        learning_starts (int): 开始学习的步数
        batch_size (int): 批次大小
        tau (float): soft update系数
        gamma_discount (float): 折扣因子
        target_update_interval (int): 目标网络更新间隔
        exploration_fraction (float): 探索衰减比例
        exploration_initial_eps (float): 初始探索率
        exploration_final_eps (float): 最终探索率
        save_path (str): 模型保存路径
        log_path (str): 日志保存路径
        seed (int): 随机种子
        verbose (int): 详细程度
    
    返回：
        model: 训练好的模型
        env: 训练环境
    """
    
    # 创建保存目录
    os.makedirs(save_path, exist_ok=True)
    if log_path:
        os.makedirs(log_path, exist_ok=True)
    
    # 设置随机种子
    if seed is not None:
        np.random.seed(seed)
    
    # 创建环境
    print(f"\n{'='*60}")
    print(f"训练配置:")
    print(f"  协议: {protocol}")
    print(f"  攻击者算力 (α): {alpha}")
    print(f"  跟随者比例 (γ): {gamma}")
    if env_kwargs and 'utb_ratio' in env_kwargs:
        print(f"  UTB 比率: {env_kwargs['utb_ratio']}")
    print(f"  训练步数: {total_timesteps}")
    print(f"  学习率: {learning_rate}")
    print(f"{'='*60}\n")
    
    # 准备环境参数
    if env_kwargs is None:
        env_kwargs = {}
    env_params = {'alpha': alpha, 'gamma': gamma, **env_kwargs}
    
    # 创建训练环境（添加步数限制防止无限循环）
    env = make_env(protocol=protocol, **env_params)
    env = TimeLimit(env, max_episode_steps=10000)  # 限制每个episode最多10000步
    env = Monitor(env, log_path if log_path else None)
    
    # 创建评估环境（同样添加步数限制）
    eval_env = make_env(protocol=protocol, **env_params)
    eval_env = TimeLimit(eval_env, max_episode_steps=1000)  # 评估时限制更短，加快评估速度
    eval_env = Monitor(eval_env)
    
    # 创建模型
    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=learning_rate,
        buffer_size=buffer_size,
        learning_starts=learning_starts,
        batch_size=batch_size,
        tau=tau,
        gamma=gamma_discount,
        target_update_interval=target_update_interval,
        exploration_fraction=exploration_fraction,
        exploration_initial_eps=exploration_initial_eps,
        exploration_final_eps=exploration_final_eps,
        verbose=verbose,
        tensorboard_log=None  # 禁用TensorBoard（需要先安装tensorboard）
    )
    
    # 创建回调函数
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if protocol == "utb" and env_kwargs and 'utb_ratio' in env_kwargs:
        model_name = f"{protocol}_alpha_{alpha:.2f}_ratio_{env_kwargs['utb_ratio']:.2f}_{timestamp}"
    elif gamma != 0.5:
        # 非默认gamma值时，将gamma加入模型名称
        model_name = f"{protocol}_alpha_{alpha:.2f}_gamma_{gamma:.2f}_{timestamp}"
    else:
        model_name = f"{protocol}_alpha_{alpha:.2f}_{timestamp}"
    
    # 创建回调函数列表
    callbacks = []
    
    if log_path:
        # 评估回调（减少评估频率和episode数，加快训练）
        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=os.path.join(save_path, f"best_{model_name}"),
            log_path=log_path,
            eval_freq=max(total_timesteps // 5, 5000),  # 减少评估频率
            n_eval_episodes=5,  # 只评估5个episode
            deterministic=True,
            render=False,
            verbose=1
        )
        callbacks.append(eval_callback)
        
        # 检查点回调
        checkpoint_callback = CheckpointCallback(
            save_freq=max(total_timesteps // 5, 5000),
            save_path=os.path.join(save_path, "checkpoints"),
            name_prefix=model_name,
            verbose=1
        )
        callbacks.append(checkpoint_callback)
    
    # 开始训练
    print(f"开始训练...")
    model.learn(
        total_timesteps=total_timesteps,
        callback=callbacks if callbacks else None,
        log_interval=100,
        progress_bar=verbose > 0
    )
    
    # 保存最终模型
    final_model_path = os.path.join(save_path, f"{model_name}_final")
    model.save(final_model_path)
    print(f"\n模型已保存到: {final_model_path}.zip")
    
    return model, env


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description="训练自私挖矿策略")
    
    # 环境参数
    parser.add_argument("--protocol", type=str, default="bitcoin",
                        choices=["bitcoin", "ghost"],
                        help="协议类型")
    parser.add_argument("--alpha", type=float, default=0.35,
                        help="攻击者算力占比 (0-0.5)")
    parser.add_argument("--gamma", type=float, default=0.5,
                        help="跟随者比例 (0-1)")
    
    # 训练参数
    parser.add_argument("--timesteps", type=int, default=100000,
                        help="总训练步数")
    parser.add_argument("--lr", type=float, default=1e-4,
                        help="学习率")
    parser.add_argument("--buffer-size", type=int, default=50000,
                        help="经验回放buffer大小")
    parser.add_argument("--batch-size", type=int, default=32,
                        help="批次大小")
    parser.add_argument("--gamma-discount", type=float, default=0.99,
                        help="折扣因子")
    
    # 其他参数
    parser.add_argument("--save-path", type=str, default="./models",
                        help="模型保存路径")
    parser.add_argument("--log-path", type=str, default="./logs",
                        help="日志保存路径")
    parser.add_argument("--seed", type=int, default=None,
                        help="随机种子")
    parser.add_argument("--verbose", type=int, default=1,
                        help="详细程度")
    
    args = parser.parse_args()
    
    # 训练
    model, env = train_selfish_mining(
        protocol=args.protocol,
        alpha=args.alpha,
        gamma=args.gamma,
        total_timesteps=args.timesteps,
        learning_rate=args.lr,
        buffer_size=args.buffer_size,
        batch_size=args.batch_size,
        gamma_discount=args.gamma_discount,
        save_path=args.save_path,
        log_path=args.log_path,
        seed=args.seed,
        verbose=args.verbose
    )
    
    print(f"\n{'='*60}")
    print("训练完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

