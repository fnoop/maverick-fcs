#!/usr/bin/env python
# Very simple file upload script, hacked on code taken from https://technobeans.com/2012/09/17/tornado-file-uploads/

import tornado
import tornado.ioloop
import tornado.web
import os, uuid

# Define paths
baseDir = "/srv/maverick/data/analysis/"
inbox = os.path.join(baseDir, "inbox/")
anonybox = os.path.join(baseDir, "anonybox/")

class Userform(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", fname=None, _uploadDir=None)

class Upload(tornado.web.RequestHandler):
    def post(self):
        fileinfo = self.request.files['file'][0]
        #print "fileinfo is", fileinfo
        fname = fileinfo['filename']
        anon = self.get_argument("anon", None, False)
        if anon:
            _uploadDir = anonybox
        else:
            _uploadDir = inbox
        fh = open(os.path.join(_uploadDir, fname), 'w')
        fh.write(fileinfo['body'])
        self.render("index.html", fname=fname, _uploadDir=_uploadDir)

application = tornado.web.Application([
        (r"/", Userform),
        (r"/upload", Upload),
        ], debug=True)


if __name__ == "__main__":
    application.listen(6792)
    tornado.ioloop.IOLoop.instance().start()