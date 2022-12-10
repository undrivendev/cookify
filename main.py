import glob
import json
import os
import shutil
from typing import Callable

import magic
import typer

solution_name_placeholder = "solution_name"


def get_cookiecutter_placeholder(arg) -> str:
    return f"{{{{cookiecutter.{arg}}}}}"


def replace_in_names(root_dir: str, replacements: list[tuple[str, str]]) -> None:
    # we are excluding files and folders starting with "."
    name_predicate: Callable[[str], bool] = lambda x: not x.startswith(".")

    for current_dir, sub_dirs, files in os.walk(root_dir):
        sub_dirs[:] = list(filter(name_predicate, sub_dirs))

        # recursively call for subdirectories
        for sub_dir in sub_dirs:
            for r in replacements:
                new_dir_name = sub_dir.replace(r[0], get_cookiecutter_placeholder(r[1]))
                if new_dir_name != sub_dir:
                    shutil.move(
                        os.path.join(current_dir, sub_dir),
                        os.path.join(current_dir, new_dir_name),
                    )

        # rename files
        for file in list(filter(name_predicate, files)):
            for r in replacements:
                new_file_name = file.replace(r[0], get_cookiecutter_placeholder(r[1]))
                if new_file_name != file:
                    shutil.move(
                        os.path.join(current_dir, file),
                        os.path.join(current_dir, new_file_name),
                    )


def move_all_in_subdir(source_dir: str, dest_dir: str) -> None:
    for entry in os.listdir(source_dir):
        shutil.move(os.path.join(source_dir, entry), dest_dir)


def delete_pattern(pattern: str) -> None:
    paths = glob.glob(pattern, recursive=True)
    for path in paths:
        shutil.rmtree(path, ignore_errors=True)


def clean(root_folder: str) -> None:
    delete_pattern(os.path.join(root_folder, "**", "bin/"))
    delete_pattern(os.path.join(root_folder, "**", "obj/"))
    delete_pattern(os.path.join(root_folder, ".idea/**"))


def get_solution_name(root_folder: str) -> str:
    matches = glob.glob(os.path.join(root_folder, "*.sln"))

    msg_base = "Cannot determine the solution name. {0}"

    if len(matches) > 1:
        raise Exception(msg_base.format("Multiple solution files found."))

    if len(matches) == 0:
        raise Exception(msg_base.format("No solution files found."))

    file_name = os.path.basename(matches[0])
    return file_name[: file_name.rindex(".")]


def is_text_file(path) -> bool:
    return magic.from_file(path, mime=True).startswith("text")


def replace_in_files_content(
    root_dir: str, replacements: list[tuple[str, str]]
) -> None:
    files = list(
        filter(
            lambda x: os.path.isfile(x)
            and not os.path.basename(x).startswith(".")
            and is_text_file(x),
            glob.glob(os.path.join(root_dir, "**"), recursive=True),
        )
    )
    for path in files:
        with open(path, "r+") as f:
            content = f.read()
            f.seek(0)
            f.truncate()
            for r in replacements:
                content = content.replace(r[0], get_cookiecutter_placeholder(r[1]))

            f.write(content)


def generate_json(root_dir: str, replacements: list[tuple[str, str]]) -> None:
    json_path = os.path.join(root_dir, "cookiecutter.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            dict((v, k) for k, v in replacements), f, ensure_ascii=False, indent=4
        )


def main(root_dir: str) -> None:
    solution_name = get_solution_name(root_dir)

    clean(root_dir)

    dest_dir = os.path.join(
        root_dir, f"{get_cookiecutter_placeholder(solution_name_placeholder)}/"
    )

    os.mkdir(dest_dir)
    move_all_in_subdir(root_dir, dest_dir)

    replacements = [
        (solution_name, solution_name_placeholder),
        ("Customer", "sample_entity_name"),
    ]
    replace_in_files_content(dest_dir, replacements)
    replace_in_names(dest_dir, replacements)
    generate_json(root_dir, replacements)


if __name__ == "__main__":
    typer.run(main)
