# SpiroHab

## Setup

```bash
python -m pip install -r requirements.txt
winget install ffmpeg
```
(use package manager of choice)

Adjust these two variables to change the length of clips created and the number of the events to clip
```python
# process_video.py, line 69-70
clip_length = 32
events_to_clip = [0, 2, 5, 10, 20, 50, 100, 200]
```

Move any videos you want processed into the current directory (can be in subdirectories) then run

```bash
python process_dir.py
```
