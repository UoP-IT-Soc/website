from flask import Flask, request, render_template, redirect, url_for, session, flash, Response
import json
import os
import dotenv
from datetime import datetime
from models import db, User, News, NewsComment, NewsLetter
import random
import string
import bcrypt

dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

# Function to generate a random password
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(characters, k=length))

# Custom Jinja2 filter
@app.template_filter('format_date')
def format_date(value, format='%d %b'):
    return datetime.strptime(value, '%Y-%m-%d').strftime(format)

# Ensure user is logged in and is an admin
def login_required(func):
    from functools import wraps

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to access this page.', 'danger')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('You are not authorized to access this page.', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)

    return decorated_view

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    with open('events.json', 'r') as file:
        events = json.load(file)
    events = sorted(events, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
    events = [event for event in events if datetime.strptime(event['date'], '%Y-%m-%d') >= datetime.now()]
    events = events[:3]
    return render_template('index.html', events=events)

@app.route('/members')
def members():
    members = User.query.all()
    return render_template('members.html', members=members)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Add a new member
        if action == 'add':
            name = request.form.get('name')
            email = request.form.get('email')
            class_of = request.form.get('class_of')
            level = request.form.get('level')
            is_admin = request.form.get('is_admin')
            role = request.form.get('role')


            is_admin = is_admin == 'on'


            # Generate a random password
            raw_password = generate_random_password()
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Create a new user
            if role:
                new_user = User(name=name,
                                email=email,
                                hashed_password=hashed_password,
                                class_of=class_of,
                                level=level,
                                role=role,
                                is_verified=True,
                                image='default.jpg',
                                is_admin=is_admin)
            else:
                new_user = User(name=name,
                                email=email,
                                hashed_password=hashed_password,
                                class_of=class_of,
                                level=level,
                                is_verified=True,
                                image='default.jpg',
                                is_admin=is_admin)
                
            try:
                db.session.add(new_user)
                db.session.commit()
                flash(f'New member added! Their password is: {raw_password}', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')

        # Delete a member
        elif action == 'delete':
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            if user:
                try:
                    db.session.delete(user)
                    db.session.commit()
                    flash(f'Member {user.name} deleted successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error: {str(e)}', 'danger')

    members = User.query.all()
    return render_template('admin.html', members=members)


@app.route('/news/<int:pagenum>')
def news(pagenum):
    articles = News.query.order_by(News.date_posted.desc()).all()
    
    # Pagination logic: limit articles per page
    per_page = 5
    total_articles = len(articles)
    start_idx = (pagenum - 1) * per_page
    end_idx = start_idx + per_page
    articles = articles[start_idx:end_idx]

    # Handle edge case where page number exceeds available pages
    if pagenum < 1 or start_idx >= total_articles:
        return redirect('/news/1')

    return render_template('news.html', articles=articles, pagenum=pagenum)


@app.route('/rss')
def rss():
    articles = News.query.all()
    articles = articles[::-1]
    return Response(render_template('rss.xml', articles=articles), mimetype='text/xml')

@app.route('/article/<int:article_id>')
def article(article_id):
    article = News.query.get(article_id)
    return render_template('article.html', article=article)

@app.route('/manage_news', methods=['GET', 'POST'])
@login_required
def manage_news():
    if request.method == 'POST':
        action = request.form.get('action')

        # Add a new article
        if action == 'add':
            title = request.form.get('title')
            content = request.form.get('content')
            user_id = session['user_id']

            new_article = News(title=title, content=content, date_posted=datetime.now(), user_id=user_id)
            try:
                db.session.add(new_article)
                db.session.commit()
                flash('Article added successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')

        # Delete an article
        elif action == 'delete':
            article_id = request.form.get('article_id')
            article = News.query.get(article_id)
            if article:
                try:
                    db.session.delete(article)
                    db.session.commit()
                    flash('Article deleted successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error: {str(e)}', 'danger')

    articles = News.query.order_by(News.date_posted.desc()).all()
    return render_template('manage_news.html', articles=articles)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  #tables are created (I know fine dinning)
        # Create an admin user if no users exist
        if User.query.count() == 0:
            admin = User(name='Admin', email=os.getenv('ADMIN_EMAIL'), hashed_password=bcrypt.hashpw(os.getenv('ADMIN_PASSWORD').encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), is_admin=True, is_verified=True,class_of='000',level='ADMIN',role='admin',image='default.jpg')
            db.session.add(admin)
            db.session.commit()


    app.run(debug=True)