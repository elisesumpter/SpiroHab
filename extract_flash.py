from pathlib import Path
from process_video import clip_event
import cv2

frames = [
    # YOUR FRAMES GO HERE
    0,
    1,
    2
]
for frame in frames:
    clip_event(cv2.VideoCapture("./PATH_GOES_HERE"), {"index": frame}, Path(f"./{frame}.tiff"))
