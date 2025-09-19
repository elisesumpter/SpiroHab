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

def get_relative_maximum_brightness(baseline: cv.Mat, frame: cv.Mat) -> float:
    """
    Get the maximum brightness of frame compared to baseline.
    Returns the brightness (0-255) of the brightest pixel in the blurred absolute difference of the images in black and white.
    """
    # convert both frames to BW
    baseline = cv.cvtColor(baseline, cv.COLOR_BGR2GRAY)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Calculate and blur diff
    diff = cv.absdiff(frame, baseline)
    diff = cv.blur(diff, (8, 8))

    # Uncomment to analyze diff
    # if np.amax(diff) > 60:
    #     cv.imshow("diff", diff)
    #     cv.waitKey(0)

    return np.amax(diff)

def get_flash_events(video: cv.VideoCapture, threshold=60) -> list[dict]:
    """
    Checks each frame of the video for flashes above the threshold, and returns a list of dicts with fields:
    - index: frame on which the flash started
    - length: duration of the flash event  
    """

    # Read the first frame to get a baseline with no flash (hopefully)
    ret, baseline = video.read()
    assert ret, "Unable to read the a frame of the flash video."

    flash_events = []
    flashing = False

    for i, frame in enumerate(iter_frames(video)):
        if i % 1000 == 0:
            print(f"Processing frame {i + 1}")

        flash_value = get_relative_maximum_brightness(baseline, frame)
        event = flash_value > threshold

        # If flash just started
        if event and not flashing:
            flash_events.append({"index": i + 1, "length": 0})
            flashing = True
        elif not event and flashing:
            flashing = False
        
        if flashing:
            flash_events[-1]["length"] += 1
        else:
            # if last flash event was exactly 20 frames ago and there's no flash now, average the old baseline with the current frame
            if len(flash_events) > 0 and (i + 1) - flash_events[-1]["index"] == 20:
                baseline = np.mean([baseline, frame], axis=0)
                baseline = frame

    return flash_events

def clip_flashes(flash_events: list[dict], video: cv.VideoCapture, output_folder: Path):
    """
    For some events in flash_events, creates a clip in .tiff file format of the flash with some frames before and after the event.
    """
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
        
        out = output_folder / f"{i}.tiff"

        if not out.parent.exists():
            out.parent.mkdir()
        cv.imwritemulti(str(out.absolute()), frames)

def process_video(flash_path: Path, clip_path: Path):
    """
    Find flashes and create clips. 
    """
    flash_video = cv.VideoCapture(flash_path.absolute())
    assert(flash_video.isOpened())

    flash_events = get_flash_events(flash_video)
    print(f"Found {len(flash_events)} flashes.")

    if input("Create clips? [y/n]") == "y":
        
        out_folder = clip_path.parent / clip_path.stem
        clip_video = cv.VideoCapture(clip_path.absolute())
        clip_flashes(flash_events, clip_video, out_folder)

if __name__ == "__main__":
    import ffmpeg
    video_path = Path("input.mp4")
    video_path_low_res = Path("input_lr.mp4")

    if not video_path_low_res.exists():
        ffmpeg.input(str(video_path.absolute())).filter('scale', 320, -1).output(str(video_path_low_res.absolute()), vsync="cfr").run()

    output = process_video(video_path_low_res, video_path)
