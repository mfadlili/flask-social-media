from flask import render_template, url_for, redirect, Blueprint
from flask_login import current_user, login_required
from myproject import app, db
from myproject.chats.forms import ChatUser
from myproject.models import User, ConversationText, RoomChat

chats = Blueprint('chats', __name__)

@chats.route("/<int:receiver_id>", methods=['GET', 'POST'])
@login_required
def chat(receiver_id):
    if receiver_id == current_user.id:
        return redirect(url_for("users.profile", id=receiver_id))
    
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

    
    
    
