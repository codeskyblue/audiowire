# coding: utf-8
import os
import pathlib
import socket
import sys

import qrcode
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import locks
import zmq
from zmq.eventloop.future import Context
from logzero import logger


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class AudioParamsHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"encoding": '16bitInt',
                    "channels": 2,
                    "sampleRate": 44100})


class AudioWebSocketHandler(tornado.websocket.WebSocketHandler):
    async def open(self):
        context = Context()
        sock = context.socket(zmq.SUB)
        sock.setsockopt(zmq.CONFLATE, 1)
        sock.connect("tcp://localhost:5555")
        sock.subscribe(b'')

        self.sock = sock
        self._stopped = False
        logger.debug("pipe audio message")
        tornado.ioloop.IOLoop.current().spawn_callback(self.pipe_message)

    async def pipe_message(self):
        while not self._stopped:
            self.write_message(await self.sock.recv(), binary=True)
        logger.debug("pipe message stopped")

    def on_message(self, message):
        logger.debug("receive message: %s", message)

    def on_close(self):
        logger.info("closed")
        self._stopped = True


def make_app(**settings):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    settings["static_path"] = os.path.join(current_dir, "static")
    settings["template_path"] = current_dir

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/audio", AudioParamsHandler),
        (r"/audio/websocket", AudioWebSocketHandler),
    ], **settings)


def current_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def run_web(port: int, **settings):
    app = make_app(**settings)
    url = f"http://{current_ip()}:{port}"
    logger.info("listen on %s", url)
    qr = qrcode.QRCode(border=2)
    qr.add_data(url)
    if os.isatty(sys.stdout.fileno()):
        qr.print_ascii(tty=True)
    app.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    run_web(7000)
