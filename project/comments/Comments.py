from project.comments.Comment import Comment


class Comments:

    def __init__(self):
        self.comments = []

    def add_comment(self, comment: Comment):
        self.comments.append(comment)

    def remove_comment(self, comment: Comment):
        self.comments.remove(comment)

    def show_comments(self):
        for comment in self.comments:
            comment.show()
