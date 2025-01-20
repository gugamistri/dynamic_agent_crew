import os
import yaml


def load_yaml_config(file_path):
    """
    Loads a YAML configuration file.

    :param file_path: Path to the YAML file.
    :return: Parsed data from the YAML file.
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"YAML file not found: {file_path}") from e


def create_methods(configs, method_creator, storage, decorator, cls):
    """
    Dynamically creates methods and registers them with the corresponding decorator.

    :param configs: Configuration data for creating the methods.
    :param method_creator: Function to create the method (agent or task).
    :param storage: Dictionary for storing the created methods.
    :param decorator: Decorator to apply to the created method.
    :param cls: Class where the methods will be added.
    """
    for name, config in configs.items():
        method = method_creator(name, config)
        decorated_method = decorator(method)
        setattr(cls, name, decorated_method)
        storage[name] = decorated_method