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

def detect_flash(baseline: cv.Mat, frame: cv.Mat, threshold=60) -> bool: #normally 60
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
    diff = cv.blur(diff, (8, 8))

    # # Show for now to analyze
    # if np.amax(diff) > threshold:
    #     cv.imshow("diff", diff)
    #     cv.waitKey(0)

    return np.amax(diff) > threshold


def process_video(flash_path: Path, clip_path: Path):
    video = cv.VideoCapture(flash_path.absolute())

    assert(video.isOpened())
    
    ret, baseline = video.read()
    assert(ret)

    flash_events = []
    flashing = False

    for i, frame in enumerate(iter_frames(video)):
        if i % 1000 == 0:
            print(f"Processing frame {i + 1}")
        event = detect_flash(baseline, frame)

        # If flash just started
        if event and not flashing:
            flash_events.append({"index": i + 1, "length": 0})
            flashing = True
        elif not event and flashing:
            flashing = False
        
        if flashing:
            flash_events[-1]["length"] += 1
        else:
            # if last flash event was exactly 10 frames ago, get a new baseline
            if len(flash_events) > 0 and (i + 1) - flash_events[-1]["index"] == 20:
                baseline = np.mean([baseline, frame], axis=0)
                baseline = frame

    print(f"Found {len(flash_events)} flashes")
    clip_flashes(flash_events, clip_path)

def clip_flashes(flash_events: list[dict], path: Path):
    video = cv.VideoCapture(path.absolute())

    clip_length = 32
    events_to_clip = [0, 9, 19, 29, 49, 74, 99, 149, 199, 249, 299, 349, 399, 400]       # 0, 4, 9, 19, 29, 49, 74, 99, 149, 199, 149, 299, 249, 349, 398,

# 0.333 : 0, 4, 9, 19, 29, 49, 74, 99, 149, 199, 249, 299, 349, 399, 400, 404, 409
# 0.111 Hz : 0, 4, 9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 109, 119, 129, 133, 134, 138, 143
# 1 Hz : 0, 9, 19, 29, 49, 74, 99, 149, 199, 249, 299, 349, 399, 499, 599, 699, 799, 899, 999, 1099, 1199, 1200, 1209, 1219, 1229
# 0.033 Hz : 0, 4, 9, 14, 19, 24, 29, 34, 39, 40, 44, 49
# FatigueCheck : 0, 9, 19, 29, 49, 74, 99, 149, 199, 249, 299, 349, 399, 400
# VoltageTest : 0, 4, 9


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
    import ffmpeg
    video_path = Path("input.mp4")
    video_path_low_res = Path("input_lr.mp4")
    # Convert with
    # winget install ffmpeg (only once ofc)
    # ffmpeg -i input.mp4 -vf "scale=320:-1 fps=fps=source_fps" input_lr.mp4
    if not video_path_low_res.exists():
        ffmpeg.input(str(video_path.absolute())).filter('scale', 320, -1).output(str(video_path_low_res.absolute()), vsync="cfr").run()
    output = process_video(video_path_low_res, video_path)
