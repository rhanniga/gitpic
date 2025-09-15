import os
import shlex
import subprocess as sp
import datetime
import argparse

from letters import GLYPH_PIXEL_MAP

REPO_NAME = "dummy"
REPO_URL = "git@github.com:rhanniga/dummy.git"


HUE_COMMIT_MAPPING = [
    20,  # Commits for an empty pixel
    100  # Commits for a filled pixel
]


def convert_text_to_commits(text: str, year: int):
    # Add 1 pixel of padding above and below the text
    pixel_matrix = [[0] * 51 for _ in range(7)]

    # Generate the pixel matrix for the text
    text_pixels = []
    current_width = 0
    for char in text.upper():
        if char in GLYPH_PIXEL_MAP:
            glyph = GLYPH_PIXEL_MAP[char]
            glyph_width = len(glyph[0])
            if current_width + glyph_width > 51:
                raise ValueError("Input text is too long to fit in the commit history")
            for r in range(5):
                for c in range(glyph_width):
                    pixel_matrix[r + 1][current_width + c] = glyph[r][c]
            current_width += glyph_width + 1  # Add 1 pixel spacing between characters
        else:
            # Handle unknown characters (add a space)
            current_width += 4 # 3 for the space + 1 for spacing

    # Check if the text fits
    if current_width > 51:
        raise ValueError("Input text is too long to fit in the commit history")


    first_sunday = datetime.date(year, 1, 1)
    while first_sunday.weekday() != 6:
        first_sunday += datetime.timedelta(days=1)

    last_saturday = datetime.date(year, 12, 31)
    while last_saturday.weekday() != 5:
        last_saturday -= datetime.timedelta(days=1)

    current_date = first_sunday
    width_index = 0
    height_index = 0
    while current_date <= last_saturday:
        if current_date.weekday() == 6:
            height_index = 0
            if current_date != first_sunday:
                width_index += 1
                if width_index >= 51:
                    break
        if width_index < 51 and height_index < 7:
            pixel = pixel_matrix[height_index][width_index]
            num_commits = HUE_COMMIT_MAPPING[pixel]
            for _ in range(num_commits):
                ret = sp.run(["git", "commit", "--quiet", "--date", f"{current_date} 12:00:00", "--allow-empty", "-m", f"update README"], cwd=REPO_NAME)
                assert ret.returncode == 0, "Failed to create commit"
        height_index += 1
        current_date += datetime.timedelta(days=1)

def run_command(command: str, working_directory: str):
    command_list = shlex.split(command)
    ret = sp.run(command_list, cwd=working_directory, capture_output=True)
    if ret.returncode != 0:
        raise RuntimeError(f"Command '{command}' failed with error: {ret.stderr.decode()}")

def clear_commit_history(repo_path_relative: str):
    run_command("git checkout --orphan tmp_branch", repo_path_relative)
    run_command("git add -A", repo_path_relative)
    run_command('git commit --allow-empty -m "update README"', repo_path_relative)
    run_command("git branch -D main", repo_path_relative)
    run_command("git branch -m main", repo_path_relative)


def initialize_dummy_repo(repo_path_relative: str):
    run_command("mkdir " + repo_path_relative, '.')
    run_command("git init", repo_path_relative)
    run_command("git remote add origin " + REPO_URL, repo_path_relative)


def setup_repo(repo_path_relative: str = REPO_NAME):
    if os.path.exists(repo_path_relative):
        clear_commit_history(repo_path_relative)
    else:
        initialize_dummy_repo(repo_path_relative)

def main():
    parser = argparse.ArgumentParser(description="Generate a git commit history that spells out a given text.")
    parser.add_argument("year", type=int, help="The year to generate the commit history in.")
    parser.add_argument("text", type=str, help="The text to spell out in the commit history.")
    args = parser.parse_args()

    setup_repo()
    convert_text_to_commits(args.text, args.year)


if __name__ == "__main__":
    main()
