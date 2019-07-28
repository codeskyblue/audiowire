# coding: utf-8
#
import argparse
import sys
import threading

import pyaudio
import zmq
from logzero import logger

import settings
import web

CHUNK = 4096


def create_publisher():
    context = zmq.Context()
    sock = context.socket(zmq.PUB)
    sock.bind("tcp://*:5555")
    return sock


def get_input_device(p: pyaudio.PyAudio):
    """
    Returns Example:
        {'index': 1, 'structVersion': 2, 'name': 'MacBook Pro麦克风', 
        'hostApi': 0, 'maxInputChannels': 1, 'maxOutputChannels': 0, 
        'defaultLowInputLatency': 0.04852607709750567, 
        'defaultLowOutputLatency': 0.01, 
        'defaultHighInputLatency': 0.05868480725623583, 
        'defaultHighOutputLatency': 0.1, 
        'defaultSampleRate': 44100.0}
    """
    device_info = None
    for idx in range(p.get_device_count()):
        info = p.get_device_info_by_index(idx)
        channels = info["maxInputChannels"]
        if channels == 0:
            continue
        if info['name'] == 'iShowU Audio Capture':
            device_info = info
            break
    if not device_info:
        sys.exit("Missing iShowU Audio Capture")
    return device_info


def main():
    p = pyaudio.PyAudio()
    info = get_input_device(p)
    audio_settings = settings.AUDIO
    audio_settings["channels"] = channels = info["maxInputChannels"]
    audio_settings["sampleRate"] = sample_rate = 44100
    logger.info("Device: %s, channels: %d", info['name'], channels)

    stream = p.open(
        input_device_index=info['index'],
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=CHUNK)

    sock = create_publisher()

    def pipe_pcm_stream(stream, sock):
        while True:
            chunk = stream.read(CHUNK)
            sock.send(chunk)

    th = threading.Thread(
        name="pcmstream", target=pipe_pcm_stream, args=(stream, sock))
    th.daemon = True
    th.start()

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true",
                        help="enable debug mode")
    args = parser.parse_args()

    web.run_web(7000, debug=args.debug)


if __name__ == "__main__":
    main()
