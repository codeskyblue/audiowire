# coding: utf-8
#
import argparse
import sys
import threading
import time

import pyaudio
import zmq
from logzero import logger

from . import settings
from . import web

CHUNK = 1024


def create_publisher(port: int = 5555):
    context = zmq.Context()
    sock = context.socket(zmq.PUB)
    sock.bind("tcp://*:" + str(port))
    return sock


def get_input_device(p: pyaudio.PyAudio, name: str):
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
        logger.debug("device name: %s", info['name'])
        if info['name'] == name:
            device_info = info

    if not device_info:
        sys.exit("Missing iShowU Audio Capture")
    return device_info


def pipe_pcm_stream(p: pyaudio.PyAudio, input_device_index: int, channels: int,
                    sample_rate: int, sock):
    while True:
        stream = p.open(input_device_index=input_device_index,
                        format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=CHUNK)

        try:
            while True:
                chunk = stream.read(CHUNK)
                sock.send(chunk)
        except Exception as e:
            logger.warning("pyaudio error: %s", e)
            stream.close()
            time.sleep(1.0)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d",
                        "--debug",
                        action="store_true",
                        help="enable debug mode")
    parser.add_argument("--zmq-port",
                        type=int,
                        default=5566,
                        help="zmq listen port")
    parser.add_argument("--device-name",
                        default="iShowU Audio Capture",
                        help="audio output device name")
    parser.add_argument("-p",
                        "--port",
                        type=int,
                        default=7000,
                        help="listen port")
    parser.add_argument("-r",
                        "--rate",
                        type=int,
                        default=44100,
                        help="sample rate")
    args = parser.parse_args()

    p = pyaudio.PyAudio()
    info = get_input_device(p, args.device_name)
    audio_settings = settings.AUDIO
    audio_settings["channels"] = channels = info["maxInputChannels"]
    audio_settings["sampleRate"] = sample_rate = args.rate
    audio_settings["name"] = info["name"]
    logger.info("Device: %s, channels: %d", info['name'], channels)

    settings.ZMQ_PORT = args.zmq_port
    sock = create_publisher(settings.ZMQ_PORT)

    threading.Thread(name="pcmstream",
                     daemon=True,
                     target=pipe_pcm_stream,
                     args=(p, info['index'], channels, sample_rate,
                           sock)).start()

    import pprint
    pprint.pprint(settings.AUDIO)
    web.run_web(args.port, debug=args.debug)


if __name__ == "__main__":
    main()
