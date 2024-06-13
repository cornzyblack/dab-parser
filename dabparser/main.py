import typer
import dab_parser.utils as utils
from typing_extensions import Annotated
from pathlib import Path
from typing import Optional

app = typer.Typer()

@app.command()
def main(variables_file: Annotated[Optional[str], typer.Argument()] = None):
    options = {1: utils.SniffPattern.FILE, 2: utils.SniffPattern.DIR}
    option_str = '\n1 for Files\n2 for Directory\n'
    selected_option = typer.prompt(f"Please choose a sniff 🐕 pattern {option_str}", type=int)

    while (selected_option not in options):
        selected_option = typer.prompt(f"Please choose a sniff 🐕 pattern {option_str}", type=int)

    selected_value = options[selected_option]
    typer.echo(f"Selected option: {selected_value}")

    if selected_value.value == 1:
        file_path_str = typer.prompt("Enter the file path", type=str)
        # validate file path
        file_path = Path(file_path_str)
        if file_path.exists():
            if file_path.suffix == '.py':
                print("Path exists 🙂")
                print(utils.sniff_task_parameters_from_file(file_path))

    if selected_value.value == 2:
        # validate directory path
        dir_path_str = typer.prompt("Enter the directory path for your files", type=str)
        dir_path = Path(dir_path_str)
        if dir_path.exists():
            print("Directory Path exists 🙂")
            py_files = utils.get_py_files_in_dir(dir_path)
            print(utils.sniff_task_parameters_from_dir(py_files))


if __name__ == '__main__':
    app()
