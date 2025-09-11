from pathlib import Path
from typing import Generator
import cv2 as cv  # For loading/processing video/images
import numpy as np  # For matrix operations

# We have to do this with a generator due to video size
def iter_frames(v: cv.VideoCapture) -> Generator[cv.Mat, None, None]:
    """
    Read one frame at a time.
    """
    while True:
        ret, frame = v.read()
        if not ret:
            break
        yield frame

def detect_flash(baseline: cv.Mat, frame: cv.Mat, threshold=100) -> bool:
    """
    Returns true if a flash is detected.
    Runs substraction from baseline, blur, gets max luminance, and returns true is value (0 - 255) is above threshold.
    100 seems to work very well
    """
    # convert both frames to BW
    baseline = cv.cvtColor(baseline, cv.COLOR_BGR2GRAY)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Calculate and blur diff
    diff = cv.absdiff(frame, baseline)
    diff = cv.blur(diff, (5, 5))

    # Show for now to analyze
    # cv.imshow("diff", diff)
    # cv.waitKey(0)

    return np.amax(diff) > threshold


def process_video(flash_path: Path, clip_path: Path):
    video = cv.VideoCapture(flash_path.absolute())

    assert(video.isOpened())
    
    ret, frame1 = video.read()
    assert(ret)

    flash_events = []
    flashing = False

    for i, frame in enumerate(iter_frames(video)):
        if i % 1000 == 0:
            print(f"Processing frame {i + 1}")
        event = detect_flash(frame1, frame)

        # If flash just started
        if event and not flashing:
            flash_events.append({"index": i + 1, "length": 0})
            flashing = True
        elif not event and flashing:
            flashing = False
        
        if flashing:
            flash_events[-1]["length"] += 1

    clip_flashes(flash_events, clip_path)

def clip_flashes(flash_events: list[dict], path: Path):
    video = cv.VideoCapture(path.absolute())

    clip_length = 32
    events_to_clip = [0, 19, 49, 66, 132, 199, 266, 399]

    for i in events_to_clip:
        print(f"Clipping event {i}")
        event = flash_events[i]
        frames = []
        video.set(cv.CAP_PROP_POS_FRAMES, int(event["index"] - clip_length / 2) - 1)
        for j in range(clip_length):
            ret, frame = video.read()
            assert(ret)  # If this fails, we're probably at the end of the video. Don't clip last flash
            frames.append(frame)
        
        out = path.parent / path.stem / f"{i}.tiff"

        if not out.parent.exists():
            out.parent.mkdir()
        cv.imwritemulti(str(out.absolute()), frames)

if __name__ == "__main__":
    video_path = Path("input.mp4")
    # Convert with
    # winget install ffmpeg (only once ofc)
    # ffmpeg -i input.mp4 -vf "scale=320:-1" input_lr.mp4
    video_path_low_res = Path("input_lr.mp4")
    output = process_video(video_path_low_res, video_path)