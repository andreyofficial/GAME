#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import venv


GAME_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(GAME_DIR, ".venv")
REQUIREMENTS_FILE = os.path.join(GAME_DIR, "requirements.txt")
GAME_ENTRY = os.path.join(GAME_DIR, "game_main.py")


def get_venv_python_path():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")

    return os.path.join(VENV_DIR, "bin", "python")


def run_command(cmd):
    subprocess.check_call(cmd, cwd=GAME_DIR)


def ensure_venv():
    venv_python = get_venv_python_path()

    if os.path.exists(venv_python):
        return venv_python

    if os.path.isdir(VENV_DIR):
        shutil.rmtree(VENV_DIR)

    builder = venv.EnvBuilder(with_pip=True, clear=True)
    builder.create(VENV_DIR)
    return venv_python


def ensure_dependencies(venv_python):
    dependency_check = [
        venv_python,
        "-c",
        "import pygame; import PIL"
    ]

    result = subprocess.run(
        dependency_check,
        cwd=GAME_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
    )

    if result.returncode == 0:
        return

    run_command([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
    run_command([venv_python, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])


def launch_game(venv_python):
    os.chdir(GAME_DIR)
    os.execv(
        venv_python,
        [venv_python, GAME_ENTRY] + sys.argv[1:]
    )


def main():
    venv_python = ensure_venv()
    ensure_dependencies(venv_python)
    launch_game(venv_python)


if __name__ == "__main__":
    main()
