
class Comment:


    def __init__(self, comment_id, username, text):
        self.comment_id = comment_id
        self.username   = username
        self.text       = text

    def __repr__(self):
        return f"Comment(id={self.comment_id}, user='{self.username}', text='{self.text}')"

    def __eq__(self, other):
        if not isinstance(other, Comment):
            return False
        return self.comment_id == other.comment_id

class Like:

    def __init__(self, like_id, username):
        self.like_id  = like_id
        self.username = username

    def __repr__(self):
        return f"Like(id={self.like_id}, user='{self.username}')"

    def __eq__(self, other):
        if not isinstance(other, Like):
            return False
        return self.like_id == other.like_id

class Post:

    def __init__(self, post_id, username, caption):
        self.post_id  = post_id
        self.username = username
        self.caption  = caption
        self.comments = []   # starts as an empty list; comments are added later
        self.likes    = []   # starts as an empty list; likes are added later

    def __repr__(self):
        return (
            f"Post(id={self.post_id}, "
            f"user='{self.username}', "
            f"caption='{self.caption}', "
            f"comments={len(self.comments)}, "
            f"likes={len(self.likes)})"
        )

    def __eq__(self, other):
        if not isinstance(other, Post):
            return False
        return self.post_id == other.post_id

    def __len__(self):
        return len(self.comments) + len(self.likes)

    def add_comment(self, comment):
        self.comments.append(comment)

    def add_like(self, like):
        self.likes.append(like)
