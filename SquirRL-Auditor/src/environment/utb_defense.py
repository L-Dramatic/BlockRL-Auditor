"""
扩展2: UTB (Uncles-To-Block) 防御机制

UTB防御是一种针对自私挖矿攻击的防御策略。
核心思想：通过调整叔块奖励机制来减少自私挖矿的收益。

参考文献：
- "Publish or Perish: A Backward-Compatible Defense Against Selfish Mining in Bitcoin"

防御机制参数：
- utb_ratio: 叔块奖励与主块奖励的比率
- max_uncles: 每个区块最多可包含的叔块数量
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from .base_env import SM_env_with_stale


class UTBDefenseEnv(gym.Env):
    """
    带UTB防御机制的自私挖矿环境
    
    UTB防御通过以下方式减少自私挖矿收益：
    1. 增加诚实矿工发布孤块的奖励
    2. 降低自私矿工隐藏区块的优势
    
    参数：
        utb_ratio (float): 叔块奖励比率 (0-1)，越高防御越强
        max_uncles (int): 每个区块最多包含的叔块数
        其他参数与标准环境相同
    """
    
    metadata = {"render_modes": ["human"], "render_fps": 30}
    
    def __init__(
        self,
        max_hidden_block=20,
        attacker_fraction=0.35,
        follower_fraction=0.5,
        utb_ratio=0.5,
        max_uncles=2,
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
        self.utb_ratio = utb_ratio
        self.max_uncles = max_uncles
        self.stale_rate = stale_rate
        self.max_hidden_block = max_hidden_block
        
        # 使用带stale的环境作为基础
        self.env = SM_env_with_stale(
            max_hidden_block=max_hidden_block,
            attacker_fraction=attacker_fraction,
            follower_fraction=follower_fraction,
            rule="longest",  # Bitcoin规则
            stale_rate=stale_rate,
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
        
        # UTB防御统计
        self.utb_stats = {
            'attacker_blocks': 0,
            'honest_blocks': 0,
            'attacker_uncles': 0,
            'honest_uncles': 0
        }
    
    def reset(self, seed=None, options=None):
        """重置环境"""
        super().reset(seed=seed)
        
        if seed is not None:
            self.env.seed(seed)
        
        self.current_state = self.env.reset()
        self.steps = 0
        self.episode_reward = 0
        self.utb_stats = {
            'attacker_blocks': 0,
            'honest_blocks': 0,
            'attacker_uncles': 0,
            'honest_uncles': 0
        }
        
        obs = np.array(self.current_state, dtype=np.float32)
        
        info = {
            'alpha': self.alpha,
            'gamma': self.gamma,
            'utb_ratio': self.utb_ratio,
            'defense': 'utb'
        }
        
        return obs, info
    
    def step(self, action):
        """执行动作，应用UTB防御调整"""
        # 获取原始环境的结果
        result = self.env.step(self.current_state, action, move=True)
        
        if len(result) == 4:
            next_state, base_reward, done, _ = result
        else:
            next_state, base_reward, done = result[:3]
        
        # 应用UTB防御奖励调整
        adjusted_reward = self._apply_utb_defense(base_reward, action)
        
        self.current_state = next_state
        self.steps += 1
        self.episode_reward += adjusted_reward
        
        obs = np.array(next_state, dtype=np.float32)
        
        terminated = done
        truncated = False
        
        info = {
            'steps': self.steps,
            'episode_reward': self.episode_reward,
            'base_reward': base_reward,
            'adjusted_reward': adjusted_reward,
            'utb_stats': self.utb_stats.copy(),
            'defense': 'utb'
        }
        
        return obs, adjusted_reward, terminated, truncated, info
    
    def _apply_utb_defense(self, base_reward, action):
        """
        应用UTB防御机制调整奖励
        
        UTB的核心思想：
        - 当攻击者发布隐藏的区块时，部分奖励会因为UTB机制而损失
        - 损失的比例与utb_ratio相关
        
        参数：
            base_reward (float): 原始奖励
            action (int): 执行的动作
        
        返回：
            adjusted_reward (float): 调整后的奖励
        """
        # 动作映射：0=adopt, 1=override, 2=wait
        
        if action == 1:  # override - 发布隐藏链
            # UTB惩罚：发布长时间隐藏的区块会损失部分奖励
            # 隐藏越久，损失越大
            hidden_length = self.current_state[0] if len(self.current_state) > 0 else 0
            utb_penalty = self.utb_ratio * (hidden_length / self.max_hidden_block) * abs(base_reward)
            adjusted_reward = base_reward - utb_penalty
        elif action == 0:  # adopt - 攻击者放弃私有链
            # 诚实行为没有UTB惩罚
            adjusted_reward = base_reward
        else:  # wait - 继续挖矿
            adjusted_reward = base_reward
        
        return adjusted_reward
    
    def render(self):
        """渲染"""
        if self.render_mode == "human":
            print(f"Step {self.steps}: state={self.current_state}, UTB stats={self.utb_stats}")
    
    def close(self):
        """关闭环境"""
        pass
    
    def get_defense_effectiveness(self):
        """
        计算UTB防御的有效性
        
        返回：
            effectiveness (dict): 防御效果指标
        """
        total_attacker = self.utb_stats['attacker_blocks'] + self.utb_stats['attacker_uncles']
        total_honest = self.utb_stats['honest_blocks'] + self.utb_stats['honest_uncles']
        total = total_attacker + total_honest
        
        if total == 0:
            return {'attacker_ratio': 0, 'honest_ratio': 0, 'defense_gain': 0}
        
        attacker_ratio = total_attacker / total
        honest_ratio = total_honest / total
        
        # 理论上攻击者应该获得alpha比例的奖励
        # 如果实际比例低于alpha，说明防御有效
        defense_gain = self.alpha - attacker_ratio
        
        return {
            'attacker_ratio': attacker_ratio,
            'honest_ratio': honest_ratio,
            'defense_gain': defense_gain,
            'utb_ratio': self.utb_ratio
        }


def make_utb_env(alpha=0.35, gamma=0.5, utb_ratio=0.5, **kwargs):
    """创建UTB防御环境的便捷函数"""
    return UTBDefenseEnv(
        attacker_fraction=alpha,
        follower_fraction=gamma,
        utb_ratio=utb_ratio,
        **kwargs
    )


def compare_defense_effectiveness(
    alphas=[0.25, 0.30, 0.35, 0.40, 0.45],
    utb_ratios=[0.0, 0.25, 0.5, 0.75, 1.0],
    n_episodes=50,
    steps_per_episode=1000
):
    """
    比较不同UTB参数下的防御效果
    
    参数：
        alphas: 测试的攻击者算力列表
        utb_ratios: 测试的UTB比率列表
        n_episodes: 每个配置的测试回合数
        steps_per_episode: 每回合步数
    
    返回：
        results: 比较结果
    """
    results = []
    
    for alpha in alphas:
        for utb_ratio in utb_ratios:
            env = UTBDefenseEnv(
                attacker_fraction=alpha,
                utb_ratio=utb_ratio
            )
            
            total_reward = 0
            for ep in range(n_episodes):
                obs, info = env.reset()
                episode_reward = 0
                
                for step in range(steps_per_episode):
                    # 使用简单的自私挖矿策略
                    action = simple_selfish_mining_policy(obs)
                    obs, reward, terminated, truncated, info = env.step(action)
                    episode_reward += reward
                    
                    if terminated or truncated:
                        break
                
                total_reward += episode_reward
            
            avg_reward = total_reward / n_episodes
            
            results.append({
                'alpha': alpha,
                'utb_ratio': utb_ratio,
                'avg_reward': avg_reward,
                'defense_effectiveness': env.get_defense_effectiveness()
            })
            
            env.close()
    
    return results


def simple_selfish_mining_policy(state):
    """
    简单的自私挖矿策略（用于测试）
    
    基于SM1策略：
    - 如果攻击者落后，采纳诚实链
    - 如果攻击者领先1，发布
    - 否则等待
    """
    if len(state) < 2:
        return 2  # wait
    
    a, h = int(state[0]), int(state[1])
    
    if a < h:
        return 0  # adopt
    elif a == h + 1 and h > 0:
        return 1  # override
    elif a > 20:  # 达到最大隐藏块数
        return 1  # override
    else:
        return 2  # wait

