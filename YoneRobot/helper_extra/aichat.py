from YoneRobot.mongo import client as db_x

lydia = db_x["CHATBOT"]
talkmode = db_x["TALKMODE"]


def add_chat(chat_id):
    stark = lydia.find_one({"chat_id": chat_id})
    if stark:
        return False
    else:
        lydia.insert_one({"chat_id": chat_id})
        return True


def remove_chat(chat_id):
    stark = lydia.find_one({"chat_id": chat_id})
    if not stark:
        return False
    else:
        lydia.delete_one({"chat_id": chat_id})
        return True


def get_session(chat_id):
    star = talkmode.find_one({"chat_id": chat_id})
    if not star:
        return False
    else:
        return star