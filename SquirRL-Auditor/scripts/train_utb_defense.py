"""
批量训练 UTB 防御机制下的模型
测试不同 UTB 参数对自私挖矿的防御效果
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.train import train_selfish_mining


def train_utb_models():
    """训练不同 UTB 参数下的模型"""
    
    print("="*60)
    print("批量训练 UTB Defense 模型")
    print("="*60)
    
    # 测试参数：固定 α=0.35（自私挖矿有明显收益的点）
    # 变化 UTB 比率：0.0（无防御）, 0.25, 0.5, 0.75, 1.0（全额叔块奖励）
    alpha = 0.35
    utb_ratios = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    print(f"\n训练配置：")
    print(f"  固定 α = {alpha}")
    print(f"  UTB 比率: {utb_ratios}")
    print(f"  每个模型训练 100,000 步")
    print("\n" + "="*60)
    
    for i, utb_ratio in enumerate(utb_ratios, 1):
        print(f"\n[{i}/{len(utb_ratios)}] 训练 UTB={utb_ratio:.2f}...")
        
        try:
            train_selfish_mining(
                protocol="utb",
                alpha=alpha,
                gamma=0.5,
                total_timesteps=100000,
                learning_rate=1e-4,
                save_path="./models",
                log_path="./logs",
                verbose=1,
                env_kwargs={'utb_ratio': utb_ratio}
            )
            print(f"✅ UTB={utb_ratio:.2f} 训练完成")
        except Exception as e:
            print(f"❌ UTB={utb_ratio:.2f} 训练失败: {e}")
            import traceback
            traceback.print_exc()
            continue
        except KeyboardInterrupt:
            print(f"\n⚠️  训练被用户中断")
            return
    
    print("\n" + "="*60)
    print("✅ 所有 UTB 模型训练完成！")
    print("="*60)
    print("\n💡 下一步：")
    print("  评估防御效果: python scripts/evaluate_utb_defense.py")


if __name__ == "__main__":
    train_utb_models()

