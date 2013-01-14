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
from datetime import date

# intialize ldap
l = ldap.initialize('ldap://ldap.uchicago.edu:389')

# l.start_tls_s()

# initialize database
mongo = Connection()
db = mongo.test
events = db.events

# Functions that all handlers have in common
class BaseHandler(tornado.web.RequestHandler):
    # Simple check if user is logged in
    def get_current_user(self):
        return self.get_secure_cookie("user")


class MainHandler(BaseHandler):
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
        all_events = events.find({'start': {'$lte': next_week}, 'end': {'$gt': today - datetime.timedelta(days=1)}})
        
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
        

class AboutHandler(BaseHandler):
    def get(self):
        self.write(self.render_string("templates/header.html"))
        self.write(self.render_string("about.html"))
        self.write(self.render_string("templates/footer.html"))


class AuthHandler(BaseHandler):
    def get(self):
        self.write(self.render_string("templates/header.html"))
        self.write(self.render_string("login.html"))
        self.write(self.render_string("templates/footer.html"))

    # Authenticate through UChicago's LDAP server
    def post(self):
        who = "uid="+self.get_argument("name")+",ou=people,dc=uchicago,dc=edu"
        cred = self.get_argument('pw')
        try:
            l.simple_bind(who, cred)
            self.set_secure_cookie("user", "t")
            self.write("You are authenticated!")
            self.redirect("/")
        except ldap.INVALID_CREDENTIALS:
            self.write("Incorrect username/password combo.")
            self.redirect("/")
        except ldap.LDAPError, error_message:
            self.write("It didn't work")
            print "Couldn't connect. %s " % error_message


class LogOut(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")


class SubmitHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write(self.render_string("templates/header.html"))
        self.write(self.render_string("submit.html"))
        self.write(self.render_string("templates/footer.html"))        

    @tornado.web.authenticated
    def post(self):
        # Get and parse the time fields into proper Python datetimes
        start = self.get_argument('start').strip().split('/')
        end = self.get_argument('end').strip().split('/')
        
        # Convert 12-hour time to 24-hour time
        start_hour = int(self.get_argument('start_hour'))
        if(self.get_argument('start_am_or_pm')=="PM" and start_hour != 12):
            start_hour += 12
        if(self.get_argument('start_am_or_pm')=="AM" and start_hour == 12):
            start_hour = 0
        end_hour = int(self.get_argument('end_hour'))
        if(self.get_argument('end_am_or_pm')=="PM" and end_hour != 12):
            end_hour += 12
        if(self.get_argument('end_am_or_pm')=="AM" and end_hour == 12):
            end_hour = 0

        # Make the dictionary to put into MongoDB
        new_event = {'name': self.get_argument('name'),
                     'start': datetime.datetime(int(start[2]), int(start[0]), int(start[1]),
                                                start_hour, int(self.get_argument('start_minute'))),
                     'end': datetime.datetime(int(end[2]), int(end[0]), int(end[1]),
                                              end_hour, int(self.get_argument('end_minute'))),
                     'host': self.get_argument('host',default=None),
                     'venue': self.get_argument('venue',default=None),
                     'price': self.get_argument('price',default=None),
                     'desc': self.get_argument('desc',default=None),}
        events.insert(new_event)
        self.redirect("/")
    



settings = {
    "debug": True,
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "login_url": "/login",
    "cookie_secret": "mI0EULgGswEEALD61XNT278e3j1iXVxDgyCsOAVZDnLSq97sWOSBFPEoXTUrr2voOCvR9QE427HArm81KXM9rehEl+76kaEkI0X1qRFbI1SapM8tntcqlEBkRZSc2yD0oi/+xkTOYcxYMSe9zgeQ6H3PKVsCbBcU1q+F/eAVi0UgohL+02KqPgz/ABEBAAG0AIicBBABAgAGBQJQuAazAAoJEMQBS0lsBX+DrEgD/11DH7gKd8Yn/qesKTxi8r3K86LPOaMAGFTdglyN5w/D4QY1cICanlyeyQzIi/w4LNux4JlabR/q0LmWpXKiekZPr9zk839Mtp5qHKrRtmNOlk6GkyiToWb0gG1329AIVzKA0VGl1PkIu7N1wrLBY9kxaNCtGvxdlNyTuOYeETnU=pH6+",
    }

application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/about/', AboutHandler),
    (r'/about', AboutHandler),
    (r'/submit/', SubmitHandler),
    (r'/submit', SubmitHandler),
    (r'/login/', AuthHandler),
    (r'/login', AuthHandler),
    (r'/logout/', LogOut),
    (r'/logout', LogOut)
], **settings)

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
