"""
T2: Gym 包装器测试
测试 BitcoinSelfishMiningEnv 是否能正常工作
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_gym_wrapper():
    """测试Gym包装器基本功能"""
    print("="*60)
    print("T2: Gym 包装器测试")
    print("="*60)
    
    try:
        from src.environment.gym_wrapper import BitcoinSelfishMiningEnv
        
        print("\n[1] 创建环境...")
        env = BitcoinSelfishMiningEnv(alpha=0.35, gamma=0.5)
        print(f"[OK] 环境创建成功")
        print(f"  - 动作空间: {env.action_space}")
        print(f"  - 观察空间: {env.observation_space}")
        print(f"  - 状态数量: {env.observation_space.n}")
        
        print("\n[2] 测试重置...")
        state, info = env.reset()
        print(f"[OK] 环境重置成功")
        print(f"  - 初始状态索引: {state}")
        print(f"  - 状态信息: {env.get_state_info(state)}")
        print(f"  - Info: {info}")
        
        print("\n[3] 测试执行动作...")
        total_reward = 0
        for i in range(10):
            action = env.action_space.sample()  # 随机动作
            next_state, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
            if i < 3:  # 只打印前3步
                print(f"  Step {i+1}: action={action}, state={next_state}, reward={reward:.4f}")
            
            if terminated or truncated:
                print(f"  Episode ended at step {i+1}")
                break
        
        print(f"[OK] 动作执行成功")
        print(f"  - 总奖励: {total_reward:.4f}")
        print(f"  - 总步数: {info['steps']}")
        
        print("\n[4] 测试工厂函数...")
        from src.environment.gym_wrapper import make_env
        
        env2 = make_env(protocol="bitcoin", alpha=0.40)
        print(f"[OK] 工厂函数正常工作")
        print(f"  - 创建的环境alpha: {env2.alpha}")
        
        print("\n" + "="*60)
        print("[SUCCESS] T2 测试通过！Gym包装器工作正常")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)
        return False

if __name__ == "__main__":
    success = test_gym_wrapper()
    sys.exit(0 if success else 1)

