"""Configuration utilities."""

import os
import yaml
from typing import Dict, Any
from dotenv import load_dotenv


def load_env(env_path: str = '.env') -> None:
    """
    Load environment variables from .env file.

    Args:
        env_path: Path to .env file
    """
    load_dotenv(env_path)


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Dictionary containing configuration
    """
    if not os.path.exists(config_path):
        return get_default_config()

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        'scraping': {
            'max_items_per_source': 100,
            'request_timeout': 30,
            'rate_limit_delay': 2
        },
        'analysis': {
            'model': 'claude-sonnet-4-5-20250929',
            'max_tokens': 4000,
            'temperature': 0.3
        },
        'output': {
            'format': 'markdown',
            'directory': './output',
            'include_raw_data': True
        },
        'awareness_stages': [
            'unaware',
            'problem_aware',
            'solution_aware',
            'product_aware',
            'most_aware'
        ]
    }


def get_api_keys() -> Dict[str, str]:
    """
    Get API keys from environment variables.

    Returns:
        Dictionary of API keys
    """
    return {
        'anthropic': os.getenv('ANTHROPIC_API_KEY'),
        'reddit_client_id': os.getenv('REDDIT_CLIENT_ID'),
        'reddit_client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
        'reddit_user_agent': os.getenv('REDDIT_USER_AGENT', 'CustomerLanguageMiner/1.0'),
        'youtube': os.getenv('YOUTUBE_API_KEY')
    }
