# audiowire
Transfer PC Audio(Sound) to Browser. For MAC Only

Python3.6+ required

## Installation
```bash
brew install portaudio

pip3 install audiowire
```

### Install virtual speaker

> The iShowU Audio Capture is not free support M1 now.

Install `iShowU Audio Capture` according to <https://support.shinywhitebox.com/hc/en-us/articles/204161459-Installing-iShowU-Audio-Capture>

Open `System Preferences` - `Sound` - `Output`
Select `iShowU Audio Capture`

Alternative (SoundFlower) (not support M1, tested 2021/07/19)

https://github.com/mattingalls/Soundflower 

## Usage
Open terminal, type the following command.

```bash
audiowire --help # see more usage

audiowire
```

Use your phone the scan the QRCode showing in the terminal.

# Develop
```
git clone https://github.com/codeskyblue/audiowire
pip3 install -e .
```

## Uninstall
- <https://support.shinywhitebox.com/hc/en-us/articles/204161529-Uninstalling-iShowU-Audio-Capture>

# Thanks
- https://people.csail.mit.edu/hubert/pyaudio/
- https://github.com/samirkumardas/pcm-player
- https://github.com/joewalnes/reconnecting-websocket
- 解决iOS Safari不能听声音的问题 https://stackoverflow.com/questions/46363048/onaudioprocess-not-called-on-ios11/46534088#46534088
- iShowU Audio Capture https://support.shinywhitebox.com/hc/en-us/articles/204161459-Installing-iShowU-Audio-Capture
- 播放不锁屏 https://github.com/richtr/NoSleep.js/


## CHANGELOG
- 1.0.0 首个能用的版本
- 1.0.1 修复import error
- 1.1.0 新增播放时不锁屏的功能


# LICENSE
[GPL 2.0](LICENSE)
