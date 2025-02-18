from .VisitorsWithStack import VisitorWithStack

class CollectCommentsTransformer(VisitorWithStack):

    # If level is None, all levels are searched. 
    def __init__(self, level = None):
        super().__init__()

        self.comment = None
        self.level = level

    def on_visit(self, node):
        if self.level != None and len(self.stack) != self.level:
            return super().on_visit(node)

        def crawl(node):
            if hasattr(node, "comment") and node.comment:
                comment = node.comment.value.removeprefix('# ')

                if self.comment == None:
                    self.comment = comment
                else:
                    self.comment += "\n" + comment

        crawl(node)

        if hasattr(node, "leading_lines"):
            for line in node.leading_lines:
                crawl(line)

        return super().on_visit(node)