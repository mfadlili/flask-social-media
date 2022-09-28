from app import db
from models import User, followers, Post

chat_room = User.query.join(room_chat, (room_chat.c.user_one==user_one.id)).filter(room_chat.c.user_two==user_two.id).first()
id_cr = chat_room.room_id

