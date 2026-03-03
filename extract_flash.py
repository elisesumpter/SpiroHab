from pathlib import Path
from process_video import clip_event
import cv2

event = {
    "index": 0  # FRAME NUMBER GOES HERE
}

clip_event(cv2.VideoCapture("./PATH_GOES_HERE"), event, Path("./out.tiff"))
