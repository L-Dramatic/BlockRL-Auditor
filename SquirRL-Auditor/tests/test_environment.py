"""
T1: 环境验证测试
测试 environment.py 能否正常导入和运行
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """测试所有依赖能否正常导入"""
    print("测试导入依赖...")
    
    try:
        import numpy as np
        print("[OK] numpy imported successfully")
        
        import scipy
        print("[OK] scipy imported successfully")
        
        import matplotlib.pyplot as plt
        print("[OK] matplotlib imported successfully")
        
        import mdptoolbox
        print("[OK] mdptoolbox imported successfully")
        
        print("\n所有依赖导入成功！")
        return True
    except ImportError as e:
        print(f"[FAIL] 导入失败: {e}")
        return False

def test_environment():
    """测试环境是否能正常创建"""
    print("\n测试创建环境...")
    
    try:
        from src.environment.base_env import SM_env
        
        # 创建一个简单的环境
        env = SM_env(
            max_hidden_block=20,
            attacker_fraction=0.35,
            follower_fraction=0.5
        )
        
        print(f"[OK] 环境创建成功")
        print(f"  - 状态空间大小: {len(env._state_space)}")
        print(f"  - 攻击者算力: {env._alpha}")
        print(f"  - 跟随者比例: {env._gamma}")
        
        # 测试重置
        state = env.reset()
        print(f"[OK] 环境重置成功，初始状态: {state}")
        
        return True
    except Exception as e:
        print(f"[FAIL] 环境测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("="*60)
    print("T1: 环境验证测试")
    print("="*60)
    
    test1 = test_imports()
    test2 = test_environment()
    
    print("\n" + "="*60)
    if test1 and test2:
        print("[SUCCESS] T1 验证通过！environment.py 可以在现代Python环境运行")
    else:
        print("[FAIL] T1 验证失败，请检查依赖安装")
    print("="*60)

if __name__ == "__main__":
    main()

