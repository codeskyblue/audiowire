# coding: utf-8
#
import argparse
import threading

import pyaudio

import zmq
from logzero import logger

CHUNK = 1024


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
    return_info = None
    for idx in range(p.get_device_count()):
        info = p.get_device_info_by_index(idx)
        channels = info["maxInputChannels"]
        if channels == 0:
            continue
        return_info = info
    return return_info


def main():
    p = pyaudio.PyAudio()
    info = get_input_device(p)
    channels = info["maxInputChannels"]
    logger.info("Device: %s, channels: %d", info['name'], channels)
    stream = p.open(
        input_device_index=info['index'],
        format=pyaudio.paInt16,
        channels=channels,
        rate=44100,
        input=True,
        frames_per_buffer=CHUNK)

    sock = create_publisher()
    while True:
        chunk = stream.read(CHUNK)
        sock.send(chunk)
        print(".", end="")


if __name__ == "__main__":
    main()
