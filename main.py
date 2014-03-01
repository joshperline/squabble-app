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
    title = db.StringProperty(required = True)

    name1 = db.StringProperty(required = True)
    arg1 = db.TextProperty(required = True)

    name2 = db.StringProperty(required = True)
    arg2 = db.TextProperty(required = True)

    score = db.IntegerProperty()
    rating = db.IntegerProperty()
    #improve to hotness algorithm = db.integer

    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        self.render("index.html")

class NewArgHandler(Handler):
    def get(self):
        self.render("newArgument.html")

    def post(self):
        #TODO: do handling on creating a new argument
        title = self.request.get('title')
        name1 = self.request.get('name1')
        name2 = self.request.get('name2')
        arg1 = self.request.get('arg1')
        arg2 = self.request.get('arg2')
        if (title and name1 and name2 and arg1 and arg2):
            a = Argument(title = title, name1 = name1, name2 = name2, arg1 = arg1,
                          arg2 = arg2, score = 0, rating = 0)
            a.put()
            self.redirect("/thanks")#TODO: thanks.html
        else:
            error = "Please fill in all required information."
            self.render("newArgument.html", title = title, name1 = name1,
                        name2 = name2, arg1 = arg1, arg2 = arg2, error = error)

class ThanksHandler(Handler):
	def get(self):
		self.response.write("Thanks")

class PlayHandler(Handler):
    def get(self, play_id):
        key = db.Key.from_path('Argument', int(play_id))
        arg = db.get(key)
        if not arg:
            self.error(404)
            return
        self.render("play.html", arg = arg)#TODO: Make sure elements are in dot notation

class StartPlayHandler(Handler):
    def get(self):
        #TODO: Get best question/random, existing 
        p = "best choice"#TODO: REPLACE WITH GQL
        self.redirect('blog/%s', str(p.key().id()))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newArgument', NewArgHandler),
    ('/play/', StartPlayHandler),
    ('/play/([0-9]+)', PlayHandler),
    ('/thanks', ThanksHandler)
], debug=True)
