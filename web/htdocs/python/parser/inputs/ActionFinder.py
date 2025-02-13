from ..VisitorWithStack import VisitorWithStack

class ActionFinder(VisitorWithStack):
    def __init__(self, index, hold = False):
        super().__init__()

        self.index = index
        self.hold = hold
        
        self.current = 0
        self.result = None     
        
    # Elements of the main input dict
    def visit_DictElement(self, node):
        if self.result:
            return False
        
        if (not self.hold and node.key.value == '"actions"') or (self.hold and node.key.value == '"actionsHold"'):
            self.actions_key = node.key.value
            self.current = 0
        else:
            return False

    def leave_DictElement(self, node):
        self.actions_key = None        

    # Actions or similar list element
    def visit_Element(self, node):
        if self.result:
            return False
        
        if len(self.stack) != 4:
            return False
        
    def leave_Element(self, node):
        if self.result:
            return False
        
        if len(self.stack) != 3:
            return False

        if not self.actions_key:
            return False
        
        if self.actions_key == ('"actions"' if not self.hold else '"actionsHold"'):
            if self.current == self.index:
                self.current += 1
                self.result = node

        self.current += 1
        return False
    
        