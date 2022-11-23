import threading
from sqlalchemy import Column, String
from Yone.Database import BASE, SESSION
class YoneChats(BASE):
    __tablename__ = "yone_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id

YoneChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_yone(chat_id):
    try:
        chat = SESSION.query(YoneChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()

def set_yone(chat_id):
    with INSERTION_LOCK:
        yonechat = SESSION.query(YoneChats).get(str(chat_id))
        if not yonechat:
            yonechat = YoneChats(str(chat_id))
        SESSION.add(yonechat)
        SESSION.commit()

def rem_yone(chat_id):
    with INSERTION_LOCK:
        yonechat = SESSION.query(YoneChats).get(str(chat_id))
        if yonechat:
            SESSION.delete(yonechat)
        SESSION.commit()


def get_all_yone_chats():
    try:
        return SESSION.query(YoneChats.chat_id).all()
    finally:
        SESSION.close()