from pymongo import collection


class User:
    '''Represent a user document in a mongodb collection'''
    def __init__(self, oauth_id: str, provider: str):
        self.oauth_id = oauth_id
        self.provider = provider
        self.best_score = 0

    def key(self):
        yield 'oauth_id', self.oauth_id
        yield 'provider', self.provider

    def __iter__(self):
        yield 'oauth_id', self.oauth_id
        yield 'provider', self.provider
        yield 'best_score', self.best_score

    def update_score(self, score: int) -> int:
        if score > self.best_score:
            self.best_score = score
        return self.best_score

    def update_db(self, col: collection.Collection):
        col.update_one(dict(self.key()),
                       {'$set': {'score': self.best_score}},
                       upsert=True)
