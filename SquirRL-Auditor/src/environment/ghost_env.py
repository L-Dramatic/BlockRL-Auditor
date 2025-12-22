"""
扩展1: GHOST协议环境
GHOST (Greedy Heaviest Observed SubTree) 是Ethereum使用的链选择规则

关键区别：
- Bitcoin: 最长链规则 (longest chain)
- GHOST: 最重子树规则 (heaviest subtree)

GHOST允许叔块（uncle blocks）获得部分奖励，这改变了自私挖矿的收益计算。
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np

from .base_env import SM_env_with_stale


class GHOSTSelfishMiningEnv(gym.Env):
    """
    GHOST协议下的自私挖矿环境
    
    与Bitcoin环境的主要区别：
    1. 使用GHOST链选择规则
    2. 考虑孤块率(stale_rate)
    3. 状态空间更复杂（包含叔块信息）
    
    参数：
        max_hidden_block (int): 攻击者最大隐藏区块数
        attacker_fraction (float): 攻击者算力占比 (alpha)
        follower_fraction (float): 跟随者比例 (gamma)
        stale_rate (float): 孤块率，默认0.06（Ethereum实际值约为6%）
        know_alpha (bool): 是否将alpha作为状态的一部分
        dev (float): alpha随机波动的标准差
        random_interval (tuple): alpha的取值范围
        random_process (str): 随机过程类型 ("iid" 或 "brown")
    """
    
    metadata = {"render_modes": ["human"], "render_fps": 30}
    
    def __init__(
        self,
        max_hidden_block=20,
        attacker_fraction=0.35,
        follower_fraction=0.5,
        stale_rate=0.06,
        know_alpha=True,
        dev=0.0,
        random_interval=(0.0, 0.5),
        random_process="iid",
        render_mode=None
    ):
        super().__init__()
        
        # 保存参数
        self.alpha = attacker_fraction
        self.gamma = follower_fraction
        self.stale_rate = stale_rate
        self.max_hidden_block = max_hidden_block
        
        # 创建底层GHOST环境
        self.env = SM_env_with_stale(
            max_hidden_block=max_hidden_block,
            attacker_fraction=attacker_fraction,
            follower_fraction=follower_fraction,
            rule="GHOST",  # 关键：使用GHOST规则
            stale_rate=stale_rate,
            know_alpha=know_alpha,
            dev=dev,
            random_interval=random_interval,
            random_process=random_process
        )
        
        # 动作空间：3个离散动作
        # 0 = adopt (采纳诚实链)
        # 1 = override (覆盖)
        # 2 = wait (等待/继续挖矿)
        self.action_space = spaces.Discrete(self.env._action_space_n)
        
        # 观察空间：状态向量
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.env._state_vector_n,),
            dtype=np.float32
        )
        
        self.render_mode = render_mode
        
        # 统计信息
        self.current_state = None
        self.steps = 0
        self.episode_reward = 0
    
    def reset(self, seed=None, options=None):
        """重置环境"""
        super().reset(seed=seed)
        
        if seed is not None:
            self.env.seed(seed)
        
        self.current_state = self.env.reset()
        self.steps = 0
        self.episode_reward = 0
        
        # 转换为numpy数组
        obs = np.array(self.current_state, dtype=np.float32)
        
        info = {
            'alpha': self.alpha,
            'gamma': self.gamma,
            'stale_rate': self.stale_rate,
            'protocol': 'ghost'
        }
        
        return obs, info
    
    def step(self, action):
        """执行动作"""
        # 执行动作
        result = self.env.step(self.current_state, action, move=True)
        
        if len(result) == 4:
            next_state, reward, done, _ = result
        else:
            next_state, reward, done = result[:3]
        
        self.current_state = next_state
        self.steps += 1
        self.episode_reward += reward
        
        # 转换为numpy数组
        obs = np.array(next_state, dtype=np.float32)
        
        # Gymnasium标准：分离terminated和truncated
        terminated = done
        truncated = False
        
        info = {
            'steps': self.steps,
            'episode_reward': self.episode_reward,
            'reward_fraction': getattr(self.env, 'reward_fraction', 0),
            'protocol': 'ghost'
        }
        
        return obs, reward, terminated, truncated, info
    
    def render(self):
        """渲染（可选）"""
        if self.render_mode == "human":
            state_info = self._get_state_info()
            print(f"Step {self.steps}: {state_info}")
    
    def _get_state_info(self):
        """获取当前状态的可读信息"""
        if self.current_state is None:
            return "Not initialized"
        
        s = self.current_state
        if len(s) >= 4:
            return {
                'attacker_blocks': s[0],
                'honest_blocks': s[1],
                'special': s[2],
                'status': s[3]
            }
        return str(s)
    
    def close(self):
        """关闭环境"""
        pass


class EthereumSelfishMiningEnv(gym.Env):
    """
    Ethereum环境（带叔块奖励机制）
    
    Ethereum的叔块机制：
    - 叔块可以获得部分区块奖励
    - 包含叔块的区块也可以获得额外奖励
    - 这改变了自私挖矿的激励结构
    
    状态空间包含：
    - 攻击者隐藏区块数
    - 诚实矿工公开区块数
    - 状态标志
    - 叔块信息（6个时隙）
    """
    
    metadata = {"render_modes": ["human"], "render_fps": 30}
    
    def __init__(
        self,
        max_hidden_block=20,
        attacker_fraction=0.35,
        follower_fraction=0.5,
        stale_rate=0.06,
        know_alpha=True,
        dev=0.0,
        random_interval=(0.0, 0.5),
        random_process="iid",
        render_mode=None
    ):
        super().__init__()
        
        self.alpha = attacker_fraction
        self.gamma = follower_fraction
        self.stale_rate = stale_rate
        self.max_hidden_block = max_hidden_block
        
        # Ethereum使用带叔块的环境
        # 这里我们使用SM_env_with_stale，它支持叔块计算
        from .base_env import eth_env
        
        self.env = eth_env(
            max_hidden_block=max_hidden_block,
            attacker_fraction=attacker_fraction,
            follower_fraction=follower_fraction,
            know_alpha=know_alpha,
            dev=dev,
            random_interval=random_interval,
            random_process=random_process
        )
        
        self.action_space = spaces.Discrete(self.env._action_space_n)
        
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.env._state_vector_n,),
            dtype=np.float32
        )
        
        self.render_mode = render_mode
        self.current_state = None
        self.steps = 0
        self.episode_reward = 0
    
    def reset(self, seed=None, options=None):
        """重置环境"""
        super().reset(seed=seed)
        
        if seed is not None:
            self.env.seed(seed)
        
        self.current_state = self.env.reset()
        self.steps = 0
        self.episode_reward = 0
        
        obs = np.array(self.current_state, dtype=np.float32)
        
        info = {
            'alpha': self.alpha,
            'gamma': self.gamma,
            'stale_rate': self.stale_rate,
            'protocol': 'ethereum'
        }
        
        return obs, info
    
    def step(self, action):
        """执行动作"""
        result = self.env.step(self.current_state, action, move=True)
        
        if len(result) == 4:
            next_state, reward, done, _ = result
        else:
            next_state, reward, done = result[:3]
        
        self.current_state = next_state
        self.steps += 1
        self.episode_reward += reward
        
        obs = np.array(next_state, dtype=np.float32)
        
        terminated = done
        truncated = False
        
        info = {
            'steps': self.steps,
            'episode_reward': self.episode_reward,
            'reward_fraction': getattr(self.env, 'reward_fraction', 0),
            'protocol': 'ethereum'
        }
        
        return obs, reward, terminated, truncated, info
    
    def render(self):
        """渲染"""
        if self.render_mode == "human":
            print(f"Step {self.steps}: state={self.current_state}")
    
    def close(self):
        """关闭环境"""
        pass


def make_ghost_env(alpha=0.35, gamma=0.5, stale_rate=0.06, **kwargs):
    """创建GHOST环境的便捷函数"""
    return GHOSTSelfishMiningEnv(
        attacker_fraction=alpha,
        follower_fraction=gamma,
        stale_rate=stale_rate,
        **kwargs
    )


def make_ethereum_env(alpha=0.35, gamma=0.5, stale_rate=0.06, **kwargs):
    """创建Ethereum环境的便捷函数"""
    return EthereumSelfishMiningEnv(
        attacker_fraction=alpha,
        follower_fraction=gamma,
        stale_rate=stale_rate,
        **kwargs
    )

