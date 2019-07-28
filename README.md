# audiowire
Transfer PC Audio(Sound) to Browser. For MAC Only

Python3 required

## Installation
```
brew install portaudio

git clone https://github.com/codeskyblue/audiowire
pip3 install -r requirements.txt
```

Install `iShowU Audio Capture` according to <https://support.shinywhitebox.com/hc/en-us/articles/204161459-Installing-iShowU-Audio-Capture>

Open `System Preferences` - `Sound` - `Output`
Select `iShowU Audio Capture`

## Usage
Open terminal, type the following command.

```
python3 main.py
```

Use your phone the scan the QRCode showing in the terminal.


## Uninstall
- <https://support.shinywhitebox.com/hc/en-us/articles/204161529-Uninstalling-iShowU-Audio-Capture>

# Thanks
- https://people.csail.mit.edu/hubert/pyaudio/
- http://www.tornadoweb.org
- https://github.com/samirkumardas/pcm-player
- 解决iOS Safari不能听声音的问题 https://stackoverflow.com/questions/46363048/onaudioprocess-not-called-on-ios11/46534088#46534088
- iShowU Audio Capture https://support.shinywhitebox.com/hc/en-us/articles/204161459-Installing-iShowU-Audio-Capture

# LICENSE
[GPL 2.0](LICENSE)
