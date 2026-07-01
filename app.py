from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Jaimin%402005@localhost/blog_app'
app.config['SECRET_KEY'] = 'Jaimin@2005'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    blogs = db.relationship(
        "Blog",
        backref="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    comments = db.relationship(
        "Comment",
        backref="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    likes = db.relationship(
        "Like",
        backref="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    image = db.Column(db.String(500))
    description = db.Column(db.Text, nullable=False)
    subtitle = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "user.id",
            ondelete="CASCADE"
        )
    )

    comments = db.relationship(
        "Comment",
        backref="blog",
        cascade="all, delete-orphan",
        lazy=True
    )

    likes = db.relationship(
        "Like",
        backref="blog",
        cascade="all, delete-orphan",
        lazy=True
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, title, category, author, date, image, description, subtitle, content, user_id):
        self.title = title
        self.category = category
        self.author = author
        self.date = date
        self.image = image
        self.description = description
        self.subtitle = subtitle
        self.content = content
        self.user_id = user_id

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, email, subject, message):
        self.name = name
        self.email = email
        self.subject = subject
        self.message = message

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'blog_id', name='unique_user_blog_like'),)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "user.id",
            ondelete="CASCADE"
        )
    )


    blog_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "blog.id",
            ondelete="CASCADE"
        )
    )

    user_name = db.Column(db.String(100))
    user_email = db.Column(db.String(100))

    blog_title = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, blog_id, user_name, user_email, blog_title):
        self.user_id = user_id
        self.blog_id = blog_id
        self.user_name = user_name
        self.user_email = user_email
        self.blog_title = blog_title

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "user.id",
            ondelete="CASCADE"
        )
    )

    blog_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "blog.id",
            ondelete="CASCADE"
        )
    )

    user_name = db.Column(db.String(100))
    user_email = db.Column(db.String(100))

    blog_title = db.Column(db.String(255))

    comment = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, blog_id, user_name, user_email, blog_title, comment):
        self.user_id = user_id
        self.blog_id = blog_id
        self.user_name = user_name
        self.user_email = user_email
        self.blog_title = blog_title
        self.comment = comment

with app.app_context():
    db.create_all()

@app.route('/')
def index():

    search = request.args.get('search', '').strip()
    query = Blog.query

    if search:
        query = query.filter(
            db.or_(
                Blog.title.ilike(f"%{search}%"),
                Blog.category.ilike(f"%{search}%")
            )
        )

    blogs = query.order_by(
        Blog.created_at.desc()
    ).all()

    liked_blogs = []

    if 'user_id' in session:
        liked_blogs = [
            like.blog_id
            for like in Like.query.filter_by(
                user_id=session['user_id']
            ).all()
        ]

    return render_template(
        'home.html',
        blogs=blogs,
        liked_blogs=liked_blogs,
        total_blogs=len(blogs),
        search=search
    )

@app.route('/signup',methods=['GET','POST'])
def signup():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            error = 'This email is already registered. Please use a different email or login.'
        else:
            new_user = User(name=name,email=email,password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')

    return render_template('signup.html', error=error)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email'] = user.email
            session['user_id'] = user.id
            session['name'] = user.name
            return redirect('/')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email',None)
    session.pop('user_id', None)
    session.pop('name', None)
    return redirect('/')

@app.route('/blogs')
def blogs():

    if 'email' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '').strip()

    query = Blog.query.filter_by(
        user_id=session['user_id']
    )

    if search:
        query = query.filter(
            db.or_(
                Blog.title.ilike(f"%{search}%"),
                Blog.category.ilike(f"%{search}%")
            )
        )

    blogs = query.order_by(
        Blog.created_at.desc()
    ).all()

    liked_blogs = [
        like.blog_id
        for like in Like.query.filter_by(
            user_id=session['user_id']
        ).all()
    ]

    comments = db.relationship(
        'Comment',
        backref='blog',
        lazy=True,
        cascade='all, delete-orphan'
    )

    categories = db.session.query(
        Blog.category
    ).filter_by(
        user_id=session['user_id']
    ).distinct().all()

    categories = [cat[0] for cat in categories]

    return render_template(
        'blogs.html',
        blogs=blogs,
        categories=categories,
        search=search,
        liked_blogs=liked_blogs
    )

@app.route('/blg/<int:blog_id>')
def blg(blog_id):

    blog = Blog.query.get_or_404(blog_id)

    source = request.args.get('source')

    liked = False

    if 'user_id' in session:
        liked = Like.query.filter_by(
            user_id=session['user_id'],
            blog_id=blog.id
        ).first() is not None

    comments = Comment.query.filter_by(
        blog_id=blog.id
    ).order_by(
        Comment.created_at.desc()
    ).all()

    return render_template(
        'blg.html',
        blog=blog,
        source=source,
        liked=liked,
        comments=comments
    )

