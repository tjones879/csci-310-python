from pymongo import MongoClient, ASCENDING, collection, errors
from multipong.models import User


def init_users(client: MongoClient) -> collection:
    db = client.myDB
    users = db.users
    users.create_index([("oauth_id", ASCENDING), ("provider", ASCENDING)],
                       unique=True, background=True)
    return users


def insert_user(users: collection.Collection, user: User) -> None:
    try:
        users.insert_one(dict(user))
    except errors.DuplicateKeyError:
        pass


def get_user(users: collection.Collection, key: dict):
    print(key)
    resp = users.find_one(filter=key)
    return resp
