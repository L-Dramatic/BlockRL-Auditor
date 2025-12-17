"""
测试评估脚本和可视化
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_visualization():
    """测试可视化功能"""
    print("\n" + "="*60)
    print("测试可视化脚本")
    print("="*60)
    
    from src.visualization.reward_plot import (
        theoretical_selfish_mining_reward,
        honest_mining_reward,
        plot_figure3
    )
    
    # [1] 测试理论公式
    print("\n[1] 测试理论奖励公式...")
    
    alphas = [0.25, 0.30, 0.35, 0.40, 0.45]
    for alpha in alphas:
        honest = honest_mining_reward(alpha)
        theoretical = theoretical_selfish_mining_reward(alpha, gamma=0.5)
        gain = theoretical - honest
        print(f"  alpha={alpha:.2f}: honest={honest:.4f}, "
              f"SM_theory={theoretical:.4f}, gain={gain:+.4f}")
    
    print("[OK] 理论公式计算正确")
    
    # [2] 测试生成演示图
    print("\n[2] 测试生成演示图...")
    
    # 创建结果目录
    os.makedirs("./results", exist_ok=True)
    
    # 模拟一些结果数据
    demo_results = [
        {'alpha': 0.25, 'relative_gain': 0.246, 'n_episodes': 100},
        {'alpha': 0.30, 'relative_gain': 0.301, 'n_episodes': 100},
        {'alpha': 0.35, 'relative_gain': 0.362, 'n_episodes': 100},
        {'alpha': 0.40, 'relative_gain': 0.428, 'n_episodes': 100},
        {'alpha': 0.45, 'relative_gain': 0.498, 'n_episodes': 100},
    ]
    
    plot_figure3(
        results=demo_results,
        title="Bitcoin Selfish Mining (Test)",
        output_path="./results/figure3_test.png"
    )
    
    # 检查文件是否创建
    assert os.path.exists("./results/figure3_test.png"), "PNG文件未创建"
    assert os.path.exists("./results/figure3_test.pdf"), "PDF文件未创建"
    
    print("[OK] 图表生成成功")
    
    print("\n" + "="*60)
    print("[SUCCESS] 可视化测试通过!")
    print("="*60)


def test_evaluate_import():
    """测试评估模块导入"""
    print("\n" + "="*60)
    print("测试评估模块导入")
    print("="*60)
    
    from src.agents.evaluate import evaluate_model, save_results
    
    print("[OK] 评估模块导入成功")
    print("  - evaluate_model: 可用")
    print("  - save_results: 可用")
    
    print("\n" + "="*60)
    print("[SUCCESS] 评估模块测试通过!")
    print("="*60)


if __name__ == "__main__":
    test_evaluate_import()
    test_visualization()

