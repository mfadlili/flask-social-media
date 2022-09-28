from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

followers = db.Table("followers",
                     db.Column("follower_id", db.Integer, db.ForeignKey("user.id")), 
                     db.Column("followed_id", db.Integer, db.ForeignKey("user.id")),
                     )

like_post = db.Table("like_post",
                     db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                     db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
                     )

dislike_post = db.Table("dislike_post",
                     db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                     db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
                     )

like_comment = db.Table("like_comment",
                     db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                     db.Column("comment_id", db.Integer, db.ForeignKey("comment.id")),
                     )

dislike_comment = db.Table("dislike_comment",
                     db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                     db.Column("comment_id", db.Integer, db.ForeignKey("comment.id")),
                     )



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.String(120), default='Blank')
    photo = db.Column(db.String(64), nullable=False, default='default.jpg')
    last_seen = db.Column(db.DateTime, index=True)
    posts = db.relationship("Post", backref='author', lazy='dynamic')
    followed = db.relationship("User",
                               secondary=followers,
                               primaryjoin = (followers.c.follower_id==id),
                               secondaryjoin = (followers.c.followed_id==id),
                               backref = db.backref("follower", lazy="dynamic"),
                               lazy= "dynamic",
                               )
    likes = db.relationship("Post", secondary=like_post, backref="likers", lazy="dynamic",)
    dislikes = db.relationship("Post", secondary=dislike_post, backref="dislikers", lazy="dynamic",)
    comments = db.relationship("Comment", backref='commentator', lazy='dynamic')
    comment_likes = db.relationship("Comment", secondary=like_comment, backref="likers", lazy="dynamic",)
    comment_dislikes = db.relationship("Comment", secondary=dislike_comment, backref="dislikers", lazy="dynamic",)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_follow(self, other_user):
        return other_user in self.followed

    def is_like(self, any_post):
        return any_post in self.likes
    
    def is_dislike(self, any_post):
        return any_post in self.dislikes
    
    def is_like_comment(self, any_comment):
        return any_comment in self.comment_likes
    
    def is_dislike_comment(self, any_comment):
        return any_comment in self.comment_dislikes

class RoomChat(db.Model):
    __tablename__ = "room_chat"
    id = db.Column(db.Integer, primary_key=True)
    user_one = db.Column("user_one", db.Integer, db.ForeignKey("user.id"))
    user_two = db.Column("user_two", db.Integer, db.ForeignKey("user.id"))

    def __init__(self, user_one, user_two,):
        self.user_one = user_one
        self.user_two = user_two

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments_list = db.relationship("Comment", backref='main_post', lazy='dynamic')

    def __init__(self, title, body, user_id):
        self.title = title
        self.body = body
        self.user_id = user_id

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __init__(self, body, user_id, post_id):
        self.body = body
        self.user_id = user_id
        self.post_id = post_id

class ConversationText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String())
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room_chat.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __init__(self, message, from_user_id, room_id):
        self.message = message
        self.from_user_id = from_user_id
        self.room_id = room_id    