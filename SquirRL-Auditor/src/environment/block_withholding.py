"""
扩展4: Block Withholding (扣块攻击) 环境

Block Withholding 是一种矿池间的博弈攻击：
- 两个矿池互相渗透
- 每个矿池可以派出部分算力加入对方矿池
- 渗透者找到区块后故意不提交（扣块）
- 获得对方矿池的分红但不贡献有效区块

这是一个**两人博弈**环境，可以用于研究矿池间的纳什均衡。

参考: SquirRL论文中的Block Withholding实验
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, Tuple, Any, Optional


def compute_reward(a: float, b: float, x: float, y: float) -> Dict[str, float]:
    """
    计算两个矿池的奖励
    
    参数:
        a (float): 矿池0的总算力
        b (float): 矿池1的总算力
        x (float): 矿池0派出的渗透算力（扣块）
        y (float): 矿池1派出的渗透算力（扣块）
    
    返回:
        rewards (dict): 两个矿池的相对奖励
    """
    eps = 1e-6
    
    # 边界情况处理
    if x + y > 1 - eps:
        return {'pool_0': 0., 'pool_1': 0.}
    if y < eps and a < eps:
        return {'pool_0': 1., 'pool_1': 1.}
    if x < eps and b < eps:
        return {'pool_0': 1., 'pool_1': 1.}
    
    # 有效算力（总算力 - 渗透算力）
    R1 = (a - x) / (1. - x - y)  # 矿池0的有效挖矿率
    R2 = (b - y) / (1. - x - y)  # 矿池1的有效挖矿率
    
    # 相对奖励公式
    # r1 = 矿池0获得的相对奖励
    # 包括：自己挖到的区块 + 从矿池1分得的奖励（通过渗透）
    r1 = ((b * R1) + x * (R1 + R2)) / (a * b + a * x + b * y)
    r2 = ((a * R2) + y * (R1 + R2)) / (a * b + a * x + b * y)
    
    return {'pool_0': float(r1), 'pool_1': float(r2)}


def get_nash_equilibrium(a: float, b: float) -> Tuple[float, float, float, float]:
    """
    计算两个矿池博弈的纳什均衡
    
    参数:
        a (float): 矿池0的算力
        b (float): 矿池1的算力
    
    返回:
        (x_eq, y_eq, r1_eq, r2_eq): 均衡时的策略和奖励
    """
    eps = 1e-6
    
    if a + b > 1. or (a < eps and b < eps):
        return 0., 0., 1., 1.
    
    # 迭代求解纳什均衡
    x, y = 0., 0.
    max_iter = 100
    
    for _ in range(max_iter):
        # 给定y，求矿池0的最优策略x
        x_new = _get_optimal_strategy(a, b, y)
        # 给定x，求矿池1的最优策略y
        y_new = _get_optimal_strategy(b, a, x)
        
        if abs(x_new - x) < eps and abs(y_new - y) < eps:
            break
        
        x, y = x_new, y_new
    
    rewards = compute_reward(a, b, x, y)
    return x, y, rewards['pool_0'], rewards['pool_1']


def _get_optimal_strategy(a: float, b: float, y: float) -> float:
    """
    给定对手策略y，求矿池的最优渗透策略
    使用数值方法近似求解
    """
    eps = 1e-6
    
    if a < eps:
        return 0.
    
    # 网格搜索找最优策略
    best_x = 0.
    best_reward = -np.inf
    
    for x in np.linspace(0, a - eps, 100):
        rewards = compute_reward(a, b, x, y)
        if rewards['pool_0'] > best_reward:
            best_reward = rewards['pool_0']
            best_x = x
    
    return best_x


class BlockWithholdingEnv(gym.Env):
    """
    Block Withholding 单智能体环境
    
    在这个简化版本中：
    - 智能体控制矿池0
    - 矿池1使用固定策略（或纳什均衡策略）
    
    状态空间: 当前轮次（或简化为单状态）
    动作空间: 渗透比例 [0, 1]，表示派出多少比例的算力去扣块
    
    参数:
        alpha_0 (float): 矿池0的算力 (0 < alpha_0 < 1)
        alpha_1 (float): 矿池1的算力 (0 < alpha_1 < 1)
        opponent_strategy (str): 对手策略 - "nash", "honest", "aggressive"
        max_steps (int): 每个episode的最大步数
    """
    
    metadata = {"render_modes": ["human"]}
    
    def __init__(
        self,
        alpha_0: float = 0.4,
        alpha_1: float = 0.5,
        opponent_strategy: str = "nash",
        max_steps: int = 100,
        render_mode: Optional[str] = None
    ):
        super().__init__()
        
        assert 0 < alpha_0 < 1, "alpha_0 must be in (0, 1)"
        assert 0 < alpha_1 < 1, "alpha_1 must be in (0, 1)"
        assert alpha_0 + alpha_1 <= 1, "alpha_0 + alpha_1 must be <= 1"
        
        self.alpha_0 = alpha_0
        self.alpha_1 = alpha_1
        self.opponent_strategy = opponent_strategy
        self.max_steps = max_steps
        self.render_mode = render_mode
        
        # 计算纳什均衡（用于对手策略）
        self.nash_x, self.nash_y, _, _ = get_nash_equilibrium(alpha_0, alpha_1)
        
        # 动作空间: 渗透比例 [0, 1]
        self.action_space = spaces.Box(
            low=np.array([0.0]),
            high=np.array([1.0]),
            dtype=np.float32
        )
        
        # 状态空间: [对手上一轮策略, 累计奖励差]
        self.observation_space = spaces.Box(
            low=np.array([0.0, -10.0]),
            high=np.array([1.0, 10.0]),
            dtype=np.float32
        )
        
        self.steps = 0
        self.cumulative_reward_0 = 0.
        self.cumulative_reward_1 = 0.
        self.last_opponent_action = 0.
    
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        """重置环境"""
        super().reset(seed=seed)
        
        self.steps = 0
        self.cumulative_reward_0 = 0.
        self.cumulative_reward_1 = 0.
        self.last_opponent_action = self._get_opponent_action()
        
        obs = self._get_obs()
        info = {
            'alpha_0': self.alpha_0,
            'alpha_1': self.alpha_1,
            'nash_equilibrium': (self.nash_x, self.nash_y)
        }
        
        return obs, info
    
    def step(self, action):
        """执行一步"""
        self.steps += 1
        
        # 我方策略：渗透比例 * 我方算力 = 实际渗透算力
        x = float(action[0]) * self.alpha_0
        x = np.clip(x, 0, self.alpha_0)
        
        # 对手策略
        y = self._get_opponent_action() * self.alpha_1
        
        # 计算奖励
        rewards = compute_reward(self.alpha_0, self.alpha_1, x, y)
        reward = rewards['pool_0']
        
        self.cumulative_reward_0 += reward
        self.cumulative_reward_1 += rewards['pool_1']
        self.last_opponent_action = y / self.alpha_1 if self.alpha_1 > 0 else 0
        
        obs = self._get_obs()
        
        terminated = False  # BW没有终止状态
        truncated = self.steps >= self.max_steps
        
        info = {
            'my_strategy': x,
            'opponent_strategy': y,
            'my_reward': rewards['pool_0'],
            'opponent_reward': rewards['pool_1'],
            'cumulative_reward_0': self.cumulative_reward_0,
            'cumulative_reward_1': self.cumulative_reward_1,
            'steps': self.steps
        }
        
        return obs, reward, terminated, truncated, info
    
    def _get_obs(self) -> np.ndarray:
        """获取观察"""
        reward_diff = self.cumulative_reward_0 - self.cumulative_reward_1
        return np.array([self.last_opponent_action, reward_diff], dtype=np.float32)
    
    def _get_opponent_action(self) -> float:
        """获取对手的策略"""
        if self.opponent_strategy == "nash":
            return self.nash_y / self.alpha_1 if self.alpha_1 > 0 else 0
        elif self.opponent_strategy == "honest":
            return 0.0  # 诚实策略：不扣块
        elif self.opponent_strategy == "aggressive":
            return 0.8  # 激进策略：80%算力用于扣块
        else:
            return self.nash_y / self.alpha_1 if self.alpha_1 > 0 else 0
    
    def render(self):
        """渲染"""
        if self.render_mode == "human":
            print(f"Step {self.steps}: "
                  f"Pool0 cumulative={self.cumulative_reward_0:.3f}, "
                  f"Pool1 cumulative={self.cumulative_reward_1:.3f}")
    
    def close(self):
        pass


class BlockWithholdingDiscreteEnv(gym.Env):
    """
    Block Withholding 离散动作版本
    
    将连续动作离散化，更容易用DQN训练
    
    动作空间: 5个离散动作
        0: 不扣块 (0%)
        1: 轻微扣块 (25%)
        2: 中等扣块 (50%)
        3: 大量扣块 (75%)
        4: 全力扣块 (100%)
    """
    
    metadata = {"render_modes": ["human"]}
    
    ACTIONS = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    def __init__(
        self,
        alpha_0: float = 0.4,
        alpha_1: float = 0.5,
        opponent_strategy: str = "nash",
        max_steps: int = 100,
        render_mode: Optional[str] = None
    ):
        super().__init__()
        
        self.alpha_0 = alpha_0
        self.alpha_1 = alpha_1
        self.opponent_strategy = opponent_strategy
        self.max_steps = max_steps
        self.render_mode = render_mode
        
        # 计算纳什均衡
        self.nash_x, self.nash_y, _, _ = get_nash_equilibrium(alpha_0, alpha_1)
        
        # 离散动作空间
        self.action_space = spaces.Discrete(len(self.ACTIONS))
        
        # 状态空间（简化为单状态，专注于学习最优策略）
        self.observation_space = spaces.Discrete(1)
        
        self.steps = 0
        self.cumulative_reward = 0.
    
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        """重置环境"""
        super().reset(seed=seed)
        
        self.steps = 0
        self.cumulative_reward = 0.
        
        obs = 0
        info = {
            'alpha_0': self.alpha_0,
            'alpha_1': self.alpha_1,
            'nash_x': self.nash_x,
            'nash_y': self.nash_y
        }
        
        return obs, info
    
    def step(self, action: int):
        """执行一步"""
        self.steps += 1
        
        # 将离散动作转换为渗透比例
        infiltration_ratio = self.ACTIONS[action]
        x = infiltration_ratio * self.alpha_0
        
        # 对手策略
        if self.opponent_strategy == "nash":
            y = self.nash_y
        elif self.opponent_strategy == "honest":
            y = 0.0
        elif self.opponent_strategy == "aggressive":
            y = 0.8 * self.alpha_1
        else:
            y = self.nash_y
        
        # 计算奖励
        rewards = compute_reward(self.alpha_0, self.alpha_1, x, y)
        reward = rewards['pool_0']
        
        self.cumulative_reward += reward
        
        obs = 0
        terminated = False
        truncated = self.steps >= self.max_steps
        
        info = {
            'my_strategy': x,
            'my_ratio': infiltration_ratio,
            'opponent_strategy': y,
            'my_reward': rewards['pool_0'],
            'opponent_reward': rewards['pool_1'],
            'cumulative_reward': self.cumulative_reward,
            'steps': self.steps
        }
        
        return obs, reward, terminated, truncated, info
    
    def render(self):
        if self.render_mode == "human":
            print(f"Step {self.steps}: cumulative_reward={self.cumulative_reward:.3f}")
    
    def close(self):
        pass


def make_bw_env(
    alpha_0: float = 0.4,
    alpha_1: float = 0.5,
    discrete: bool = True,
    **kwargs
) -> gym.Env:
    """
    创建Block Withholding环境的便捷函数
    
    参数:
        alpha_0: 矿池0的算力
        alpha_1: 矿池1的算力
        discrete: 是否使用离散动作版本（推荐用于DQN）
    """
    if discrete:
        return BlockWithholdingDiscreteEnv(alpha_0=alpha_0, alpha_1=alpha_1, **kwargs)
    else:
        return BlockWithholdingEnv(alpha_0=alpha_0, alpha_1=alpha_1, **kwargs)


# 测试代码
if __name__ == "__main__":
    print("测试 Block Withholding 环境")
    print("="*60)
    
    # 测试纳什均衡计算
    print("\n[1] 测试纳什均衡计算...")
    x, y, r1, r2 = get_nash_equilibrium(0.4, 0.5)
    print(f"  alpha_0=0.4, alpha_1=0.5")
    print(f"  纳什均衡: x={x:.4f}, y={y:.4f}")
    print(f"  均衡奖励: r1={r1:.4f}, r2={r2:.4f}")
    
    # 测试离散环境
    print("\n[2] 测试离散动作环境...")
    env = make_bw_env(alpha_0=0.4, alpha_1=0.5, discrete=True)
    obs, info = env.reset(seed=42)
    print(f"  初始状态: {obs}")
    print(f"  动作空间: {env.action_space}")
    
    total_reward = 0
    for i in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        if i < 3:
            print(f"  Step {i+1}: action={action}, reward={reward:.4f}")
    
    print(f"  总奖励: {total_reward:.4f}")
    
    print("\n[SUCCESS] Block Withholding 环境测试通过!")







