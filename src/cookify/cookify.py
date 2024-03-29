import glob
import json
import os
import shutil
from collections import defaultdict
from itertools import groupby

import magic

solution_name_placeholder = "solution_name"


def get_cookiecutter_placeholder(arg) -> str:
    return f"{{{{cookiecutter.{arg}}}}}"


def rename_in_paths(
    root_dir: str, paths: list[str], replacements: list[tuple[str, str]]
):
    for path in paths:
        base_name = os.path.basename(path)
        for r in replacements:
            new_base_name = base_name.replace(r[0], get_cookiecutter_placeholder(r[1]))
            if new_base_name != base_name:
                new_path = path[: -len(base_name)] + new_base_name
                os.rename(
                    os.path.join(root_dir, path), os.path.join(root_dir, new_path)
                )


def replace_in_names(root_dir: str, replacements: list[tuple[str, str]]) -> None:
    files_and_folders = glob.glob(os.path.join(root_dir, "**"), recursive=True)
    files = list(
        filter(
            lambda f: bool(f),
            map(
                lambda f: f.replace(root_dir, ""),
                filter(lambda f: os.path.isfile(f), files_and_folders),
            ),
        )
    )
    dirs = list(
        filter(
            lambda f: bool(f),
            map(
                lambda f: f.replace(root_dir, ""),
                filter(lambda f: os.path.isdir(f), files_and_folders),
            ),
        )
    )

    files_levels_map: dict[int, list[str]] = defaultdict(list)
    for count, items in groupby(files, lambda s: s.count("/")):
        files_levels_map[count].extend(items)

    dir_levels_map: dict[int, list[str]] = defaultdict(list)
    for count, items in groupby(dirs, lambda s: s.count("/")):
        dir_levels_map[count].extend(items)

    max_level = max([max(files_levels_map.keys()), max(dir_levels_map.keys())])
    for level in reversed(range(max_level + 1)):
        rename_in_paths(root_dir, files_levels_map[level], replacements)
        rename_in_paths(root_dir, dir_levels_map[level], replacements)


def move_all_in_subdir(source_dir: str, dest_dir: str) -> None:
    for entry in filter(lambda x: x != ".git", os.listdir(source_dir)):
        shutil.move(os.path.join(source_dir, entry), dest_dir)


def delete_pattern(pattern: str) -> None:
    paths = glob.glob(pattern, recursive=True)
    for path in paths:
        shutil.rmtree(path, ignore_errors=True)


def clean(root_folder: str) -> None:
    delete_pattern(os.path.join(root_folder, "**", "bin/"))
    delete_pattern(os.path.join(root_folder, "**", "obj/"))
    delete_pattern(os.path.join(root_folder, ".idea/**"))


def is_text_file(path) -> bool:
    return magic.from_file(path, mime=True).startswith("text")


def replace_in_files_content(
    root_dir: str, replacements: list[tuple[str, str]]
) -> None:
    files = list(
        filter(
            lambda x: os.path.isfile(x) and is_text_file(x),
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
        json.dump({v: k for k, v in replacements}, f, ensure_ascii=False, indent=4)


def run(
    root_dir: str,
    placeholder_1_name: str,
    placeholder_1_value: str,
    placeholder_2_name: str,
    placeholder_2_value: str,
) -> None:
    # first of all, clean
    clean(root_dir)

    # move everything one level down in cookiecutter subdirectory
    dest_dir = os.path.join(
        root_dir, f"{get_cookiecutter_placeholder(solution_name_placeholder)}/"
    )
    os.mkdir(dest_dir)
    move_all_in_subdir(root_dir, dest_dir)

    # replace cookiecutter placeholders in file contents and file names
    replacements = [
        (placeholder_1_value, placeholder_1_name),
        (placeholder_2_value, placeholder_2_name),
    ]
    replace_in_files_content(dest_dir, replacements)
    replace_in_names(dest_dir, replacements)

    # generate cookiecutter template manifest file
    generate_json(root_dir, replacements)
