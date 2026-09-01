# models.py
# Point 12 — Data modeling
#
# Defines three simple data classes:
#   Post    — a single Instagram-style post
#   Comment — a comment left on a post
#   Like    — a like left on a post
#
# Each class implements three special (dunder) methods:
#   __repr__  → makes print() show something readable instead of <Post object at 0x...>
#   __eq__    → lets us compare two objects with == (compares by id)
#   __len__   → lets us use len() on the object (counts comments/likes on a Post)


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

class Comment:
    """
    Represents a single comment on a post.

    Attributes:
        comment_id (int)  : Unique identifier for this comment.
        username   (str)  : The person who wrote the comment.
        text       (str)  : The comment text.
    """

    def __init__(self, comment_id, username, text):
        self.comment_id = comment_id
        self.username   = username
        self.text       = text

    def __repr__(self):
        # Called when you print() a Comment or look at it in the REPL.
        # Returns a string that clearly shows what is inside the object.
        return f"Comment(id={self.comment_id}, user='{self.username}', text='{self.text}')"

    def __eq__(self, other):
        # Called when you use ==  e.g.  comment_a == comment_b
        # Two comments are considered equal if they have the same comment_id.
        if not isinstance(other, Comment):
            return False
        return self.comment_id == other.comment_id


# ---------------------------------------------------------------------------
# Like
# ---------------------------------------------------------------------------

class Like:
    """
    Represents a single like on a post.

    Attributes:
        like_id  (int) : Unique identifier for this like.
        username (str) : The person who liked the post.
    """

    def __init__(self, like_id, username):
        self.like_id  = like_id
        self.username = username

    def __repr__(self):
        return f"Like(id={self.like_id}, user='{self.username}')"

    def __eq__(self, other):
        # Two likes are equal if they have the same like_id.
        if not isinstance(other, Like):
            return False
        return self.like_id == other.like_id


# ---------------------------------------------------------------------------
# Post
# ---------------------------------------------------------------------------

class Post:
    """
    Represents a single Instagram-style post.

    Attributes:
        post_id   (int)         : Unique identifier for this post.
        username  (str)         : The author of the post.
        caption   (str)         : The post caption/description.
        comments  (list)        : A list of Comment objects. Starts empty.
        likes     (list)        : A list of Like objects. Starts empty.
    """

    def __init__(self, post_id, username, caption):
        self.post_id  = post_id
        self.username = username
        self.caption  = caption
        self.comments = []   # starts as an empty list; comments are added later
        self.likes    = []   # starts as an empty list; likes are added later

    # -- Dunder methods -------------------------------------------------------

    def __repr__(self):
        # Shows the post's key information when printed.
        return (
            f"Post(id={self.post_id}, "
            f"user='{self.username}', "
            f"caption='{self.caption}', "
            f"comments={len(self.comments)}, "
            f"likes={len(self.likes)})"
        )

    def __eq__(self, other):
        # Two posts are equal if they have the same post_id.
        if not isinstance(other, Post):
            return False
        return self.post_id == other.post_id

    def __len__(self):
        # len(post) returns the total number of interactions (comments + likes).
        # This gives a quick sense of how active the post is.
        return len(self.comments) + len(self.likes)

    # -- Helper methods -------------------------------------------------------

    def add_comment(self, comment):
        """Attach a Comment object to this post."""
        self.comments.append(comment)

    def add_like(self, like):
        """Attach a Like object to this post."""
        self.likes.append(like)