@app.route('/like/<int:blog_id>', methods=['POST'])
def like_blog(blog_id):

    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'login_required': True
        })

    blog = Blog.query.get_or_404(blog_id)

    existing_like = Like.query.filter_by(
        user_id=session['user_id'],
        blog_id=blog.id
    ).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()

        likes_count = Like.query.filter_by(
            blog_id=blog.id
        ).count()

        return jsonify({
            'success': True,
            'liked': False,
            'count': likes_count
        })

    like = Like(
        user_id=session['user_id'],
        blog_id=blog.id,
        user_name=session['name'],
        user_email=session['email'],
        blog_title=blog.title
    )

    db.session.add(like)
    db.session.commit()

    likes_count = Like.query.filter_by(
        blog_id=blog.id
    ).count()

    return jsonify({
        'success': True,
        'liked': True,
        'count': likes_count
    })

@app.route('/comment/<int:blog_id>', methods=['POST'])
def add_comment(blog_id):

    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'login_required': True
        })

    text = request.form.get('comment')

    if not text:
        return jsonify({
            'success': False
        })

    blog = Blog.query.get_or_404(blog_id)

    comment = Comment(
        user_id=session['user_id'],
        blog_id=blog.id,
        user_name=session['name'],
        user_email=session['email'],
        blog_title=blog.title,
        comment=text
    )

    db.session.add(comment)
    db.session.commit()

    comments = Comment.query.filter_by(
        blog_id=blog.id
    ).all()

    return jsonify({
        'success': True,
        'count': len(comments)
    })

@app.route('/edit-blog/<int:blog_id>', methods=['GET', 'POST'])
def edit_blog(blog_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    blog = Blog.query.filter_by(
        id=blog_id,
        user_id=session['user_id']).first_or_404()

    if request.method == 'POST':

        blog.title = request.form['title']
        blog.category = request.form['category']
        blog.author = request.form['author']
        blog.date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()
        blog.image = request.form['image']
        blog.description = request.form['description']
        blog.subtitle = request.form['subtitle']
        blog.content = request.form['content']

        db.session.commit()

        return redirect(url_for('blg', blog_id=blog.id))

    return render_template('editblog.html',blog=blog)

@app.route('/delete-blog/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    blog = Blog.query.filter_by(
        id=blog_id,
        user_id=session['user_id']
    ).first_or_404()

    db.session.delete(blog)
    db.session.commit()

    return redirect(url_for('blogs'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':

        contact_data = Contact(
            name=request.form['name'],
            email=request.form['email'],
            subject=request.form['subject'],
            message=request.form['message']
        )

        db.session.add(contact_data)
        db.session.commit()

        flash('Your message has been sent successfully!', 'success')

        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/addtask')
def addtask():
    return render_template('addtask.html')

@app.route('/addtask', methods=['POST'])
def addtaskview():
    blog = Blog(
        title=request.form['title'],
        category=request.form['category'],
        author=request.form['author'],
        date=datetime.strptime(request.form['date'], "%Y-%m-%d").date(),
        image=request.form['image'],
        description=request.form['description'],
        subtitle=request.form['subtitle'],
        content=request.form['content'],
        user_id=session['user_id']
        )
    db.session.add(blog)
    db.session.commit()
    
    return redirect(url_for('blogs'))

@app.route('/admin')
def admin():

    total_users = User.query.count()
    total_posts = Blog.query.count()
    total_comments = Comment.query.count()
    total_contacts = Contact.query.count()

    users = User.query.all()
    contacts = Contact.query.all()
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()

    categories = db.session.query(
        Blog.category,
        db.func.count(Blog.id).label("total_blogs")
    ).group_by(
        Blog.category
    ).all()
    
    recent_posts = Blog.query.order_by(
        Blog.updated_at.desc()
    ).limit(5).all()
    
    return render_template(
        'admin.html',
        total_users=total_users,
        total_posts=total_posts,
        total_comments=total_comments,
        total_contacts=total_contacts,
        users=users,
        contacts=contacts,
        comments=comments,
        categories=categories,
        blogs=blogs,
        recent_posts=recent_posts
    )

@app.route('/admin/edit-blog/<int:blog_id>', methods=['GET', 'POST'])
def admin_edit_blog(blog_id):

    blog = Blog.query.get_or_404(blog_id)

    if request.method == 'POST':

        blog.title = request.form['title']
        blog.category = request.form['category']
        blog.author = request.form['author']
        blog.date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()
        blog.image = request.form['image']
        blog.description = request.form['description']
        blog.subtitle = request.form['subtitle']
        blog.content = request.form['content']

        db.session.commit()

        return redirect(url_for('admin'))

    return render_template(
        'editblog.html',
        blog=blog
    )

@app.route('/admin/delete-blog/<int:blog_id>', methods=['POST'])
def admin_delete_blog(blog_id):

    blog = Blog.query.get_or_404(blog_id)

    db.session.delete(blog)
    db.session.commit()

    return redirect(url_for('admin'))

@app.route("/delete-user/<int:id>", methods=["POST"])
def delete_user(id):

    user = User.query.get_or_404(id)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("admin"))

@app.route("/delete-comment/<int:id>", methods=["POST"])
def delete_comment(id):

    comment = Comment.query.get_or_404(id)

    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for("admin"))

if __name__ == '__main__':
    app.run(debug=True, port = 8000)