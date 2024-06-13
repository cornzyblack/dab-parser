import yaml
import re
from typing import Optional, Union, List, Any
from pathlib import Path

FILE_PATH_TYPE = Union[Path, str]

def get_yaml_content(file_path: Path|str) -> str:
    """
    Parses a YAML file

    Parameters
    ----------
    file_path : Path|str
        The filepath of the YAML file

    Returns
    -------
    str
        The YAML file as a string
    """
    yaml_content = ''
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError as e:
        # TODO: log error
        print(e)
    return yaml_content

def get_yaml_to_dict(yaml_content: str) -> dict:
    """
    Convert a YAML file into a dictionary

    Parameters
    ----------
    yaml_content : str
        The yaml file as a string

    Returns
    -------
    dict
        The yaml file as a dictionary
    """
    yaml_asdict = {}
    try:
        yaml_asdict = yaml.safe_load(yaml_content)
    except yaml.scanner.ScannerError as e:
        # TODO: log error
        print(e)
    return yaml_asdict

def flatten_dict(d: dict, parent_key: str='', sep: str='.') -> dict:
    """Flatten a nested dictionary."""
    items: List[Any] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, new_key, sep=sep).items())
                else:
                    items.append((new_key, item))
        else:
            items.append((new_key, v))
    return dict(items)

def get_dab_rendered_vars(flattened_vars_dict):
    rendered_vars_dict = {key.replace('.default', '').replace('variables.', 'var.'): value for key, value in flattened_vars_dict.items()}
    return rendered_vars_dict

def get_dab_variables_def(parsed_yaml_dict: dict) -> dict:
    """
    Checks if a JSON is valid variables' config file

    Parameters
    ----------
    parsed_yaml_dict : dict
        The parsed YAML file as a dict

    Returns
    -------
    dict
        A dictionary containing the variables' definitions else an empty dictionary
    """
    return get_dab_rendered_vars(flatten_dict(parsed_yaml_dict))

def substitute_variables(yaml_content: str, substitution_dict: dict) -> str:
    pattern = re.compile(r'\$\{([^}]+)\}')
    def replace_match(match):
        key = match.group(1)
        return str(substitution_dict.get(key, match.group(0)))
    result = pattern.sub(replace_match, yaml_content)
    return result

def render_resources_yaml(resources_yaml_filepath: str, variables_yaml_file_path: Optional[FILE_PATH_TYPE] = None) -> str:
    resources_yaml_content = get_yaml_content(resources_yaml_filepath)
    resources_yaml_dict = get_yaml_to_dict(resources_yaml_content)
    if not variables_yaml_file_path:
        vars_dict = get_dab_variables_def(resources_yaml_dict)
    else:
        variables_yaml_content = get_yaml_content(variables_yaml_file_path)
        vars_dict = get_yaml_to_dict(variables_yaml_content)

        rendered_var_dict = get_dab_variables_def(vars_dict)
    return substitute_variables(resources_yaml_content, rendered_var_dict)

print(render_resources_yaml('resources.yaml', 'variables.yaml'))
