# SquirRL-Auditor

基于深度强化学习的区块链激励机制攻击分析工具

## 项目简介

本项目基于 [SquirRL (NDSS 2020)](https://www.ndss-symposium.org/ndss-paper/squirrl-automating-attack-analysis-on-blockchain-incentive-mechanisms-with-deep-reinforcement-learning/) 论文，使用现代化的强化学习框架（Stable-Baselines3）重新实现并扩展了区块链自私挖矿攻击的分析。

### 核心功能

- ✅ **基础复现**：复现论文中 Bitcoin 自私挖矿攻击 (Figure 3)
- ✅ **协议扩展**：支持 Bitcoin / GHOST / Ethereum 三种协议对比分析
- ✅ **防御机制**：UTB (Uncles-To-Block) 防御效果评估
- ✅ **参数分析**：Gamma (γ) 参数对攻击效果的影响研究
- ✅ **命令行工具**：配置化的实验运行工具
- ✅ **Web 可视化**：Streamlit 交互式仪表盘

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行 Web 界面

```bash
# Windows
run_app.bat

# Linux/Mac
./run_app.sh

# 或直接运行
streamlit run app/main.py
```

然后打开浏览器访问 http://localhost:8501

### 3. 命令行使用

```bash
# 训练 Bitcoin 自私挖矿策略
python auditor.py train --protocol bitcoin --alpha 0.35

# 训练 GHOST 协议
python auditor.py train --protocol ghost --alpha 0.35

# 训练 Ethereum 协议
python auditor.py train --protocol ethereum --alpha 0.35

# 训练 UTB 防御
python auditor.py train --protocol utb --alpha 0.35 --utb-ratio 0.5

# 评估模型
python auditor.py evaluate ./models/best_model.zip --alpha 0.35

# 生成结果图
python auditor.py plot --results ./results/evaluation.csv
```

### 4. 批量训练脚本

```bash
# 训练所有 Bitcoin 模型 (α = 0.05 ~ 0.45)
python scripts/batch_evaluate.py

# 训练所有 GHOST 模型
python scripts/batch_evaluate_ghost.py

# 训练所有 Ethereum 模型
python scripts/train_ethereum_all.py

# 训练 UTB 防御模型
python scripts/train_utb_defense.py

# 训练 Gamma 参数分析模型
python scripts/train_gamma_analysis.py
```

### 5. Docker 部署

```bash
# 构建并运行
docker-compose up --build

# 访问 http://localhost:8501
```

## 项目结构

```
SquirRL-Auditor/
├── app/                    # Streamlit Web 应用
│   ├── main.py            # 主入口
│   └── pages/             # 功能页面
│       ├── attack_animation.py    # 攻击模拟动画
│       ├── auto_demo.py           # 一键演示
│       ├── defense_evaluation.py  # 防御效果评估
│       ├── gamma_analysis.py      # Gamma 参数分析
│       └── protocol_comparison.py # 多协议对比
├── src/
│   ├── environment/       # 区块链模拟环境
│   │   ├── base_env.py    # Bitcoin 基础环境
│   │   ├── ghost_env.py   # GHOST 协议环境
│   │   ├── utb_defense.py # UTB 防御环境
│   │   └── gym_wrapper.py # Gymnasium 包装器
│   ├── agents/            # 训练和评估
│   │   ├── train.py       # 训练脚本
│   │   └── evaluate.py    # 评估脚本
│   ├── visualization/     # 可视化工具
│   └── cli.py             # 命令行接口
├── scripts/               # 批量实验脚本
│   ├── batch_evaluate.py          # Bitcoin 批量评估
│   ├── batch_evaluate_ghost.py    # GHOST 批量评估
│   ├── batch_evaluate_ethereum.py # Ethereum 批量评估
│   ├── train_utb_defense.py       # UTB 防御训练
│   ├── evaluate_utb_defense.py    # UTB 防御评估
│   ├── train_gamma_analysis.py    # Gamma 分析训练
│   └── plot_*.py                  # 绘图脚本
├── configs/               # 实验配置文件
│   ├── default.yaml       # 默认配置 (Bitcoin)
│   ├── ghost.yaml         # GHOST 配置
│   ├── ethereum.yaml      # Ethereum 配置
│   └── utb.yaml           # UTB 防御配置
├── models/                # 训练好的模型 (.zip)
├── results/               # 实验结果 (.csv, .png, .pdf)
├── tests/                 # 单元测试
├── auditor.py             # 命令行工具入口
├── requirements.txt       # 依赖列表
├── Dockerfile             # Docker 配置
└── docker-compose.yml     # Docker Compose 配置
```

## 实验结果

### 1. Figure 3 复现 (Bitcoin 自私挖矿)

Bitcoin 自私挖矿攻击收益曲线，验证了论文中的理论分析：

- α = 35% 时，攻击者可获得约 39.4% 的区块奖励
- 相比诚实挖矿，收益提升约 12.7%

### 2. 三协议安全性对比

| 协议 | 攻击阈值 | 高算力安全性 | 特点 |
|------|---------|-------------|------|
| Bitcoin | ~25% | ⭐⭐ | 最长链规则 |
| GHOST | ~30% | ⭐⭐⭐⭐ | 考虑叔块权重，更安全 |
| Ethereum | ~35% | ⭐⭐⭐ | 叔块奖励，低算力安全但高算力反而更易受攻击 |

### 3. UTB 防御效果

UTB (Uncles-To-Block) 防御机制可以有效降低自私挖矿攻击收益：

- 当 UTB ratio = 0.5 时，攻击超额收益降低约 40%
- 发现"过度防御"现象：UTB ratio 过高时反而增加攻击者收益

### 4. Gamma 参数分析

研究网络跟随者比例 (γ) 对攻击效果的影响：

| γ 值 | 攻击效果 | 结论 |
|------|---------|------|
| γ < 0.5 | 无效 | 攻击几乎无法获利 |
| γ = 0.5 | 临界点 | 攻击开始有效 |
| γ = 1.0 | 最大化 | 35% 算力可获得 48% 收益 |

## 技术栈

- **强化学习**: Stable-Baselines3 (DQN), Gymnasium
- **深度学习**: PyTorch
- **Web 框架**: Streamlit
- **可视化**: Plotly, Matplotlib
- **容器化**: Docker, Docker Compose

## 创新点

1. **多协议对比**：首次在同一框架下对比 Bitcoin、GHOST、Ethereum 三种协议的自私挖矿安全性
2. **UTB 防御分析**：深入研究 UTB 防御机制的效果和局限性
3. **Gamma 参数研究**：系统分析网络传播能力对攻击效果的影响
4. **交互式可视化**：提供直观的 Web 界面展示实验结果

## 参考文献

- SquirRL: Automating Attack Analysis on Blockchain Incentive Mechanisms with Deep Reinforcement Learning (NDSS 2020)
- Majority is not Enough: Bitcoin Mining is Vulnerable (Eyal & Sirer, 2014)
- GHOST: Secure High-Rate Transaction Processing in Bitcoin (Sompolinsky & Zohar, 2015)

## 团队

本项目由5人团队开发，作为区块链导论课程项目。

## 许可证

本项目仅用于学术研究和教育目的。
