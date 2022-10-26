from flask import Blueprint, render_template, request, url_for
from flask_login import current_user, login_required
from myproject import db
from myproject.models import User, Post, followers, ConversationText, RoomChat
from datetime import datetime

core = Blueprint("core", __name__)

@core.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@core.route('/')
def home():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        list_post = Post.query.join(followers, (followers.c.followed_id==Post.user_id)).filter(followers.c.follower_id==current_user.id).order_by(Post.timestamp.desc()).paginate(page, 1, False)
        next_url = url_for('core.home', page=list_post.next_num) if list_post.has_next else None
        prev_url = url_for('core.home', page=list_post.prev_num) if list_post.has_prev else None
    else :
        list_post = None
        next_url = None
        prev_url = None
    return render_template('home.html', posts=list_post, all_user=User.query, 
                            next_url=next_url, prev_url=prev_url
                            )

@core.route("/notifications")
@login_required
def notifications():
    room_first = RoomChat.query.filter_by(user_one=current_user.id).all()
    room_second = RoomChat.query.filter_by(user_two=current_user.id).all()
    rooms = []
    for room in room_first:
        rooms.append(room.id)
    for room in room_second:
        rooms.append(room.id)

    page = request.args.get('page', 1, type=int)
    messages = ConversationText.query.filter(ConversationText.room_id.in_(rooms)).filter(ConversationText.from_user_id != current_user.id).order_by(ConversationText.timestamp.desc()).paginate(page, 10, False)
    next_url = url_for('core.notifications', page=messages.next_num) if messages.has_next else None
    prev_url = url_for('core.notifications', page=messages.prev_num) if messages.has_prev else None

    return render_template("notifications.html", messages=messages, all_user=User.query, next_url=next_url, prev_url=prev_url)