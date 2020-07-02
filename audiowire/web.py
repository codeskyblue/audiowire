# coding: utf-8
import os
import pathlib
import socket
import sys

import qrcode
import tornado.ioloop
import tornado.web
import tornado.websocket
import zmq
from logzero import logger
from tornado import locks
from zmq.eventloop.future import Context
import pkg_resources

from . import settings


__version__ = pkg_resources.get_distribution("audiowire").version

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", version=__version__)


class AudioParamsHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(settings.AUDIO)


class AudioWebSocketHandler(tornado.websocket.WebSocketHandler):
    async def open(self):
        context = Context()
        sock = context.socket(zmq.SUB)
        sock.setsockopt(zmq.CONFLATE, 1)
        sock.connect("tcp://localhost:{}".format(settings.ZMQ_PORT))
        sock.subscribe(b'')

        self.sock = sock
        self._stopped = False
        logger.debug("client connected: %s", self.request.remote_ip)
        tornado.ioloop.IOLoop.current().spawn_callback(self.pipe_message)

    async def pipe_message(self):
        while not self._stopped:
            try:
                await self.write_message(await self.sock.recv(), binary=True)
            except tornado.websocket.WebSocketClosedError:
                break
        self.sock.close()
        logger.debug("pipe message stopped")

    def on_message(self, message):
        logger.debug("receive message: %s", message)

    def on_close(self):
        logger.info("client disconnected: %s", self.request.remote_ip)
        self._stopped = True


class WeUI(tornado.web.RequestHandler):
    def get(self):
        self.render("weui.html")


def make_app(**settings):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    settings["static_path"] = os.path.join(current_dir, "static")
    settings["template_path"] = current_dir

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/audio", AudioParamsHandler),
        (r"/audio/websocket", AudioWebSocketHandler),
        (r"/weui", WeUI),
    ], **settings)


def current_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        return ip
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def run_web(port: int, **settings):
    app = make_app(**settings)
    url = f"http://{current_ip()}:{port}"
    logger.info("listen on %s", url)
    qr = qrcode.QRCode(border=2)
    qr.add_data(url)
    if os.isatty(sys.stdout.fileno()):
        qr.print_ascii(tty=True)
    app.listen(port)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()


if __name__ == "__main__":
    run_web(7000)
