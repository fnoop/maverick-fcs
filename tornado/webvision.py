#!/usr/bin/env python
# Very simple web vision script, to service vxg media plugin for vision rtsp output

import tornado
import tornado.ioloop
import tornado.web
import os, sys, ConfigParser, socket

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
        
class Upload(tornado.web.RequestHandler):
    def post(self):
        fileinfo = self.request.files['file'][0]
        filename = fileinfo['filename']
        anon = self.get_argument("anon", None, False)
        if anon:
            _uploadDir = anonybox
        else:
            _uploadDir = inbox

        # Write an entry to the meta db
        description = self.get_argument("description", None, False)
        try:
            conn = sqlite3.connect("/srv/maverick/data/analysis/mavlog-meta.db")
            cursor = conn.cursor()
            # See if entry already exists
            cursor.execute("SELECT id FROM logfiles WHERE filename='"+filename+"'")
            try:
                id_exists = cursor.fetchone()[0]
            except:
                id_exists = None
            if not id_exists:
                cursor.execute('INSERT INTO logfiles (filename,state,description) VALUES (?,?,?)', (filename,"uploaded",description))
            else:
                cursor.execute('UPDATE logfiles SET start=?,state=?,description=? WHERE id=?', (filename,"uploaded",description,id_exists))
            conn.commit()
            conn.close()
        except Exception as e:
            print "Meta entry exception: {}".format(repr(e))

        # Write the upload contents to a new file in inbox/anonybox
        fh = open(os.path.join(_uploadDir, filename), 'w')
        fh.write(fileinfo['body'])
        self.render("index.html", fname=filename, _uploadDir=_uploadDir)

application = tornado.web.Application([
        (r"/", Webload),
        ], debug=True)


if __name__ == "__main__":
    application.listen(6793)
    tornado.ioloop.IOLoop.instance().start()