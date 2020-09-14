from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
import json,math
from datetime import datetime
local_server = True
with open("config.json",'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = "xx-secret-key"

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

db = SQLAlchemy(app)

class Contacts(db.Model):
    #  	sno 	name 	email 	phone_no 	msg 	date 	
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(12), nullable=False)
    phone_no = db.Column(db.String(12),  nullable=False)
    msg = db.Column(db.String(12),nullable=False)
    date = db.Column(db.String(20),nullable=True)

class Posts(db.Model):
    #  	sno title slug content date 	
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    tagline = db.Column(db.String(30), nullable=False)
    slug = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(100),  nullable=False)
    date = db.Column(db.String(12),nullable=True)


@app.route('/')
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params["no_posts"]))
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[int(params["no_posts"])*(page-1):int(params["no_posts"])*(page-1)+int(params["no_posts"])]
    
    if page==1:
        prev = "#"
        next = "/?page="+str(page+1)
    elif page==last:
        prev = "/?page="+str(page-1)
        next = "#"
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)
    
    
    return render_template('index.html',posts=posts,prev=prev,next=next)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard',methods=['POST','GET'])
def dashboard():
    if 'user' in session and session['user']==params["username"]:
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params,posts=posts)
    
    if request.method=="POST":
        email = request.form.get('email')
        password = request.form.get('password')
        if(email==params["username"] and password==params["password"]):
            posts = Posts.query.all()
            session['user'] = email
            return render_template('dashboard.html',params=params,posts=posts)
    return render_template('login.html',params=params)

@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post  = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',post=post)

@app.route('/Edit/<string:sno>', methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user']==params["username"]:
        if request.method =="POST":
            title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            date = datetime.now()
            if sno=='0':
                entry = Posts(title=title,tagline=tline,slug=slug,content=content,date = date)
                db.session.add(entry)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.slug = slug
                post.content = content
                post.tagline  = tline
                post.date = date
                db.session.commit()
                return redirect('/Edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post)


@app.route('/delete/<string:sno>')
def delete(sno):
    if 'user' in session and session['user']==params["username"]:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method=="POST":
        #add entry to the database
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        message = request.form.get('message')

        entry = Contacts(name=name,email=email,phone_no=phone,msg=message,date = datetime.now())
        db.session.add(entry)
        db.session.commit()
    
    return render_template('contact.html')

app.run(debug=True)