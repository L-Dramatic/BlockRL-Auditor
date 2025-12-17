"""
T3: 训练脚本测试
快速验证训练脚本是否能正常工作（不实际训练太久）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_training_script():
    """测试训练脚本基本功能"""
    print("="*60)
    print("T3: 训练脚本测试（快速验证）")
    print("="*60)
    
    try:
        from src.agents.train import train_selfish_mining
        
        print("\n[1] 导入训练函数...")
        print("[OK] 训练函数导入成功")
        
        print("\n[2] 检查 Stable-Baselines3 是否可用...")
        import stable_baselines3
        print(f"[OK] Stable-Baselines3 版本: {stable_baselines3.__version__}")
        
        print("\n[3] 快速训练测试（100步）...")
        print("    （这可能需要1-2分钟，请稍候...）")
        
        # 临时禁用 tensorboard 日志（避免依赖问题）
        import warnings
        warnings.filterwarnings('ignore')
        
        model, env = train_selfish_mining(
            protocol="bitcoin",
            alpha=0.35,
            gamma=0.5,
            total_timesteps=100,  # 只训练100步用于测试
            verbose=0,  # 静默模式
            save_path="./tests/temp_models",
            log_path=None  # 禁用 tensorboard
        )
        
        print("[OK] 训练脚本运行成功")
        print(f"  - 模型类型: {type(model).__name__}")
        print(f"  - 环境: {env}")
        
        print("\n[4] 测试模型预测...")
        state, info = env.reset()  # Gymnasium 返回 (obs, info)
        action, _states = model.predict(state, deterministic=True)
        print(f"[OK] 模型预测成功")
        print(f"  - 状态: {state}")
        print(f"  - 动作: {action}")
        
        # 清理临时文件
        import shutil
        if os.path.exists("./tests/temp_models"):
            shutil.rmtree("./tests/temp_models")
        if os.path.exists("./tests/temp_logs"):
            shutil.rmtree("./tests/temp_logs")
        
        print("\n" + "="*60)
        print("[SUCCESS] T3 测试通过！训练脚本工作正常")
        print("="*60)
        return True
        
    except ImportError as e:
        print(f"\n[FAIL] 导入失败: {e}")
        print("提示: 请安装 stable-baselines3")
        print("      pip install stable-baselines3")
        return False
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)
        return False

if __name__ == "__main__":
    success = test_training_script()
    sys.exit(0 if success else 1)

