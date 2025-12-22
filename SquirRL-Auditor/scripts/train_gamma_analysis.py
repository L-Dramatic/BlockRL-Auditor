"""
Gamma参数分析 - 批量训练脚本
研究目标：分析跟随者比例(gamma)对自私挖矿攻击收益的影响

固定参数：
- 协议：Bitcoin
- α (攻击者算力)：0.35

变化参数：
- γ (跟随者比例)：0.0, 0.25, 0.5, 0.75, 1.0
"""

import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 实验参数
PROTOCOL = "bitcoin"
ALPHA = 0.35
GAMMA_VALUES = [0.0, 0.25, 0.5, 0.75, 1.0]
TOTAL_TIMESTEPS = 100000

def train_single(gamma: float):
    """训练单个gamma值的模型"""
    print(f"\n{'='*60}")
    print(f"训练 Gamma={gamma}")
    print(f"{'='*60}")
    
    cmd = [
        sys.executable, "-m", "src.cli", "train",
        "--protocol", PROTOCOL,
        "--alpha", str(ALPHA),
        "--gamma", str(gamma),
        "--timesteps", str(TOTAL_TIMESTEPS)
    ]
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode == 0:
        print(f"[OK] Gamma={gamma} training completed")
    else:
        print(f"[FAIL] Gamma={gamma} training failed")
    
    return result.returncode == 0

def main():
    print("="*60)
    print("Gamma参数分析 - 批量训练")
    print(f"协议: {PROTOCOL}")
    print(f"Alpha: {ALPHA}")
    print(f"Gamma值: {GAMMA_VALUES}")
    print("="*60)
    
    # 需要训练的gamma值（gamma=0.5使用现有模型，其他需要训练）
    to_train = [g for g in GAMMA_VALUES if g != 0.5]
    
    print(f"\nWill train {len(to_train)} models (gamma=0.5 uses existing model)")
    for gamma in to_train:
        print(f"  gamma={gamma}: will train")
    
    # 开始训练
    success = 0
    failed = 0
    
    for gamma in to_train:
        if train_single(gamma):
            success += 1
        else:
            failed += 1
    
    # 总结
    print("\n" + "="*60)
    print("训练完成")
    print(f"成功: {success}, 失败: {failed}")
    print("="*60)

if __name__ == "__main__":
    main()


