"""Utility functions"""
import yaml

def load_config(config_file='config/config.yaml'):
    """Load configuration from YAML file"""
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)
