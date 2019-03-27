#!/usr/bin/env python3
# Very simple web vision script, to service vxg media plugin for vision rtsp output

import tornado
import tornado.ioloop
import tornado.web
import os
import sys
import socket
import configparser as ConfigParser

# Define paths
baseDir = "/srv/maverick/data/analysis/"
inbox = os.path.join(baseDir, "inbox/")
anonybox = os.path.join(baseDir, "anonybox/")

class Webload(tornado.web.RequestHandler):
    def get(self):
        self.config = self.config_parse("/srv/maverick/config/vision/maverick-visiond.conf")
        if self.config['output'] == "rtsp":
            if 'port' in self.config:
                _port = self.config['port']
            else:
                _port = 5600
            if 'webvision_hostname' in self.config:
                _fqdn = self.config['webvision_hostname']
            else:
                _fqdn = socket.getfqdn()
            self.render("webvision.html", port=_port, fqdn=_fqdn)
        else:
            self.render("webvision_disabled.html")

    def config_parse(self, path):
        Config = ConfigParser.SafeConfigParser()
        options = {}
        try:
            Config.read(path)
            for item in Config.options("visiond"):
                options[item] = Config.get("visiond", item)
        except:
            sys.exit(1)
        return options


application = tornado.web.Application([
        (r"/", Webload),
        ], debug=True)


if __name__ == "__main__":
    application.listen(6793)
    tornado.ioloop.IOLoop.instance().start()