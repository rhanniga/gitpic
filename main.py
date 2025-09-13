import os
import subprocess as sp
import datetime

from PIL import Image

REPO_NAME = "dummy"
INPUT_IMAGE_PATH = "whatever.png"

IMAGE_WIDTH = 51
IMAGE_HEIGHT = 7


HUE_COMMIT_MAPPING = [
    10,
    20,
    30,
    40,
]



def convert_image_to_commits():
    img = Image.open(INPUT_IMAGE_PATH)

    grayscale_img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT)).quantize(len(HUE_COMMIT_MAPPING))

    grayscale_img.save("output_grayscale.png")

    data = list(grayscale_img.getdata())


    first_sunday = datetime.date(datetime.datetime.now().year - 1, 1, 7)
    last_saturday = datetime.date(datetime.datetime.now().year - 1, 12, 28)

    current_date = first_sunday
    width_index = 0
    height_index = 0
    while current_date <= last_saturday:
        if current_date.weekday() == 6:
            height_index = 0
            if current_date != first_sunday:
                width_index += 1
                if width_index >= IMAGE_WIDTH:
                    break
        num_commits = HUE_COMMIT_MAPPING[data[height_index * IMAGE_WIDTH + width_index]]
        for _ in range(num_commits):
            ret = sp.run(["git", "commit", "--quiet", "--date", f"{current_date} 12:00:00", "--allow-empty", "-m", f"update README"], cwd=REPO_NAME)
            assert ret.returncode == 0, "Failed to create commit"
        height_index += 1
        current_date += datetime.timedelta(days=1)



def clear_commit_history(repo_path_relative: str):
    # this is ugly, but perhaps only temporary solution
    ret = sp.run(["git", "checkout", "--orphan", "tmp_branch"], cwd=repo_path_relative)
    assert ret.returncode == 0, f"Failed to create orphan branch: {ret.stderr}"
    ret = sp.run(["git", "add", "-A"], cwd=repo_path_relative)
    assert ret.returncode == 0, f"Failed to add files: {ret.stderr}"
    ret = sp.run(["git", "commit", "-am", "update README"], cwd=repo_path_relative)
    assert ret.returncode == 0, f"Failed to commit changes: {ret.stderr}"
    ret = sp.run(["git", "branch", "-D", "main"], cwd=repo_path_relative)
    assert ret.returncode == 0, f"Failed to delete master branch: {ret.stderr}"
    ret = sp.run(["git", "branch", "-m", "main"], cwd=repo_path_relative)
    assert ret.returncode == 0, f"Failed to rename branch to master: {ret.stderr}"
    ret = sp.run(["git", "push", "-f", "origin", "main"], cwd=repo_path_relative)
    assert ret.returncode == 0, f"Failed to push changes to remote: {ret.stderr}"

def initialize_dummy_repo(repo_path_relative: str):
    ret = sp.run(["mkdir", repo_path_relative])
    assert ret.returncode == 0, "Failed to create dummy directory"
    ret = sp.run(["git", "init"], cwd=repo_path_relative)
    assert ret.returncode == 0, "Failed to initialize git repository"

def setup_repo(repo_path_relative: str = REPO_NAME):
    if os.path.exists(repo_path_relative):
        clear_commit_history(repo_path_relative)
    else:
        initialize_dummy_repo(repo_path_relative)

def main():
    setup_repo()
    convert_image_to_commits()


if __name__ == "__main__":
    main()
