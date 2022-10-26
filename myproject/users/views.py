from flask import render_template, url_for, redirect, flash, request, Blueprint
from flask_login import current_user, login_user, login_required, logout_user
from myproject import db
from myproject.users.forms import LoginForm, RegistrationForm, EditProfile
from myproject.models import User, Post
from myproject.users.helper import add_profil_pict

users = Blueprint('users',__name__)

@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('core.home'))

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('username or password is incorrect')
            return redirect(url_for('users.login'))

        login_user(user)
        return redirect(url_for('core.home'))

    return render_template('login.html', form=form)

@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('core.home'))

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username, email, password)
        db.session.add(user)
        db.session.commit()
        flash('Thank you for registering your account')
        return redirect(url_for('users.login'))

    return render_template('register.html', form=form)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out')
    return redirect(url_for('core.home'))

@users.route('/profile/<int:id>')
def profile(id):
    user = User.query.get(id)
    photo = url_for('static', filename='profile_pic/' + user.photo)

    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id = user.id).order_by(Post.timestamp.desc()).paginate(page, 5, False)
    next_url = url_for('users.profile', id=id, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('users.profile', id=id, page=posts.prev_num) if posts.has_prev else None

    count_follower = len(list(user.follower))
    count_followed = len(list(user.followed))
    return render_template("profile.html", user=user, posts=posts, photo=photo, num_follower = count_follower, num_followed = count_followed,
                            next_url=next_url, prev_url=prev_url)

@users.route('/edit_profile', methods=['GET', 'POST'])
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
        return redirect(url_for("users.profile", id=user.id))

    if request.method=="GET":
        form.username.data = user.username
        form.email.data = user.email
        form.about.data = user.about

    return render_template("edit_profile.html", user=user, form=form)

@users.route("/follow/<int:user_id>")
@login_required
def follow(user_id):
    user = User.query.get(user_id)
    if user==current_user:
        return redirect(url_for('core.home'))

    if not current_user.is_follow(user):
        current_user.followed.append(user)
        db.session.commit()
        return redirect(url_for("users.profile", id=user.id))
    else:
        return redirect(url_for("users.profile", id=user.id))

@users.route("/unfollow/<int:user_id>")
@login_required
def unfollow(user_id):
    user = User.query.get(user_id)
    if user==current_user:
        return redirect(url_for('core.home'))

    if current_user.is_follow(user):
        current_user.followed.remove(user)
        db.session.commit()
        return redirect(url_for("users.profile", id=user.id))
    else:
        return redirect(url_for("users.profile", id=user.id))

@users.route("/following/<int:user_id>")
def following_list(user_id):
    user = User.query.get(user_id)
    lst = []
    for i in user.followed.order_by(User.username.asc()):
        lst.append(i)
    return render_template("following.html", user=user, following=lst)

@users.route("/follower/<int:user_id>")
def follower_list(user_id):
    user = User.query.get(user_id)
    lst = []
    for i in user.follower.order_by(User.username.asc()):
        lst.append(i)
    return render_template("follower.html", user=user, follower=lst)