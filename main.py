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


def create_publisher(port: int = 5555):
    context = zmq.Context()
    sock = context.socket(zmq.PUB)
    sock.bind("tcp://*:"+str(port))
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
        if info['name'] == name:
            device_info = info
            break
        device_info = info

    if not device_info:
        sys.exit("Missing iShowU Audio Capture")
    return device_info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true",
                        help="enable debug mode")
    parser.add_argument("--zmq-port", type=int,
                        default=5566, help="zmq listen port")
    parser.add_argument(
        "--device-name", default="iShowU Audio Capture", help="audio output device name")
    args = parser.parse_args()

    p = pyaudio.PyAudio()
    info = get_input_device(p, args.device_name)
    audio_settings = settings.AUDIO
    audio_settings["channels"] = channels = info["maxInputChannels"]
    audio_settings["sampleRate"] = sample_rate = 44100
    audio_settings["name"] = info["name"]
    logger.info("Device: %s, channels: %d", info['name'], channels)

    stream = p.open(
        input_device_index=info['index'],
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=CHUNK)

    settings.ZMQ_PORT = args.zmq_port
    sock = create_publisher(settings.ZMQ_PORT)

    def pipe_pcm_stream(stream, sock):
        while True:
            chunk = stream.read(CHUNK)
            sock.send(chunk)

    threading.Thread(
        name="pcmstream", daemon=True,
        target=pipe_pcm_stream, args=(stream, sock)).start()

    import pprint
    pprint.pprint(settings.AUDIO)
    web.run_web(7000, debug=args.debug)


if __name__ == "__main__":
    main()
