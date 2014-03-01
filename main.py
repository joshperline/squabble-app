import os
import webapp2
import cgi
import re
import jinja2
import time

#sends input to certain directory or site
#unless post is there, its a get method (post doesnt put the query in the url)
#post = uploading/updating, no max length
#get = recieving stuff, dont change server

"""TODO: Profiles later."""

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

#Good to inherit for templates
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#"Row" in database table
class Argument(db.Model):
	name1 = db.StringProperty(required = True)
    arg1 = db.StringProperty(required = True)

    name2 = db.StringProperty(required = True)
    arg2 = db.StringProperty(required = True)

    score = db.IntegerProperty()
    rating = db.IntegerProperty()
    #make hotness algorithm = db.integer

    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        self.response.write('Big Things are coming. Check this out. ')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newArgument', NewArgHandler),
    ('/play/([0-9]+)', NewArgHandler)
], debug=True)
