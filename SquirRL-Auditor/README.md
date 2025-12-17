# SquirRL-Auditor

基于深度强化学习的区块链激励机制攻击分析工具

## 项目简介

本项目基于 [SquirRL (NDSS 2020)](https://www.ndss-symposium.org/ndss-paper/squirrl-automating-attack-analysis-on-blockchain-incentive-mechanisms-with-deep-reinforcement-learning/) 论文，使用现代化的强化学习框架（Stable-Baselines3）重新实现并扩展了区块链自私挖矿攻击的分析。

### 核心功能

- ✅ **基础复现**：复现论文中 Bitcoin 自私挖矿攻击
- ✅ **协议扩展**：支持 Ethereum/GHOST 协议
- ✅ **防御机制**：UTB (Uniform Tie-Breaking) 防御分析
- ✅ **命令行工具**：配置化的实验运行工具
- ⏰ **Block Withholding**：矿池间博弈攻击（可选）

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行基础实验

```bash
# 训练 Bitcoin 自私挖矿策略
python auditor.py train --protocol bitcoin --alpha 0.35

# 评估模型
python auditor.py evaluate --model models/bitcoin_baseline.zip
```

## 项目结构

```
SquirRL-Auditor/
├── src/
│   ├── environment/        # 区块链模拟环境
│   ├── agents/             # 训练和评估脚本
│   └── visualization/      # 可视化工具
├── configs/                # 实验配置文件
├── models/                 # 训练好的模型
├── results/                # 实验结果
├── tests/                  # 单元测试
├── auditor.py              # 命令行工具
└── requirements.txt        # 依赖列表
```

## 开发状态

- [x] Week 1: 基础环境搭建
- [ ] Week 2: 扩展功能开发
- [ ] Week 3: 工具整合与文档

## 参考文献

- SquirRL: Automating Attack Analysis on Blockchain Incentive Mechanisms with Deep Reinforcement Learning (NDSS 2020)
- Majority is not Enough: Bitcoin Mining is Vulnerable (Eyal & Sirer, 2014)

## 团队

本项目由5人团队开发，作为区块链安全课程项目。

## 许可证

本项目仅用于学术研究和教育目的。

