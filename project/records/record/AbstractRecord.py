class AbstractRecord:

    def __init__ (self, TTL: int = None, class_: str = "IN", type_: str = None, comment= None ):
        self.TTL = TTL
        self.class_ = class_
        self.type_ = type_
        self._comment = comment

    def trim(self):
        self.class_ = self.class_.strip()
        self.type_ = self.type_.strip()

    def show(self):
        print(f"class : {self.class_}")
        print(f"TTL : {self.TTL}")
        print(f"comment : {self.comment}")
        print(f"type : {self.type_}")

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, comment):
        if isinstance(comment, Comment):
            self._comment = comment
        else:
            raise TypeError("The comment must be an instance of the class Comment.")
