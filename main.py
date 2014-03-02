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
    sex1 = db.StringProperty(required = True)


    name2 = db.StringProperty(required = True)
    arg2 = db.TextProperty(required = True)
    sex2 = db.StringProperty(required = True)


    created = db.DateTimeProperty(auto_now_add = True)
    
    #who's winning
    score1 = db.IntegerProperty()
    score2 = db.IntegerProperty()

    maleCorrect = db.IntegerProperty()
    femaleCorrect = db.IntegerProperty()

    rating = db.IntegerProperty()
    #improve to hotness algorithm = db.integer

    #TODO: Update this shitKHJK
    "****Methods****"
    def score_up1():
        score1 += 1
    def score_up2():
        score2 += 1

    def ratingUp():
        rating += 1
    def maleCorrect():
        maleCorrect += 1
    def femaleCorrect():
        femaleCorrect += 1

class MainHandler(Handler):
    def get(self):
        self.render("index.html")

class NewArgHandler(Handler):
    def get(self):
        self.render("argument.html")

    def post(self):
        #TODO: do handling on creating a new argument
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
            url = 'judge/' + str(a.key().id())
            self.redirect(url)
            #self.redirect(url)#TODO: MAKE thanks.html
        else:
            error = "Please fill in all required information."
            self.render("argument.html", title = title, name1 = name1,
                        name2 = name2, arg1 = arg1, arg2 = arg2, error = error)

class ThanksHandler(Handler):
    def get(self):
        self.response.write("Thanks.")


class JudgeHandler(Handler):
    def get(self):
        #TODO: Get best question/random, existing
        args = db.GqlQuery("SELECT * FROM Argument ORDER BY created DESC")#DESC=descending order
        for arg in args:
            a = arg
            break
        url = 'judge/' + str(a.key().id())
        self.redirect(url)

class PlayHandler(Handler):
    def __init__(self, x, y):
        Handler.__init__(self,x,y)
        self.arg = None

    def get(self, arg_id):
        key = db.Key.from_path('Argument', int(arg_id))
        self.arg = arg = db.get(key)
        if not arg:
            self.error(404)
            return
        self.render("judge.html", squabble = arg)#TODO: Make sure elements are in dot notation
    def post(self):
        #change arg's score and rating.
        arg = self.arg
        decision = self.request.get('decision')
        star = self.request.get('favorite')
        if (decision):
            #Also keeps track of male vs female
            if decision == "1":
                arg.score_up1()
                if arg.sex1 == "male":
                    arg.maleCorrect()
                else:
                    arg.femaleCorrect()
            elif decision == "2":
                arg.score_up2()
                if arg.sex2 == "male":
                    arg.maleCorrect()
                else:
                    arg.femaleCorrect()
            if star:
                arg.ratingsUp()
            #TODO: DELETE AND FIX
            self.redirect("/")
        else:
            error = "Please choose a side."
            self.render("judge.html", squabble = arg, error = error)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/argument', NewArgHandler),
    ('/judge', JudgeHandler),
    ('/judge/([0-9]+)', PlayHandler),
    ('/thanks', ThanksHandler)
], debug=True)
