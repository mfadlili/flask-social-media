from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_user, login_required, logout_user
from app import app, db
from forms import LoginForm, RegistrationForm, PostForm, EditProfile, EditPost, AddComment, ChatUser
from models import User, Post, followers, Comment, ConversationText, RoomChat
from helper import add_profil_pict
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
def home():
    try:
        list_post = Post.query.join(followers, (followers.c.followed_id==Post.user_id)).filter(followers.c.follower_id==current_user.id).order_by(Post.timestamp.desc())
    except:
        list_post = None
    return render_template('home.html', posts=list_post, all_user=User.query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('username or password is incorrect')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('home'))

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username, email, password)
        db.session.add(user)
        db.session.commit()
        flash('Thank you for registering your account')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out')
    return redirect(url_for('home'))

@app.route('/profile/<int:id>')
def profile(id):
    user = User.query.get(id)
    posts = Post.query.filter_by(user_id = user.id).order_by(Post.timestamp.desc()).all()
    photo = url_for('static', filename='profile_pic/' + user.photo)
    count_follower = len(list(user.follower))
    count_followed = len(list(user.followed))
    return render_template("profile.html", user=user, posts=posts, photo=photo, num_follower = count_follower, num_followed = count_followed)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        add_post = Post(title, body, current_user.id)
        db.session.add(add_post)
        db.session.commit()
        return redirect(url_for("profile", username=current_user.username))

    return render_template('create_post.html', form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfile(current_user.username)
    user = User.query.filter_by(username=current_user.username).first()

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.about = form.about.data
        if form.photo.data:
            user.photo = add_profil_pict(form.photo.data, user.id)
        db.session.commit()
        return redirect(url_for("profile", id=user.id))

    if request.method=="GET":
        form.username.data = user.username
        form.email.data = user.email
        form.about.data = user.about

    return render_template("edit_profile.html", user=user, form=form)

@app.route('/view_post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    user = User.query.filter_by(id=post.user_id).first()
    comments = Comment.query.filter_by(post_id=post_id).all()
    form = AddComment()
    count_likes = len(list(post.likers))
    count_dislikes = len(list(post.dislikers))
    count_comments = len(list(post.comments_list))

    if form.validate_on_submit():
        body = form.body.data
        id_post = post_id
        id_user = current_user.id
        add_comment = Comment(body, id_user, id_post)
        db.session.add(add_comment)
        db.session.commit()
        return redirect(url_for('view_post', post_id=post_id), )

    return render_template("view_post.html", post=post, user=user, form=form, comments=comments, all_user=User.query,
                            num_likes=count_likes, num_dislikes=count_dislikes, num_comments=count_comments, list=list, len=len)

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    
    if post.user_id != current_user.id:
        return redirect(url_for("home"))

    form = EditPost()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.timestamp = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("view_post", post_id=post.id))

    if request.method=="GET":
        form.title.data = post.title
        form.body.data = post.body

    return render_template("edit_post.html", post=post, form=form)

@app.route("/delete_post/<int:post_id>")
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    user = User.query.filter_by(id=post.user_id).first()
    
    if post.user_id != current_user.id:
        return redirect(url_for("home"))
    
    db.session.delete(post)
    db.session.commit()
    
    return redirect(url_for("profile", id=user.id))

@app.route("/follow/<int:user_id>")
@login_required
def follow(user_id):
    user = User.query.get(user_id)
    if user==current_user:
        return redirect(url_for('home'))

    if not current_user.is_follow(user):
        current_user.followed.append(user)
        db.session.commit()
        return redirect(url_for("profile", id=user.id))
    else:
        return redirect(url_for("profile", id=user.id))

@app.route("/unfollow/<int:user_id>")
@login_required
def unfollow(user_id):
    user = User.query.get(user_id)
    if user==current_user:
        return redirect(url_for('home'))

    if current_user.is_follow(user):
        current_user.followed.remove(user)
        db.session.commit()
        return redirect(url_for("profile", id=user.id))
    else:
        return redirect(url_for("profile", id=user.id))

@app.route("/<int:user_id>/following")
def following_list(user_id):
    user = User.query.get(user_id)
    lst = []
    for i in user.followed.order_by(User.username.asc()):
        lst.append(i)
    return render_template("following.html", user=user, following=lst)

@app.route("/<int:user_id>/follower")
def follower_list(user_id):
    user = User.query.get(user_id)
    lst = []
    for i in user.follower.order_by(User.username.asc()):
        lst.append(i)
    return render_template("follower.html", user=user, follower=lst)

@app.route("/like_post/<int:id>")
@login_required
def like_post(id):
    post = Post.query.get(id)
    user = User.query.get(post.user_id)
    if user==current_user:
        return redirect(url_for('view_post', post_id=id))

    if not current_user.is_like(post):
        if current_user.is_dislike(post): 
            current_user.dislikes.remove(post)
            current_user.likes.append(post)
        else :
            current_user.likes.append(post)
        db.session.commit()
        return redirect(url_for('view_post', post_id=id))
    else:
        return redirect(url_for('view_post', post_id=id))

@app.route("/unlike_post/<int:id>")
@login_required
def unlike_post(id):
    post = Post.query.get(id)
    user = User.query.get(post.user_id)

    if user==current_user:
        return redirect(url_for('view_post', post_id=id))

    if current_user.is_like(post):
        current_user.likes.remove(post)
        db.session.commit()
        return redirect(url_for('view_post', post_id=id))
    else:
        return redirect(url_for('view_post', post_id=id))

@app.route("/dislike_post/<int:id>")
@login_required
def dislike_post(id):
    post = Post.query.get(id)
    user = User.query.get(post.user_id)
    if user==current_user:
        return redirect(url_for('view_post', post_id=id))

    if not current_user.is_dislike(post):
        if current_user.is_like(post): 
            current_user.likes.remove(post)
            current_user.dislikes.append(post)
        else :
            current_user.dislikes.append(post)
        db.session.commit()
        return redirect(url_for('view_post', post_id=id))
    else:
        return redirect(url_for('view_post', post_id=id))

@app.route("/undislike_post/<int:id>")
@login_required
def undislike_post(id):
    post = Post.query.get(id)
    user = User.query.get(post.user_id)

    if user==current_user:
        return redirect(url_for('view_post', post_id=id))

    if current_user.is_dislike(post):
        current_user.dislikes.remove(post)
        db.session.commit()
        return redirect(url_for('view_post', post_id=id))
    else:
        return redirect(url_for('view_post', post_id=id))

@app.route("/like_comment/<int:id>")
@login_required
def like_comment(id):
    comment = Comment.query.get(id)
    user = User.query.get(comment.user_id)
    if user==current_user:
        return redirect(url_for('view_post', post_id=comment.post_id))

    if not current_user.is_like_comment(comment):
        if current_user.is_dislike_comment(comment): 
            current_user.comment_dislikes.remove(comment)
            current_user.comment_likes.append(comment)
        else :
            current_user.comment_likes.append(comment)
        db.session.commit()
        return redirect(url_for('view_post', post_id=comment.post_id))
    else:
        return redirect(url_for('view_post', post_id=comment.post_id))

@app.route("/unlike_comment/<int:id>")
@login_required
def unlike_comment(id):
    comment = Comment.query.get(id)
    user = User.query.get(comment.user_id)

    if user==current_user:
        return redirect(url_for('view_post', post_id=comment.post_id))

    if current_user.is_like_comment(comment):
        current_user.comment_likes.remove(comment)
        db.session.commit()
        return redirect(url_for('view_post', post_id=comment.post_id))
    else:
        return redirect(url_for('view_post', post_id=comment.post_id))

@app.route("/dislike_comment/<int:id>")
@login_required
def dislike_comment(id):
    comment = Comment.query.get(id)
    user = User.query.get(comment.user_id)
    if user==current_user:
        return redirect(url_for('view_post', post_id=comment.post_id))

    if not current_user.is_dislike_comment(comment):
        if current_user.is_like_comment(comment): 
            current_user.comment_likes.remove(comment)
            current_user.comment_dislikes.append(comment)
        else :
            current_user.comment_dislikes.append(comment)
        db.session.commit()
        return redirect(url_for('view_post', post_id=comment.post_id))
    else:
        return redirect(url_for('view_post', post_id=comment.post_id))

@app.route("/undislike_comment/<int:id>")
@login_required
def undislike_comment(id):
    comment = Comment.query.get(id)
    user = User.query.get(comment.user_id)

    if user==current_user:
        return redirect(url_for('view_post', post_id=comment.post_id))

    if current_user.is_dislike_comment(comment):
        current_user.comment_dislikes.remove(comment)
        db.session.commit()
        return redirect(url_for('view_post', post_id=comment.post_id))
    else:
        return redirect(url_for('view_post', post_id=comment.post_id))

@app.route("/chat/<int:receiver_id>", methods=['GET', 'POST'])
@login_required
def chat(receiver_id):
    if receiver_id == current_user.id:
        return redirect(url_for("profile", id=receiver_id))
    
    if current_user.id > receiver_id:
        user_one = User.query.get(receiver_id)
        user_two = current_user
    else:
        user_one = current_user
        user_two = User.query.get(receiver_id)

    try :
        room = RoomChat.query.filter_by(user_one=user_one.id).filter_by(user_two=user_two.id).first()
        room_id = room.id
    except :
        room = RoomChat(user_one.id, user_two.id)
        db.session.add(room)
        db.session.commit()
        room_id = room.id
    
    all_chat = ConversationText.query.filter_by(room_id=room_id).all()
    
    form = ChatUser()
    if form.validate_on_submit():
        message = form.body.data
        new_message = ConversationText(message, current_user.id, room.id)
        db.session.add(new_message)
        db.session.commit() 
        return redirect(url_for("chat", receiver_id=receiver_id))

    return render_template("chat.html", form=form, all_chat=all_chat, all_user=User.query)

@app.route("/notifications")
@login_required
def notifications():
    room_first = RoomChat.query.filter_by(user_one=current_user.id).all()
    room_second = RoomChat.query.filter_by(user_two=current_user.id).all()
    rooms = []
    for room in room_first:
        rooms.append(room.id)
    for room in room_second:
        rooms.append(room.id)
    messages = ConversationText.query.filter(ConversationText.room_id.in_(rooms)).filter(ConversationText.from_user_id != current_user.id).order_by(ConversationText.timestamp.desc()).limit(10).all()
    return render_template("notifications.html", messages=messages, all_user=User.query)

    
    
    
