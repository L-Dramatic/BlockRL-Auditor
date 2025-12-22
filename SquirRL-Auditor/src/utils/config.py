"""
配置文件加载和管理工具
"""

import os
import yaml
from typing import Dict, Any, Optional


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载YAML配置文件
    
    参数：
        config_path (str): 配置文件路径
    
    返回：
        config (dict): 配置字典
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def save_config(config: Dict[str, Any], config_path: str):
    """
    保存配置到YAML文件
    
    参数：
        config (dict): 配置字典
        config_path (str): 保存路径
    """
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def merge_configs(base_config: Dict, override_config: Dict) -> Dict:
    """
    合并两个配置，override_config 中的值会覆盖 base_config
    
    参数：
        base_config (dict): 基础配置
        override_config (dict): 覆盖配置
    
    返回：
        merged (dict): 合并后的配置
    """
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置
    
    返回：
        config (dict): 默认配置字典
    """
    return {
        'environment': {
            'protocol': 'bitcoin',
            'alpha': 0.35,
            'gamma': 0.5,
            'max_hidden_block': 20,
            'stale_rate': 0.0,
            'know_alpha': True,
            'random': {
                'enabled': False,
                'dev': 0.0,
                'interval': [0.0, 0.5],
                'process': 'iid'
            }
        },
        'training': {
            'algorithm': 'DQN',
            'total_timesteps': 100000,
            'learning_rate': 1e-4,
            'buffer_size': 50000,
            'learning_starts': 1000,
            'batch_size': 32,
            'gamma_discount': 0.99,
            'target_update_interval': 1000,
            'exploration': {
                'initial_eps': 1.0,
                'final_eps': 0.05,
                'fraction': 0.1
            }
        },
        'evaluation': {
            'n_episodes': 100,
            'max_steps': 10000,
            'deterministic': True
        },
        'output': {
            'model_path': './models',
            'log_path': './logs',
            'results_path': './results',
            'tensorboard': False
        }
    }


def config_to_args(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    将嵌套配置转换为扁平的参数字典
    用于传递给训练函数
    
    参数：
        config (dict): 嵌套配置
    
    返回：
        args (dict): 扁平参数字典
    """
    env_config = config.get('environment', {})
    train_config = config.get('training', {})
    output_config = config.get('output', {})
    
    return {
        # 环境参数
        'protocol': env_config.get('protocol', 'bitcoin'),
        'alpha': env_config.get('alpha', 0.35),
        'gamma': env_config.get('gamma', 0.5),
        'max_hidden_block': env_config.get('max_hidden_block', 20),
        'stale_rate': env_config.get('stale_rate', 0.0),
        
        # 训练参数
        'total_timesteps': train_config.get('total_timesteps', 100000),
        'learning_rate': train_config.get('learning_rate', 1e-4),
        'buffer_size': train_config.get('buffer_size', 50000),
        'batch_size': train_config.get('batch_size', 32),
        'gamma_discount': train_config.get('gamma_discount', 0.99),
        
        # 输出参数
        'save_path': output_config.get('model_path', './models'),
        'log_path': output_config.get('log_path', './logs'),
    }

