import tornado.ioloop
import tornado.web
import tornado.template
import cgi
import urllib
import datetime
import os
import pymongo
import ldap

from pymongo import Connection

# intialize ldap
ldap_con = ldap.initialize('ldap://ldap.uchicago.edu')
ldap_con.start_tls_s()

# initialize database
mongo_con = Connection()
db = mongo_con.test
events = db.events


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.render_string("templates/header.html"))
        for event in events.find():
            self.write(event["name"])
        # self.write(self.render_string("main.html"))
        self.write(self.render_string("templates/footer.html"))
        

class AboutHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.render_string("templates/header.html"))
        self.write(self.render_string("about.html"))
        self.write(self.render_string("templates/footer.html"))

class SubmitHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.render_string("templates/header.html"))
        self.write(self.render_string("submit.html"))
        self.write(self.render_string("templates/footer.html"))
    
    def post(self):
        new_event = {'name': self.get_argument('name'),
                     'start': self.get_argument('start'),
                     'end': self.get_argument('end'),
                     'host': self.get_argument('host'),
                     'venue': self.get_argument('venue'),
                     'price': self.get_argument('price'),
                     'desc': self.get_argument('desc'),}
        events.insert(new_event)
    
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}

application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/about/', AboutHandler),
    (r'/submit/', SubmitHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
