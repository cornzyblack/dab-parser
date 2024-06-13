import ast
from pathlib import Path
from typing import Optional
from enum import IntEnum

FILE_PATHS = list[Path]


class Task:
    def __init__(self, task_file_path: Path| str, task_parameters: dict, job_parameters: Optional[dict] = None):
        self.task_file_path = task_file_path
        self.task_parameters = task_parameters
        self.job_parameters = job_parameters
    
class SniffPattern(IntEnum):
    FILE = 1
    DIR = 2

# TODO: validate if file is a Databricks script
    
def get_parsed_file(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)
    return tree

def get_py_files_in_dir(dir_path: str) -> FILE_PATHS:
    """Get all python files in a directory

    Args:
        dir_path (str): The full path of the directory

    Returns:
        DIRECTORY_LIST: A list of directory paths
    """
    _dir = Path(dir_path)
    return list(_dir.glob('**/*.py'))

def sniff_task_parameters_from_dir(file_paths: FILE_PATHS) -> dict[Path, list]:
    parameter_script_mapping = {}
    for file_path in file_paths:
        parameter_script_mapping[file_path] = sniff_task_parameters_from_file(file_path)
    return parameter_script_mapping

def sniff_task_parameters_from_file(file_path: str) -> list:
    script_nodes = get_parsed_file(file_path)
    return find_dbutils_widgets_get_calls(script_nodes)


def find_dbutils_widgets_set_calls(node) -> list:
    calls = []
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if isinstance(n.func.value, ast.Attribute):
                if (isinstance(n.func.value.value, ast.Name) and
                        n.func.value.value.id == 'dbutils' and
                        n.func.value.attr == 'jobs' and
                        n.func.value.attr == 'taskValues' and
                        n.func.attr == 'get'):
                    # Extract the argument
                    if n.args:
                        arg = n.args[0]
                        if isinstance(arg, ast.Constant):  # Python 3.8+
                            calls.append(arg.value)

    return calls


def find_dbutils_widgets_get_calls(node) -> list:
    calls = []
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            # Check if it's a call to dbutils.widgets.get
            if isinstance(n.func.value, ast.Attribute):
                if (isinstance(n.func.value.value, ast.Name) and
                        n.func.value.value.id == 'dbutils' and
                        n.func.value.attr == 'widgets' and
                        n.func.attr == 'get'):
                    # Extract the argument
                    if n.args:
                        arg = n.args[0]
                        if isinstance(arg, ast.Constant):  # Python 3.8+
                            calls.append(arg.value)

                if (isinstance(n.func.value.value, ast.Name) and
                        n.func.value.value.id == 'dbutils' and
                        n.func.value.attr == 'jobs' and
                        n.func.value.attr == 'taskValues' and
                        n.func.attr == 'get'):
                    # Extract the argument
                    if n.args:
                        arg = n.args[0]
                        if isinstance(arg, ast.Constant):  # Python 3.8+
                            calls.append(arg.value)

    return calls


