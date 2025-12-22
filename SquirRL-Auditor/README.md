# SquirRL-Auditor

基于深度强化学习的区块链激励机制攻击分析工具

## 项目简介

本项目基于 [SquirRL (NDSS 2020)](https://www.ndss-symposium.org/ndss-paper/squirrl-automating-attack-analysis-on-blockchain-incentive-mechanisms-with-deep-reinforcement-learning/) 论文，使用现代化的强化学习框架（Stable-Baselines3）重新实现并扩展了区块链自私挖矿攻击的分析。

### 核心功能

- ✅ **基础复现**：复现论文中 Bitcoin 自私挖矿攻击 (Figure 3)
- ✅ **协议扩展**：支持 Bitcoin / GHOST / Ethereum 协议
- ✅ **防御机制**：UTB (Uniform Tie-Breaking) 防御分析
- ✅ **命令行工具**：配置化的实验运行工具
- ✅ **Web 可视化**：Streamlit 交互式仪表盘
- ✅ **Block Withholding**：矿池间博弈攻击分析

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

# 评估模型
python auditor.py evaluate ./models/best_model.zip --alpha 0.35

# 生成 Figure 3
python auditor.py plot --results ./results/evaluation.csv

# 查看环境信息
python auditor.py info
```

### 4. Docker 部署

```bash
# 构建并运行
docker-compose up --build

# 访问 http://localhost:8501
```

## 项目结构

```
SquirRL-Auditor/
├── app/                    # Streamlit Web 应用
│   ├── main.py            # 主页面
│   └── pages/             # 功能页面
├── src/
│   ├── environment/       # 区块链模拟环境
│   │   ├── base_env.py    # 基础环境
│   │   ├── gym_wrapper.py # Gymnasium 包装器
│   │   ├── ghost_env.py   # GHOST 协议环境
│   │   ├── utb_defense.py # UTB 防御环境
│   │   └── block_withholding.py  # BW 博弈环境
│   ├── agents/            # 训练和评估
│   │   ├── train.py       # 训练脚本
│   │   └── evaluate.py    # 评估脚本
│   ├── visualization/     # 可视化工具
│   └── cli.py             # 命令行接口
├── configs/               # 实验配置文件
│   ├── default.yaml       # 默认配置
│   ├── ghost.yaml         # GHOST 配置
│   ├── ethereum.yaml      # Ethereum 配置
│   ├── utb.yaml           # UTB 防御配置
│   └── block_withholding.yaml  # BW 配置
├── models/                # 训练好的模型
├── results/               # 实验结果
├── tests/                 # 单元测试
├── auditor.py             # 命令行工具入口
├── requirements.txt       # 依赖列表
├── Dockerfile             # Docker 配置
└── docker-compose.yml     # Docker Compose 配置
```

## 实验结果

### Figure 3 复现

Bitcoin 自私挖矿攻击收益曲线，验证了论文中的理论分析：

- α=35% 时，攻击者可获得约 39.4% 的区块奖励
- 相比诚实挖矿，收益提升约 12.7%

### 协议安全性对比

| 协议 | 攻击阈值 | 安全性 |
|------|---------|--------|
| Bitcoin | ~25% | ⭐ |
| GHOST | ~30% | ⭐⭐⭐ |
| Ethereum | ~35% | ⭐⭐⭐⭐ |

## 技术栈

- **强化学习**: Stable-Baselines3, Gymnasium
- **深度学习**: PyTorch
- **Web 框架**: Streamlit
- **可视化**: Plotly, Matplotlib
- **容器化**: Docker

## 开发状态

- [x] Week 1: 基础环境搭建
- [x] Week 2: 扩展功能开发
- [x] Week 3: 工具整合与可视化

## 参考文献

- SquirRL: Automating Attack Analysis on Blockchain Incentive Mechanisms with Deep Reinforcement Learning (NDSS 2020)
- Majority is not Enough: Bitcoin Mining is Vulnerable (Eyal & Sirer, 2014)
- GHOST: Secure High-Rate Transaction Processing in Bitcoin (Sompolinsky & Zohar, 2015)

## 团队

本项目由5人团队开发，作为区块链导论课程项目。

## 许可证

本项目仅用于学术研究和教育目的。
