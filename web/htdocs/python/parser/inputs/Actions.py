import libcst

from .Action import Action

class Actions(libcst.CSTVisitor):
    def __init__(self, hold = False):
        self.hold = hold
        self.result = []

    # Elements of the main input dict
    def visit_DictElement(self, node):
        if (not self.hold and node.key.value == '"actions"') or (self.hold and node.key.value == '"actionsHold"'):
            self.actions_key = node.key.value
        else:
            return False

    def leave_DictElement(self, node):
        self.actions_key = None

    # Actions or similar list element
    def visit_Element(self, node):
        if not self.actions_key:
            return False
        
        if not isinstance(node.value, libcst.Call):
            return False

        self.result.append(Action(node.value))
        return False
    
        