# VideoBrowser
![Main Page](https://github.com/AnkithAbhayan/AnkithAbhayan.github.io/blob/main/images/screenshot_videobrowser.png "pic")
- A video browser built using python and tkinter.
- Ability to browse videos in a folder and preview them upon hovering the mouse cursor over the thumbnail.
- Ability to preview 1, 2 or even 4 videos at once (with or without audio).
- Stores the previously opened folder path in a file to immediately open it again the next time the program is run.
- Clicking a thumbnail will invoke vlc (if available) to play the video.

## Installation
```
git clone "https://github.com/AnkithAbhayan/VideoBrowser" VideoBrowser
cd VideoBrowser
pip install -r requirements.txt
```
## Execution
```
python main.py [path]
```
Note: path argument is optional.