"""
批量评估所有训练好的模型
生成完整的评估结果用于 Figure 3
"""

import os
import sys
import glob
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.evaluate import evaluate_model, save_results


def find_models(base_dir="./models"):
    """查找所有训练好的模型"""
    models = []
    
    # 查找所有 final 模型
    final_pattern = os.path.join(base_dir, "bitcoin_alpha_*_final.zip")
    final_models = glob.glob(final_pattern)
    
    for model_path in final_models:
        # 从文件名提取 alpha
        match = re.search(r'alpha_([0-9.]+)_', model_path)
        if match:
            alpha = float(match.group(1))
            models.append((alpha, model_path))
    
    # 也查找 best_model
    best_pattern = os.path.join(base_dir, "best_bitcoin_alpha_*", "best_model.zip")
    best_models = glob.glob(best_pattern)
    
    for model_path in best_models:
        match = re.search(r'alpha_([0-9.]+)_', model_path)
        if match:
            alpha = float(match.group(1))
            # 如果已经有 final 模型，优先使用 final
            if not any(a == alpha for a, _ in models):
                models.append((alpha, model_path))
    
    return sorted(models, key=lambda x: x[0])


def main():
    print("="*60)
    print("批量评估 Bitcoin 模型")
    print("="*60)
    
    models = find_models()
    
    if not models:
        print("❌ 未找到任何模型！")
        print("请确保模型文件在 ./models/ 目录下")
        return
    
    print(f"\n找到 {len(models)} 个模型：")
    for alpha, path in models:
        print(f"  α={alpha:.2f}: {os.path.basename(path)}")
    
    print("\n开始评估...")
    print("="*60)
    
    results = []
    
    for i, (alpha, model_path) in enumerate(models, 1):
        print(f"\n[{i}/{len(models)}] 评估 α={alpha:.2f}...")
        print(f"模型: {os.path.basename(model_path)}")
        
        try:
            result = evaluate_model(
                model_path=model_path,
                protocol="bitcoin",
                alpha=alpha,
                gamma=0.5,
                n_episodes=50,  # 可以增加到 100 获得更准确结果
                verbose=1
            )
            results.append(result)
            print(f"✅ 完成: 相对奖励 = {result['mean_reward_fraction']:.4f}")
        except Exception as e:
            print(f"❌ 评估失败: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not results:
        print("\n❌ 没有成功评估的模型！")
        return
    
    # 保存结果
    output_path = "./results/bitcoin_full_evaluation.csv"
    save_results(results, output_path)
    
    print("\n" + "="*60)
    print("✅ 评估完成！")
    print(f"结果已保存到: {output_path}")
    print("="*60)
    
    # 显示摘要
    print("\n📊 评估摘要：")
    print("-" * 60)
    print(f"{'α':<8} {'相对奖励':<12} {'vs 诚实':<12} {'超额收益':<12}")
    print("-" * 60)
    
    for r in results:
        alpha = r['alpha']
        reward = r['mean_reward_fraction']
        honest = alpha
        excess = reward - honest
        excess_pct = (excess / honest * 100) if honest > 0 else 0
        
        print(f"{alpha:<8.2f} {reward:<12.4f} {reward-honest:+.4f} ({excess_pct:+.1f}%)")
    
    print("-" * 60)
    
    print("\n💡 下一步：")
    print(f"  生成 Figure 3: python -m src.cli plot --results {output_path}")


if __name__ == "__main__":
    main()

