"""
批量训练 Ethereum 所有 alpha 值的模型
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.train import train_selfish_mining


def train_ethereum_models():
    """训练所有 Ethereum 模型"""
    
    print("="*60)
    print("批量训练 Ethereum 模型")
    print("="*60)
    
    alphas = [0.25, 0.30, 0.35, 0.40, 0.45]
    
    print(f"\n训练配置：")
    print(f"  协议: Ethereum")
    print(f"  Alpha 值: {alphas}")
    print(f"  每个模型训练 100,000 步")
    print(f"  预计总时间: ~75 分钟")
    print("\n" + "="*60)
    
    for i, alpha in enumerate(alphas, 1):
        print(f"\n[{i}/{len(alphas)}] 训练 α={alpha:.2f}...")
        
        try:
            train_selfish_mining(
                protocol="ethereum",
                alpha=alpha,
                gamma=0.5,
                total_timesteps=100000,
                learning_rate=1e-4,
                save_path="./models",
                log_path="./logs",
                verbose=1
            )
            print(f"✅ α={alpha:.2f} 训练完成")
        except Exception as e:
            print(f"❌ α={alpha:.2f} 训练失败: {e}")
            import traceback
            traceback.print_exc()
            continue
        except KeyboardInterrupt:
            print(f"\n⚠️  训练被用户中断")
            return
    
    print("\n" + "="*60)
    print("✅ 所有 Ethereum 模型训练完成！")
    print("="*60)
    print("\n💡 下一步：")
    print("  评估模型: python scripts/batch_evaluate_ethereum.py")
    print("  生成对比图: python scripts/plot_three_protocols.py")


if __name__ == "__main__":
    train_ethereum_models()

