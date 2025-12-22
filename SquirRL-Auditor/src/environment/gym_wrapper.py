"""
T2: Gym 包装器
将 SquirRL 的 SM_env 包装成标准的 OpenAI Gym 环境
使其能够与 Stable-Baselines3 配合使用
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from .base_env import SM_env, SM_env_with_stale

# 延迟导入GHOST环境（避免循环导入）
GHOSTSelfishMiningEnv = None
EthereumSelfishMiningEnv = None


class BitcoinSelfishMiningEnv(gym.Env):
    """
    Bitcoin 自私挖矿环境的 Gym 包装器
    
    观察空间：状态索引
    动作空间：3个动作 (adopt, override, match, wait)
    
    参数：
        alpha (float): 攻击者算力占比 (0-0.5)
        gamma (float): 跟随者比例 (0-1)
        max_fork_length (int): 最大分叉长度
        stale_rate (float): 孤块率 (0-0.1)
        protocol (str): 共识协议 ("bitcoin" 或 "ghost")
    """
    
    metadata = {'render.modes': ['human']}
    
    def __init__(self, alpha=0.35, gamma=0.5, max_fork_length=20, 
                 stale_rate=0.0, protocol="bitcoin", **kwargs):
        super(BitcoinSelfishMiningEnv, self).__init__()
        
        self.alpha = alpha
        self.gamma = gamma
        self.max_fork_length = max_fork_length
        self.stale_rate = stale_rate
        self.protocol = protocol
        
        # 创建底层环境
        if stale_rate > 0:
            self.env = SM_env_with_stale(
                max_hidden_block=max_fork_length,
                attacker_fraction=alpha,
                follower_fraction=gamma,
                stale_rate=stale_rate,
                **kwargs
            )
        else:
            self.env = SM_env(
                max_hidden_block=max_fork_length,
                attacker_fraction=alpha,
                follower_fraction=gamma,
                **kwargs
            )
        
        # 定义动作空间：3个离散动作
        # 0: adopt (采用诚实链)
        # 1: override (发布私有链)
        # 2: match/wait (匹配或等待)
        self.action_space = spaces.Discrete(3)
        
        # 定义观察空间：状态索引
        # 状态数量取决于 max_fork_length
        n_states = len(self.env._state_space)
        self.observation_space = spaces.Discrete(n_states)
        
        self.current_state = None
        self.steps = 0
        self.episode_reward = 0
        
    def reset(self, seed=None, options=None):
        """
        重置环境到初始状态
        
        参数：
            seed (int, optional): 随机种子
            options (dict, optional): 额外选项
        
        返回：
            observation: 初始状态
            info: 额外信息字典
        """
        if seed is not None:
            self.env.seed(seed)
            np.random.seed(seed)
        
        self.current_state = self.env.reset()
        self.steps = 0
        self.episode_reward = 0
        
        # Gymnasium 标准：reset 需要返回 (observation, info)
        info = {
            'alpha': self.alpha,
            'gamma': self.gamma
        }
        
        return self.current_state, info
    
    def step(self, action):
        """
        执行一个动作
        
        参数：
            action (int): 动作索引 (0, 1, 或 2)
        
        返回（Gymnasium 标准接口）：
            observation (int): 新状态
            reward (float): 奖励
            terminated (bool): 是否因为到达终止状态而结束
            truncated (bool): 是否因为超时等原因被截断
            info (dict): 额外信息
        """
        # 执行动作（底层环境返回的是 4 个值，但 info 可能不是字典）
        step_result = self.env.step(self.current_state, action)
        
        if len(step_result) == 4:
            next_state, reward, done, _original_info = step_result
        else:
            # 某些环境可能只返回3个值
            next_state, reward, done = step_result
            _original_info = None
        
        self.current_state = next_state
        self.steps += 1
        self.episode_reward += reward
        
        # Gymnasium 标准：分离 terminated 和 truncated
        terminated = done  # 原环境的 done 表示 terminated
        truncated = False  # 我们不使用 truncation
        
        # 创建新的 info 字典
        # 获取真正的相对奖励（攻击者区块占比）
        reward_fraction = getattr(self.env, 'reward_fraction', 0)
        attacker_blocks = getattr(self.env, '_attack_block', 0)
        honest_blocks = getattr(self.env, '_honest_block', 0)
        
        info = {
            'steps': self.steps,
            'episode_reward': self.episode_reward,
            'alpha': self.alpha,
            'state_info': self.get_state_info(next_state),
            'reward_fraction': reward_fraction,  # 这是论文中的相对奖励！
            'attacker_blocks': attacker_blocks,
            'honest_blocks': honest_blocks
        }
        
        return next_state, reward, terminated, truncated, info
    
    def render(self, mode='human'):
        """渲染环境（可选）"""
        if mode == 'human':
            state_info = self.env._state_space[self.current_state]
            print(f"Step: {self.steps}, State: {state_info}, Reward: {self.episode_reward:.3f}")
    
    def close(self):
        """关闭环境"""
        pass
    
    def get_state_info(self, state_idx):
        """获取状态信息（用于调试）"""
        if 0 <= state_idx < len(self.env._state_space):
            return self.env._state_space[state_idx]
        return None


class GHOSTSelfishMiningEnv(BitcoinSelfishMiningEnv):
    """
    GHOST 协议的自私挖矿环境
    继承自 BitcoinSelfishMiningEnv，但使用不同的区块选择规则
    """
    
    def __init__(self, alpha=0.35, gamma=0.5, max_fork_length=20, 
                 k=10, **kwargs):
        """
        参数：
            k (int): GHOST 参数，选择链时考虑的深度
        """
        super().__init__(alpha, gamma, max_fork_length, protocol="ghost", **kwargs)
        self.k = k
        # TODO: 需要修改底层环境以支持 GHOST 规则


def make_env(protocol="bitcoin", **kwargs):
    """
    工厂函数：根据协议类型创建环境
    
    参数：
        protocol (str): "bitcoin" 或 "ghost"
        **kwargs: 传递给环境的其他参数
    
    返回：
        env (gym.Env): Gym 环境实例
    """
    global GHOSTSelfishMiningEnv, EthereumSelfishMiningEnv
    
    if protocol.lower() == "bitcoin":
        return BitcoinSelfishMiningEnv(**kwargs)
    elif protocol.lower() == "ghost":
        # 延迟导入
        if GHOSTSelfishMiningEnv is None:
            from .ghost_env import GHOSTSelfishMiningEnv as _GHOSTEnv
            GHOSTSelfishMiningEnv = _GHOSTEnv
        return GHOSTSelfishMiningEnv(**kwargs)
    elif protocol.lower() == "ethereum" or protocol.lower() == "eth":
        # 延迟导入
        if EthereumSelfishMiningEnv is None:
            from .ghost_env import EthereumSelfishMiningEnv as _EthEnv
            EthereumSelfishMiningEnv = _EthEnv
        # Ethereum环境使用不同的参数名
        eth_kwargs = dict(kwargs)
        if 'alpha' in eth_kwargs:
            eth_kwargs['attacker_fraction'] = eth_kwargs.pop('alpha')
        if 'gamma' in eth_kwargs:
            eth_kwargs['follower_fraction'] = eth_kwargs.pop('gamma')
        return EthereumSelfishMiningEnv(**eth_kwargs)
    elif protocol.lower() == "utb":
        # UTB防御环境
        from .utb_defense import UTBDefenseEnv
        # UTBDefenseEnv 使用不同的参数名
        utb_kwargs = dict(kwargs)
        if 'alpha' in utb_kwargs:
            utb_kwargs['attacker_fraction'] = utb_kwargs.pop('alpha')
        if 'gamma' in utb_kwargs:
            utb_kwargs['follower_fraction'] = utb_kwargs.pop('gamma')
        return UTBDefenseEnv(**utb_kwargs)
    else:
        raise ValueError(f"Unknown protocol: {protocol}. Supported: bitcoin, ghost, ethereum, utb")


if __name__ == "__main__":
    # 测试代码
    print("测试 Gym 包装器...")
    
    env = BitcoinSelfishMiningEnv(alpha=0.35)
    print(f"动作空间: {env.action_space}")
    print(f"观察空间: {env.observation_space}")
    
    state = env.reset()
    print(f"初始状态: {state}")
    
    # 运行几步
    for i in range(5):
        action = env.action_space.sample()  # 随机动作
        next_state, reward, done, info = env.step(action)
        print(f"Step {i+1}: action={action}, state={next_state}, reward={reward:.3f}")
        if done:
            break
    
    print("\nGym 包装器测试完成！")

