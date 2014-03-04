import os
import random
import webapp2
import cgi
import re
import jinja2
import time

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

class IDList(db.Expando):
    theList = db.ListProperty(int)
    count = 0
    created = db.DateTimeProperty(auto_now_add = True)

#"Row" in database table
class Argument(db.Expando):
    title = db.StringProperty(required = True)

    name1 = db.StringProperty(required = True)
    arg1 = db.TextProperty(required = True)
    sex1 = db.StringProperty(required = True)

    name2 = db.StringProperty(required = True)
    arg2 = db.TextProperty(required = True)
    sex2 = db.StringProperty(required = True)

    created = db.DateTimeProperty(auto_now_add = True)

    #who's winning
    score1 = 0
    score2 = 0

    maleCorrect = 0
    femaleCorrect = 0

    rating = 0
    #improve to hotness algorithm = db.integer

class MainHandler(Handler):
    def get(self):
        self.render("index.html")

class AboutHandler(Handler):
    def get(self):
        self.render("about.html")

class ContactHandler(Handler):
    def get(self):
        self.render("contact.html")

class NewArgHandler(Handler):
    def get(self):
        self.render("argument.html")

    def post(self):
        title = self.request.get('title')
        name1 = self.request.get('name1')
        name2 = self.request.get('name2')
        arg1 = self.request.get('arg1')
        arg2 = self.request.get('arg2')
        sex1 = self.request.get('sex1')
        sex2 = self.request.get('sex2')
        if (title and name1 and name2 and arg1 and arg2 and sex1 and sex2):
            a = Argument(title = title, name1 = name1, name2 = name2, arg1 = arg1,
                          arg2 = arg2, sex1 = sex1, sex2 = sex2, score1 = 0, score2 = 0,
                          rating = 0, maleCorrect = 0, femaleCorrect = 0)
            a.put()

            idList = db.GqlQuery("SELECT * FROM IDList").get()
            idList.theList.append((a.key().id()))
            idList.put()

            url = 'judge/' + str(a.key().id())
            self.redirect(url)
        else:
            error = "Please fill in all required information."
            self.render("argument.html", title = title, name1 = name1,
                        name2 = name2, arg1 = arg1, arg2 = arg2, error = error)

class ThanksHandler(Handler):
    def get(self):
        self.response.write("Thanks.")

class JudgeHandler(Handler):
    def get(self):
        idList = db.GqlQuery("SELECT * FROM IDList ORDER BY created DESC").get()
        args = db.GqlQuery("SELECT * FROM Argument ORDER BY rating DESC").fetch(limit=100)
        a = args[idList.count]
        idList.count += 1
        if idList.count >= len(args):
            idList.count = 0
        idList.put()

        url = 'judge/' + str(a.key().id())
        self.redirect(url)

class PlayHandler(Handler):
    def get(self, arg_id):
        key = db.Key.from_path('Argument', int(arg_id))
        arg = db.get(key)
        if not arg:
            self.error(404)
            return
        self.render("judge.html", squabble = arg)

    def post(self, arg_id):
        #change arg's score and rating.
        key = db.Key.from_path('Argument', int(arg_id))
        arg = db.get(key)
        decision = self.request.get('decision')
        star = self.request.get('favorite')
        if (decision):
            if decision == "1":
                arg.score1 += 1
                if arg.sex1 == "male":
                    arg.maleCorrect += 1
                else:
                    arg.femaleCorrect += 1
            elif decision == "2":
                arg.score2 += 1
                if arg.sex2 == "male":
                    arg.maleCorrect += 1
                else:
                    arg.femaleCorrect += 1
            if star:
                arg.rating += 1
            arg.put()
            self.redirect("/judge")
        else:
            error = "Please choose a side."
            self.render("judge.html", squabble = arg, error = error)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/argument', NewArgHandler),
    ('/judge', JudgeHandler),
    ('/judge/([0-9]+)', PlayHandler),
    ('/about', AboutHandler),
    ('/contact', ContactHandler),
    ('/thanks', ThanksHandler)
], debug=True)