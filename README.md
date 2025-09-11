# SpiroHab

## Setup

```bash
python -m pip install -r requirements.txt
winget install ffmpeg
```
(use package manager of choice)

Adjust these two variables to change the length of clips created and the number of the events to clip. The clip length is written in frames. The stimulus will always happen in the middle of the clip, no matter the clip length. It is recommended to use an even number of frames.

```python
# process_video.py, line 69-70
clip_length = 32
events_to_clip = [0, 19, 49, 66, 132, 199, 266, 399]
```
For example, this will select events (stimuli) 1, 20, 50, 67, 133, 200, 267, and 400. It will produce a tiff file with 32 frames, and the stimulus is expected to occur on or around the 16th frame.

Move any videos you want processed into the current directory (can be in subdirectories) then run

```bash
python process_dir.py
```
