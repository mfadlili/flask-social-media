from flask import render_template, url_for, redirect, request, Blueprint
from flask_login import current_user, login_required
from myproject import db
from myproject.posts.forms import PostForm, EditPost, AddComment
from myproject.models import User, Post, Comment
from datetime import datetime

posts = Blueprint('posts',__name__)

@posts.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        add_post = Post(title, body, current_user.id)
        db.session.add(add_post)
        db.session.commit()
        return redirect(url_for("users.profile", username=current_user.username))

    return render_template('create_post.html', form=form)

@posts.route('/view/<int:post_id>', methods=['GET', 'POST'])
def view(post_id):
    post = Post.query.filter_by(id=post_id).first()
    user = User.query.filter_by(id=post.user_id).first()

    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(post_id=post_id).paginate(page, 1, False)

    next_url = url_for('posts.view', post_id=post_id,page=comments.next_num) if comments.has_next else None
    prev_url = url_for('posts.view', post_id=post_id,page=comments.prev_num) if comments.has_prev else None

    count_likes = len(list(post.likers))
    count_dislikes = len(list(post.dislikers))
    count_comments = len(list(post.comments_list))

    form = AddComment()

    if form.validate_on_submit():
        body = form.body.data
        id_post = post_id
        id_user = current_user.id
        add_comment = Comment(body, id_user, id_post)
        db.session.add(add_comment)
        db.session.commit()
        return redirect(url_for('posts.view', post_id=post_id), )

    return render_template("view_post.html", post=post, user=user, form=form, comments=comments, all_user=User.query,
                            num_likes=count_likes, num_dislikes=count_dislikes, num_comments=count_comments, list=list, len=len,
                            next_url=next_url, prev_url=prev_url)

@posts.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.filter_by(id=post_id).first()
    
    if post.user_id != current_user.id:
        return redirect(url_for("home"))

    form = EditPost()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.timestamp = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("posts.view", post_id=post.id))

    if request.method=="GET":
        form.title.data = post.title
        form.body.data = post.body

    return render_template("edit_post.html", post=post, form=form)

@posts.route("/delete/<int:post_id>")
@login_required
def delete(post_id):
    post = Post.query.filter_by(id=post_id).first()
    user = User.query.filter_by(id=post.user_id).first()
    
    if post.user_id != current_user.id:
        return redirect(url_for("home"))
    
    db.session.delete(post)
    db.session.commit()
    
    return redirect(url_for("users.profile", id=user.id))

@posts.route("/like/<int:id>")
@login_required
def like(id):
    post = Post.query.get(id)
    user = User.query.get(post.user_id)
    if user==current_user:
        return redirect(url_for('posts.view', post_id=id))

    if not current_user.is_like(post):
        if current_user.is_dislike(post): 
            current_user.dislikes.remove(post)
            current_user.likes.append(post)
        else :
            current_user.likes.append(post)
        db.session.commit()
        return redirect(url_for('posts.view', post_id=id))
    else:
        return redirect(url_for('posts.view', post_id=id))

@posts.route("/unlike/<int:id>")
@login_required
def unlike(id):
    post = Post.query.get(id)
    user = User.query.get(post.user_id)

    if user==current_user:
        return redirect(url_for('posts.view', post_id=id))

    if current_user.is_like(post):
        current_user.likes.remove(post)
        db.session.commit()
        return redirect(url_for('posts.view', post_id=id))
    else:
        return redirect(url_for('posts.view', post_id=id))

@posts.route("/dislike/<int:id>")
@login_required
def dislike(id):
    post = Post.query.get(id)
    user = User.query.get(post.user_id)
    if user==current_user:
        return redirect(url_for('posts.view', post_id=id))

    if not current_user.is_dislike(post):
        if current_user.is_like(post): 
            current_user.likes.remove(post)
            current_user.dislikes.append(post)
        else :
            current_user.dislikes.append(post)
        db.session.commit()
        return redirect(url_for('posts.view', post_id=id))
    else:
        return redirect(url_for('posts.view', post_id=id))

@posts.route("/undislike/<int:id>")
@login_required
def undislike(id):
    post = Post.query.get(id)
    user = User.query.get(post.user_id)

    if user==current_user:
        return redirect(url_for('posts.view', post_id=id))

    if current_user.is_dislike(post):
        current_user.dislikes.remove(post)
        db.session.commit()
        return redirect(url_for('posts.view', post_id=id))
    else:
        return redirect(url_for('posts.view', post_id=id))


@posts.route("/like_comment/<int:id>")
@login_required
def like_comment(id):
    comment = Comment.query.get(id)
    user = User.query.get(comment.user_id)
    if user==current_user:
        return redirect(url_for('posts.view', post_id=comment.post_id))

    if not current_user.is_like_comment(comment):
        if current_user.is_dislike_comment(comment): 
            current_user.comment_dislikes.remove(comment)
            current_user.comment_likes.append(comment)
        else :
            current_user.comment_likes.append(comment)
        db.session.commit()
        return redirect(url_for('posts.view', post_id=comment.post_id))
    else:
        return redirect(url_for('posts.view', post_id=comment.post_id))

@posts.route("/unlike_comment/<int:id>")
@login_required
def unlike_comment(id):
    comment = Comment.query.get(id)
    user = User.query.get(comment.user_id)

    if user==current_user:
        return redirect(url_for('posts.view', post_id=comment.post_id))

    if current_user.is_like_comment(comment):
        current_user.comment_likes.remove(comment)
        db.session.commit()
        return redirect(url_for('posts.view', post_id=comment.post_id))
    else:
        return redirect(url_for('posts.view', post_id=comment.post_id))

@posts.route("/dislike_comment/<int:id>")
@login_required
def dislike_comment(id):
    comment = Comment.query.get(id)
    user = User.query.get(comment.user_id)
    if user==current_user:
        return redirect(url_for('posts.view', post_id=comment.post_id))

    if not current_user.is_dislike_comment(comment):
        if current_user.is_like_comment(comment): 
            current_user.comment_likes.remove(comment)
            current_user.comment_dislikes.append(comment)
        else :
            current_user.comment_dislikes.append(comment)
        db.session.commit()
        return redirect(url_for('posts.view', post_id=comment.post_id))
    else:
        return redirect(url_for('posts.view', post_id=comment.post_id))

@posts.route("/undislike_comment/<int:id>")
@login_required
def undislike_comment(id):
    comment = Comment.query.get(id)
    user = User.query.get(comment.user_id)

    if user==current_user:
        return redirect(url_for('posts.view', post_id=comment.post_id))

    if current_user.is_dislike_comment(comment):
        current_user.comment_dislikes.remove(comment)
        db.session.commit()
        return redirect(url_for('posts.view', post_id=comment.post_id))
    else:
        return redirect(url_for('posts.view', post_id=comment.post_id))