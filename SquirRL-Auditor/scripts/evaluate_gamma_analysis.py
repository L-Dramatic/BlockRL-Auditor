"""
Gamma参数分析 - 评估脚本
评估不同gamma值下的攻击收益
"""

import subprocess
import sys
import csv
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 实验参数
PROTOCOL = "bitcoin"
ALPHA = 0.35
GAMMA_VALUES = [0.0, 0.25, 0.5, 0.75, 1.0]
N_EPISODES = 50

def find_model(gamma: float) -> Path:
    """查找指定gamma的模型"""
    models_dir = PROJECT_ROOT / "models"
    
    if gamma == 0.5:
        # gamma=0.5是默认值，查找标准Bitcoin模型
        pattern = f"best_bitcoin_alpha_{ALPHA:.2f}_*"
        matches = list(models_dir.glob(pattern))
        if not matches:
            # 尝试不带best前缀的
            pattern2 = f"bitcoin_alpha_{ALPHA:.2f}_2*"
            matches = list(models_dir.glob(pattern2))
    else:
        # 查找带gamma的模型
        gamma_str = f"{gamma:.2f}"
        pattern = f"best_bitcoin_alpha_{ALPHA:.2f}_gamma_{gamma_str}_*"
        matches = list(models_dir.glob(pattern))
        
        if not matches:
            # 尝试不带best前缀的final模型
            pattern2 = f"bitcoin_alpha_{ALPHA:.2f}_gamma_{gamma_str}_*_final*"
            matches = list(models_dir.glob(pattern2))
    
    if matches:
        # 返回最新的
        return sorted(matches, key=lambda p: p.stat().st_mtime)[-1]
    
    return None

def evaluate_single(gamma: float) -> dict:
    """评估单个模型"""
    print(f"\nEvaluating Gamma={gamma}...")
    
    model_path = find_model(gamma)
    
    if not model_path:
        print(f"  [X] Model not found for gamma={gamma}")
        return None
    
    # 查找best_model.zip
    if model_path.is_dir():
        model_file = model_path / "best_model.zip"
        if not model_file.exists():
            model_file = model_path
    else:
        model_file = model_path
    
    print(f"  Model: {model_file}")
    
    cmd = [
        sys.executable, "-m", "src.cli", "evaluate",
        str(model_file),
        "--alpha", str(ALPHA),
        "--gamma", str(gamma),
        "--episodes", str(N_EPISODES)
    ]
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  [X] Evaluation failed")
        print(result.stderr)
        return None
    
    # 解析输出
    output = result.stdout
    print(output)
    
    # 提取结果
    metrics = {
        'gamma': gamma,
        'alpha': ALPHA,
        'protocol': PROTOCOL
    }
    
    for line in output.split('\n'):
        if 'Mean reward fraction' in line:
            try:
                metrics['mean_reward_fraction'] = float(line.split(':')[1].strip().split()[0])
            except:
                pass
        elif 'Relative gain' in line:
            try:
                metrics['relative_gain'] = float(line.split(':')[1].strip().split()[0])
            except:
                pass
    
    return metrics

def main():
    print("="*60)
    print("Gamma Analysis - Evaluation")
    print(f"Protocol: {PROTOCOL}, Alpha: {ALPHA}")
    print("="*60)
    
    results = []
    
    for gamma in GAMMA_VALUES:
        result = evaluate_single(gamma)
        if result:
            results.append(result)
    
    # 保存结果
    output_file = PROJECT_ROOT / "results" / "gamma_analysis_evaluation.csv"
    
    if results:
        fieldnames = ['protocol', 'alpha', 'gamma', 'mean_reward_fraction', 'relative_gain']
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n[OK] Results saved to: {output_file}")
        
        # 打印摘要
        print("\n" + "="*60)
        print("Results Summary")
        print("="*60)
        print(f"{'Gamma':<10} {'Reward Fraction':<18} {'Excess Reward':<15}")
        print("-"*45)
        for r in results:
            reward = r.get('mean_reward_fraction', 0)
            gain = reward - ALPHA
            print(f"{r['gamma']:<10} {reward:<18.4f} {gain:+.4f}")
    else:
        print("\n[X] No evaluation results")

if __name__ == "__main__":
    main()
