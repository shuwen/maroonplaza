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
        # Set up some values we need. Today's day, the date a week from now,
        # today's weekday, and a list of 
        today = datetime.datetime.today()
        next_week = today + datetime.timedelta(days=7)
        weekday = today.weekday()
        list_of_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days = [(weekday+2)%7, (weekday+3)%7, (weekday+4)%7, (weekday+5)%7, (weekday+6)%7]

        # We also need a structure to sort the events by weekday
        # Let's use a list of seven lists for that
        upcoming = [[] for i in range(7)]

        # Find the events we want. They'll have to have started before next week,
        # but they can't have already ended.
        all_events = events.find({'start': {'$lt': next_week}, 'end': {'$gt': today}})
        
        # Go through our list of events, and put them in the appropriate date boxes.
        for e in all_events:
            for i in range(7):
                the_day = today + datetime.timedelta(days=i)
                if(e["start"].date() <= the_day.date() and e["end"].date() >= the_day.date()):
                    upcoming[i].append(e)

        # Build the kwargs dict
        kwargs = {
            'days': days,
            'list_of_days': list_of_days,
            'upcoming': upcoming,
        }
        
        self.write(self.render_string("templates/header.html"))
        self.write(self.render_string("main.html", **kwargs))
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
        # Get and parse the time fields into proper Python datetimes
        start = self.get_argument('start').strip().split('/')
        end = self.get_argument('end').strip().split('/')
        # Make the dictionary to put into MongoDB
        new_event = {'name': self.get_argument('name'),
                     'start': datetime.datetime(int(start[2]), int(start[0]), int(start[1])),
                     'end': datetime.datetime(int(end[2]), int(end[0]), int(end[1])),
                     'host': self.get_argument('host'),
                     'venue': self.get_argument('venue'),
                     'price': self.get_argument('price'),
                     'desc': self.get_argument('desc'),}
        events.insert(new_event)
    
settings = {
    "debug": True,
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
