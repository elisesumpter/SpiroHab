from pathlib import Path

import ffmpeg
from process_video import process_video

def process_dir(dir: Path):
    files: list[Path] = []

    for subdir, _, _ in dir.walk():
        for file in subdir.iterdir():
            if file.name.endswith(".mp4") and not file.name.endswith("lr.mp4"):
                files.append(file)

    print(files)
    
    i = "a"
    while i.lower() not in "yn":
        i = input(f"Are you sure you want to run the script on these files: {files}? [y/n] ")
    
    if i.lower() != "y":
        exit(1)
    
    for file in files:
        lr_file = file.parent.absolute() / f"{file.stem}_lr.mp4"
        if not lr_file.exists():
            ffmpeg.input(str(file.absolute())).filter('scale', 320, -1).output(str(lr_file.absolute())).run()
        process_video(lr_file, file)

if __name__ == "__main__":
    process_dir(Path(__file__).parent)
        